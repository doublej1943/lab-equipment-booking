import time
from concurrent.futures import ThreadPoolExecutor
from datetime import date, timedelta
from threading import Event

import pytest
from sqlalchemy import text
from labbooking.bookings import services
from labbooking.extensions import db
from labbooking.time_rules import snapshot
from .support import future
from .test_load import evidence


def uri(client, token, device, day=None):
    return client.post("/bookings", data=dict(device_id=device, booking_date=day or future(),
                                              slot="AM", csrf_token=token))


def state(lab, device):
    return lab.rows("SELECT * FROM bookings WHERE device_id=:id ORDER BY id", id=device)


def wait_for_lock(lab, query):
    with lab.app.app_context(), db.engine.connect().execution_options(isolation_level="AUTOCOMMIT") as conn:
        deadline = time.monotonic() + 5
        while time.monotonic() < deadline:
            waiters = conn.scalar(text("SELECT count(*) FROM pg_stat_activity WHERE pid<>pg_backend_pid() "
                "AND usename=current_user AND query ILIKE :query AND wait_event_type='Lock' "
                "AND cardinality(pg_blocking_pids(pid))>0"), {"query": "%" + query + "%"})
            if waiters:
                return
            time.sleep(0.01)
        pytest.fail("Expected PostgreSQL lock wait was not observed")


def wait_until_database_time(lab, target):
    deadline = time.monotonic() + 8
    while time.monotonic() < deadline:
        if lab.rows("SELECT clock_timestamp() >= :target AS ready", target=target)[0]["ready"]:
            return
        time.sleep(0.02)
    pytest.fail("Database did not reach the target time")


@pytest.mark.parametrize("operation", ["create", "cancel"])
@pytest.mark.parametrize("cross_before_check", [True, False])
def test_lock_then_fresh_clock(system, monkeypatch, operation, cross_before_check):
    lab = system
    client, token = lab.client("reader")
    device = lab.device()
    url = uri(client, token, device).location if operation == "cancel" else None
    now = lab.rows("SELECT clock_timestamp() AS now")[0]["now"]
    boundary = now + timedelta(seconds=2)
    if operation == "create":
        monkeypatch.setattr(services, "snapshot", lambda day, slot: (boundary, boundary + timedelta(hours=4)))
    else:
        with lab.maintenance.begin() as conn:
            conn.execute(text("UPDATE bookings SET start_at=:start WHERE device_id=:device"),
                         dict(start=boundary, device=device))
    checked, resume = Event(), Event()
    readings = []
    original_clock = services.database_now
    def timed_check():
        value = original_clock()
        readings.append(value)
        checked.set()
        assert resume.wait(timeout=8)
        return value
    monkeypatch.setattr(services, "database_now", timed_check)
    with ThreadPoolExecutor(1) as workers, lab.maintenance.connect() as gate:
        if cross_before_check:
            if operation == "create":
                gate.execute(text("SELECT id FROM devices WHERE id=:device FOR UPDATE"), {"device": device})
            else:
                gate.execute(text("SELECT id FROM bookings WHERE device_id=:device FOR UPDATE"), {"device": device})
        if operation == "create":
            job = workers.submit(uri, client, token, device)
        else:
            job = workers.submit(client.post, url + "/cancel", data={"csrf_token":token})
        try:
            if cross_before_check:
                wait_for_lock(lab, "FOR SHARE" if operation == "create" else "FOR UPDATE")
                assert not checked.is_set()
            else:
                assert checked.wait(timeout=5) and readings[0] < boundary
            wait_until_database_time(lab, boundary)
        finally:
            gate.rollback()
            resume.set()
        response = job.result(timeout=10)
    assert response.status_code == (409 if cross_before_check else 303)
    assert (readings[0] >= boundary) == cross_before_check
    statuses = [r["status"] for r in state(lab, device)]
    if operation == "create":
        assert statuses == ([] if cross_before_check else ["Confirmed"])
    else:
        assert statuses == (["Confirmed"] if cross_before_check else ["Cancelled"])
    evidence(f"clock-{operation}-{cross_before_check}", dict(
        device=device, lock_wait=cross_before_check, start_at=boundary.isoformat(),
        check_time=readings[0].isoformat(), http=response.status_code, statuses=statuses))


@pytest.mark.parametrize("commit", [True, False])
def test_disable_wins_or_rolls_back(system, commit):
    lab = system
    device = lab.device()
    client, token = lab.client("reader")
    with ThreadPoolExecutor(1) as workers, lab.maintenance.connect() as gate:
        gate.execute(text("UPDATE devices SET status='Disabled' WHERE id=:id"), {"id":device})
        job = workers.submit(uri, client, token, device)
        wait_for_lock(lab, "FOR SHARE")
        gate.commit() if commit else gate.rollback()
        assert job.result(timeout=10).status_code == (409 if commit else 303)
    assert len(state(lab, device)) == (0 if commit else 1)


