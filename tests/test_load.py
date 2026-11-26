"""B's reproducible NFR-01/02 run on disposable PostgreSQL, through Waitress."""
import http.client
import json
import math
import os
import platform
import re
import time
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from datetime import date, timedelta
from http.cookies import SimpleCookie
from pathlib import Path
from secrets import token_urlsafe
from threading import Barrier, Thread
from urllib.parse import urlencode

from sqlalchemy import text
from waitress import create_server
from labbooking.auth.services import preset_rows
from labbooking.auth.models import User
from .support import future


class Browser:
    def __init__(self, port, name, password):
        self.port = port
        self.cookie = ""
        self.name = name
        status, page = self.request("GET", "/login")
        assert status == 200
        status, _ = self.request("POST", "/login", dict(username=name, password=password,
                                                       csrf_token=self.token_from(page)))
        assert status == 303
        status, page = self.request("GET", "/devices")
        assert status == 200
        self.token = self.token_from(page)

    @staticmethod
    def token_from(page):
        return re.search(r'name="csrf_token" value="([^"]+)"', page).group(1)

    def request(self, method, path, form=None):
        connection = http.client.HTTPConnection("127.0.0.1", self.port, timeout=30)
        headers = {"Cookie": self.cookie}
        if form is not None:
            headers["Content-Type"] = "application/x-www-form-urlencoded"
        try:
            connection.request(method, path, urlencode(form) if form is not None else None, headers)
            response = connection.getresponse()
            body = response.read().decode("utf-8")
            if response.getheader("Set-Cookie"):
                cookies = SimpleCookie(response.getheader("Set-Cookie"))
                if "session" in cookies:
                    self.cookie = "session=" + cookies["session"].value
            return response.status, body
        finally:
            connection.close()


@contextmanager
def serve(app):
    server = create_server(app, host="127.0.0.1", port=0, threads=24, asyncore_loop_timeout=1)
    worker = Thread(target=server.run, daemon=True)
    worker.start()
    try:
        yield int(server.effective_port)
    finally:
        server.task_dispatcher.shutdown()
        server.close()
        worker.join(5)


def seed(lab):
    password = token_urlsafe(32)
    accounts = [dict(username=f"load-{i:02}", password=password, phone=f"138{i:08}", role="user")
                for i in range(20)]
    with lab.maintenance.begin() as conn:
        conn.execute(User.__table__.insert(), preset_rows(accounts))
        conn.execute(text("""
            INSERT INTO devices(code,name,location,status)
            SELECT 'EQ-'||lpad(i::text,3,'0'), '仪器-'||i, '房间-'||i,
                   CASE WHEN i%5=0 THEN 'Disabled' ELSE 'Available' END
            FROM generate_series(1,100) AS i
        """))
        conn.execute(text("""
            INSERT INTO bookings(user_id,device_id,booking_date,slot,status,start_at,end_at)
            SELECT (SELECT id FROM users WHERE username='reader'), d.id, DATE '2020-01-01'+i,
                   'AM','Confirmed', (DATE '2020-01-01'+i+TIME '08:00') AT TIME ZONE 'Asia/Shanghai',
                   (DATE '2020-01-01'+i+TIME '12:00') AT TIME ZONE 'Asia/Shanghai'
            FROM devices d CROSS JOIN generate_series(1,10) AS i
        """))
    return accounts, password


def evidence(name, data):
    directory = os.environ.get("LABBOOKING_EVIDENCE_DIR")
    if directory:
        folder = Path(directory)
        folder.mkdir(parents=True, exist_ok=True)
        (folder / (name + ".json")).write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")


def measured(browser, method, path, form=None):
    start = time.perf_counter_ns()
    try:
        status, body = browser.request(method, path, form)
    except (OSError, http.client.HTTPException) as error:
        status, body = 0, type(error).__name__
    finish = time.perf_counter_ns()
    return dict(actor=browser.name, status=status, start_ns=start, end_ns=finish,
                ms=(finish-start)/1_000_000), body


