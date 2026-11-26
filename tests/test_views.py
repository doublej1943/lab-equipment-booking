import re
from datetime import date, timedelta
from flask import before_render_template, template_rendered
from sqlalchemy import event, text
from sqlalchemy.exc import OperationalError
from labbooking import create_app
from labbooking.bookings import services
from labbooking.extensions import db
from labbooking.time_rules import snapshot
from .support import future


def test_slot_cutoffs(system, monkeypatch):
    lab = system
    client, token = lab.client("reader")
    day = date.fromisoformat(future())
    device = lab.device()
    for slot in ("AM", "PM"):
        start, end = snapshot(day, slot)
        assert (start.hour, start.minute, end.hour, end.minute) == (
            (8,0,12,0) if slot == "AM" else (13,30,17,30))
        form = dict(device_id=device, booking_date=day.isoformat(), slot=slot, csrf_token=token)
        def move(instant):
            monkeypatch.setattr(services, "database_now", lambda: instant)
        move(start - timedelta(microseconds=1))
        created = client.post("/bookings", data=form)
        assert created.status_code == 303
        for instant in (start, start + timedelta(microseconds=1), end):
            move(instant)
            assert client.post(created.location+"/cancel", data={"csrf_token":token}).status_code == 409
            assert client.post("/bookings", data=form).status_code == 409
            assert "时段已开始" in client.get(f"/devices/{device}/availability?date={day}").text
        move(start - timedelta(microseconds=1))
        assert client.post(created.location+"/cancel", data={"csrf_token":token}).status_code == 303


def test_filters_pagination_and_history(system):
    lab = system
    user, token = lab.client("reader")
    admin, _ = lab.client("manager")
    device = lab.device("Disabled")
    other_device = lab.device()
    with lab.maintenance.begin() as conn:
        def seed(target, day, status, owner):
            start, end = snapshot(day, "AM")
            return conn.scalar(text("INSERT INTO bookings(user_id,device_id,booking_date,slot,status,start_at,end_at) "
                "VALUES ((SELECT id FROM users WHERE username=:owner),:target,:day,'AM',:status,:start,:end) RETURNING id"),
                dict(owner=owner,target=target,day=day,status=status,start=start,end=end))
        past = seed(device, date(2020,1,1), "Confirmed","reader")
        day = date.fromisoformat(future(65))
        cancelled = seed(device, day, "Cancelled","reader")
        first = seed(device, day, "Confirmed","reader")
        later = seed(device, day + timedelta(days=1), "Confirmed","other")
        seed(other_device, day, "Confirmed","reader")
    def ids(url):
        page = admin.get(url)
        assert page.status_code == 200 and lab.phones["reader"] not in page.text
        return [int(value) for value in re.findall(r'/admin/bookings/([0-9]+)/coordination', page.text)]
    assert ids(f"/admin/bookings?device_id={device}&date_from={day}&date_to={day}") == [first,cancelled]
    assert ids(f"/admin/devices/{device}/affected-bookings?page_size=1") == [first]
    assert ids(f"/admin/devices/{device}/affected-bookings?page=2&page_size=1") == [later]
    assert ids(f"/admin/devices/{device}/affected-bookings?page=3&page_size=1") == []
    assert ids(f"/admin/bookings?device_id={device}&status=Cancelled") == [cancelled]
    assert "时段已结束" in user.get(f"/bookings/{past}").text
    assert user.post(f"/bookings/{past}/cancel", data={"csrf_token":token}).status_code == 409
    assert user.get(f"/bookings/{later}").status_code == 404
    assert [r["status"] for r in lab.rows("SELECT status FROM bookings WHERE device_id=:id ORDER BY id", id=device)] == [
        "Confirmed","Cancelled","Confirmed","Confirmed"]


def test_catalog_privacy_rendering_and_failures(system, databases, monkeypatch, caplog):
    lab = system
    client, _ = lab.client("reader")
    with lab.app.app_context():
        engine = db.engine
    rendering = []
    statements = []
    def begin(sender, **kwargs):
        rendering.append(True)
    def end(sender, **kwargs):
        rendering.clear()
    def during(conn, cursor, statement, parameters, context, executemany):
        if rendering:
            statements.append(statement)
    event.listen(engine, "before_cursor_execute", during)
    try:
        with before_render_template.connected_to(begin, lab.app), template_rendered.connected_to(end, lab.app):
            assert client.get("/devices").status_code == 200
    finally:
        event.remove(engine, "before_cursor_execute", during)
    assert not statements
    from labbooking.devices import services as devices
    def failure(actor):
        raise OperationalError("sensitive query", {}, RuntimeError("private database detail"))
    monkeypatch.setattr(devices, "catalog", failure)
    response = client.get("/devices")
    assert response.status_code == 503 and "暂无设备" not in response.text
    for secret in (lab.phones["reader"], lab.passwords["reader"], "sensitive query", "private database detail"):
        assert secret not in response.text and secret not in caplog.text
    for mode in ("local-http", "https"):
        app = create_app({**databases, "LABBOOKING_TRANSPORT":mode})
        cookie = app.test_client().get("/login").headers["Set-Cookie"].split("; ")
        assert "HttpOnly" in cookie and "SameSite=Lax" in cookie and ("Secure" in cookie) == (mode=="https")