@pytest.mark.parametrize("commit", [True, False])
@pytest.mark.parametrize("second", ["cancel", "create"])
def test_pending_cancellation(system, commit, second):
    lab = system
    device = lab.device()
    client, token = lab.client("reader")
    url = uri(client, token, device).location
    with ThreadPoolExecutor(1) as workers, lab.maintenance.connect() as gate:
        gate.execute(text("UPDATE bookings SET status='Cancelled' WHERE device_id=:id"), {"id":device})
        if second == "cancel":
            job = workers.submit(client.post, url + "/cancel", data={"csrf_token":token})
            wait_for_lock(lab, "FOR UPDATE")
        else:
            job = workers.submit(uri, client, token, device)
            wait_for_lock(lab, "INSERT INTO bookings")
        gate.commit() if commit else gate.rollback()
        succeeds = commit if second == "create" else not commit
        assert job.result(timeout=10).status_code == (303 if succeeds else 409)
    statuses = [r["status"] for r in state(lab, device)]
    if second == "cancel":
        assert statuses == ["Cancelled"]
    else:
        assert statuses == (["Cancelled","Confirmed"] if commit else ["Confirmed"])


@pytest.mark.parametrize("commit", [True, False])
def test_shared_device_lock_and_pending_disable(system, monkeypatch, commit):
    lab = system
    device = lab.device()
    first, token = lab.client("reader")
    other, second_token = lab.client("other")
    admin, admin_token = lab.client("manager")
    held, release = Event(), Event()
    real_clock = services.database_now
    def clock():
        value = real_clock()
        if not held.is_set():
            held.set()
            assert release.wait(8)
            if not commit:
                from labbooking.errors import Conflict
                raise Conflict("测试事务回滚。")
        return value
    monkeypatch.setattr(services, "database_now", clock)
    with ThreadPoolExecutor(2) as pool:
        first_job = pool.submit(uri, first, token, device)
        try:
            assert held.wait(5)
            assert uri(other, second_token, device, future(9)).status_code == 303
            disable = pool.submit(admin.post, f"/admin/devices/{device}/disable", data={"csrf_token": admin_token})
            wait_for_lock(lab, "UPDATE devices")
        finally:
            release.set()
        assert first_job.result().status_code == (303 if commit else 409)
        assert disable.result().status_code == 303
    assert len(state(lab, device)) == (2 if commit else 1)


@pytest.mark.parametrize("operation", ["create", "cancel"])
@pytest.mark.parametrize("mode", ["rollback", "wire", "simulated"])
def test_commit_outcomes(system, monkeypatch, operation, mode):
    import psycopg

    lab = system
    client, token = lab.client("reader")
    device = lab.device()
    url = uri(client, token, device).location if operation == "cancel" else None
    before = state(lab, device)
    with lab.app.app_context():
        dialect = db.engine.dialect
    real_commit = dialect.do_commit
    observed = []
    def inject(connection):
        physical = connection.driver_connection
        if mode == "rollback":
            # A server-reported SQL error inside the transaction, before COMMIT.
            physical.execute("SELECT 1/0")
        elif mode == "simulated":
            real_commit(connection)
            raise psycopg.OperationalError("synthetic confirmation loss")
        else:
            # Send the real protocol request. Never read its result from libpq.
            physical.pgconn.send_query(b"COMMIT")
            deadline = time.monotonic() + 5
            while physical.pgconn.flush() == 1:
                assert time.monotonic() < deadline
                time.sleep(0.001)
            expected = "Confirmed" if operation == "create" else "Cancelled"
            while time.monotonic() < deadline:
                if [r["status"] for r in state(lab, device)] == [expected]:
                    observed.append(expected)
                    break
                time.sleep(0.005)
            assert observed == [expected]
            physical.close()
            real_commit(connection)
    with monkeypatch.context() as patch:
        patch.setattr(dialect, "do_commit", inject)
        response = (uri(client, token, device) if operation == "create"
                    else client.post(url+"/cancel", data={"csrf_token":token}))
    after = state(lab, device)
    if mode == "rollback":
        assert response.status_code == 500 and after == before
    else:
        assert response.status_code == 503 and "尚未确认" in response.text
        recovery = "/bookings" if operation == "create" else url
        assert f'href="{recovery}"' in response.text
        assert len(after) == 1
        page = client.get(recovery)
        assert page.status_code == 200
        if operation == "create":
            assert after[0]["status"] == "Confirmed" and "已确认" in page.text
        else:
            assert dict(before[0], status="Cancelled") == dict(after[0]) and "已取消" in page.text
            assert uri(client, token, device).status_code == 303
    evidence(f"commit-{mode}-{operation}", dict(operation=operation, mechanism=mode,
             original_http=response.status_code, independent_commit_observation=observed,
             final_status=[r["status"] for r in after]))