def create_round(lab, workers, clients, observer, round_number, device, user):
    day = date.fromisoformat(future(40)) + timedelta(days=round_number)
    barrier = Barrier(20, timeout=15)
    def book(client):
        barrier.wait()
        result, body = measured(client, "POST", "/bookings", dict(csrf_token=client.token,
                                booking_date=day.isoformat(), slot="AM", device_id=device))
        result["occupied"] = result["status"] == 409 and "时段已被预约" in body and str(day) in body
        return result

    params = dict(day=day, device=device, user=user)
    with lab.maintenance.connect() as gate:
        free = gate.scalar(text("""
            SELECT status='Available' AND CAST(:day AS date)>CURRENT_DATE AND NOT EXISTS
            (SELECT 1 FROM bookings WHERE device_id=:device AND booking_date=:day AND slot='AM'
             AND status='Confirmed') FROM devices WHERE id=:device
        """), params)
        assert free
        gate.execute(text("""
            INSERT INTO bookings(user_id,device_id,booking_date,slot,status,start_at,end_at)
            VALUES (:user,:device,:day,'AM','Confirmed',
                    (CAST(:day AS date)+TIME '08:00') AT TIME ZONE 'Asia/Shanghai',
                    (CAST(:day AS date)+TIME '12:00') AT TIME ZONE 'Asia/Shanghai')
        """), params)
        futures = [workers.submit(book, client) for client in clients]
        peak = 0
        deadline = time.monotonic()+7
        while peak < 20 and time.monotonic() < deadline:
            count = observer.scalar(text("""
                SELECT count(*) FROM pg_stat_activity WHERE datname=current_database()
                AND usename=current_user AND state='active' AND wait_event_type='Lock'
                AND query ILIKE 'INSERT INTO bookings%' AND cardinality(pg_blocking_pids(pid))>0
            """))
            peak = max(peak, count)
            if peak < 20:
                time.sleep(0.01)
        gate.rollback()
    samples = [f.result(timeout=35) for f in futures]
    with lab.maintenance.begin() as conn:
        rows = conn.execute(text("SELECT id,status FROM bookings WHERE device_id=:device "
                                 "AND booking_date=:day AND slot='AM'"), params).all()
        conn.execute(text("DELETE FROM bookings WHERE device_id=:device AND booking_date=:day AND slot='AM'"), params)
        clean = conn.scalar(text("SELECT count(*) FROM bookings WHERE device_id=:device AND booking_date=:day"), params)
    return dict(round=round_number, sql_waiters=peak, samples=samples, final=[r.status for r in rows],
                after_cleanup=clean)


def test_load_profiles(system):
    from labbooking.extensions import db

    lab = system
    accounts, password = seed(lab)
    assert lab.rows("SELECT count(*) AS n FROM devices")[0]["n"] == 100
    assert lab.rows("SELECT count(*) AS n FROM bookings")[0]["n"] == 1000
    device = lab.rows("SELECT id FROM devices WHERE code='EQ-001'")[0]["id"]
    user = lab.rows("SELECT id FROM users WHERE username='reader'")[0]["id"]
    meta = dict(commit=os.getenv("GITHUB_SHA"), machine=platform.platform(), threads=24,
                pool_size=24, overflow=0, process_count=1, devices=100, history=1000,
                postgres=lab.rows("SHOW server_version")[0]["server_version"],
                max_connections=lab.rows("SHOW max_connections")[0]["max_connections"])
    rounds, readings = [], []
    with serve(lab.app) as port, ThreadPoolExecutor(max_workers=20) as workers:
        clients = [Browser(port, account["username"], password) for account in accounts]
        with lab.app.app_context(), db.engine.connect().execution_options(isolation_level="AUTOCOMMIT") as observer:
            try:
                for index in range(50):
                    rounds.append(create_round(lab, workers, clients, observer, index, device, user))
            finally:
                evidence("nfr-01", dict(environment=meta, rounds=rounds))
        # Login and one full preflight per client precede the measured reads.
        for client in clients:
            assert client.request("GET", "/devices")[0] == 200
        expected = [(f"EQ-{i:03}", f"仪器-{i}", f"房间-{i}", "Disabled" if i%5==0 else "Available")
                    for i in range(1,101)]
        sync = Barrier(20, timeout=30)
        def reads(index):
            client = clients[index]
            sync.wait()
            samples = []
            for sequence in range(50):
                result, body = measured(client, "GET", "/devices")
                rows = re.findall(r"<tr><td><strong>(.*?)</strong><small>(.*?)</small></td><td>(.*?)</td>"
                                  r'<td><span class="state (Available|Disabled)">', body)
                phones = re.findall(r"(?<![0-9])1[3-9][0-9]{9}(?![0-9])", body)
                result.update(sequence=sequence, correct=(
                    result["status"] == 200 and [(c,n,l,s) for n,c,l,s in rows] == expected
                    and phones == [accounts[index]["phone"]] and client.name in body))
                samples.append(result)
            return samples
        for group in workers.map(reads, range(20)):
            readings.extend(group)
    p95 = sorted(row["ms"] for row in readings)[math.ceil(0.95*len(readings))-1]
    evidence("nfr-02", dict(environment=meta, samples=readings, p95_ms=p95))
    print(f"NFR-02: {len(readings)} requests, P95 {p95:.2f} ms")
    assert len(rounds) == 50
    for item in rounds:
        assert item["sql_waiters"] == 20 and item["final"] == ["Confirmed"] and item["after_cleanup"] == 0
        assert sum(r["status"] == 303 for r in item["samples"]) == 1
        assert sum(r["occupied"] for r in item["samples"]) == 19
    assert lab.rows("SELECT count(*) AS n FROM bookings")[0]["n"] == 1000
    assert len(readings) == 1000 and all(row["correct"] for row in readings)
    assert p95 <= 1000
