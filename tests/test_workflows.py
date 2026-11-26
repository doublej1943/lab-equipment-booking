import json
from datetime import datetime, timedelta
from time import time

import pytest
from sqlalchemy import event, text
from labbooking import create_app
from labbooking.auth import routes as auth_routes
from labbooking.extensions import db
from labbooking.time_rules import ZONE
from .support import csrf, future


def test_core_booking_cycle(system):
    lab = system
    owner, token = lab.client("reader")
    other, second = lab.client("other")
    admin, admin_token = lab.client("manager")
    device = lab.device()
    day = future()
    url = f"/devices/{device}/availability"
    assert owner.get(url).status_code == 400
    assert owner.get(url + "?date=2027-02-30").status_code == 400
    assert "可预约" in owner.get(url, query_string={"date": day}).text
    form = dict(device_id=device, booking_date=day, slot="AM", csrf_token=token)
    original = owner.post("/bookings", data={**form, "role": "admin", "user_id": "999999"})
    assert original.status_code == 303
    detail = original.location
    ident = int(detail.split("/")[-1])
    assert owner.get(detail).status_code == 200
    assert other.get(detail).status_code == 404
    assert other.post(detail + "/cancel", data={"csrf_token": second}).status_code == 404
    assert admin.post(detail + "/cancel", data={"csrf_token": admin_token}).status_code == 403
    before = lab.rows("SELECT * FROM bookings WHERE id=:id", id=ident)[0]
    assert before["start_at"].astimezone(ZONE).strftime("%H:%M") == "08:00"
    assert before["end_at"].astimezone(ZONE).strftime("%H:%M") == "12:00"
    conflict = other.post("/bookings", data={**form, "csrf_token": second})
    assert conflict.status_code == 409 and "已被预约" in conflict.text and day in conflict.text
    assert lab.phones["reader"] not in conflict.text
    assert other.post("/bookings", data={**form, "csrf_token": second, "slot": "PM"}).status_code == 303
    assert owner.post("/bookings", data={**form, "device_id": lab.device()}).status_code == 303
    assert "已占用" in owner.get(url, query_string={"date": day}).text
    assert owner.post(detail + "/cancel", data={"csrf_token": token}).status_code == 303
    assert owner.post(detail + "/cancel", data={"csrf_token": token}).status_code == 409
    after = lab.rows("SELECT * FROM bookings WHERE id=:id", id=ident)[0]
    assert dict(before, status="Cancelled") == dict(after)
    assert owner.post("/bookings", data=form).status_code == 303
    assert "已取消" in owner.get("/bookings").text
    assert "已取消" not in owner.get("/bookings?status=Confirmed").text
    for params in ("page=0", "page=1&page=2", "page_size=101", "page=", "status=Cancelled"):
        assert owner.get("/bookings?" + params).status_code == 400
    for page in ("101", "9"*100):
        assert "暂无符合条件" in owner.get("/bookings?page=" + page).text


def test_admin_maintenance_and_privacy(system):
    lab = system
    admin, token = lab.client("manager")
    user, personal = lab.client("reader")
    origin = dict(code="Case01", name="显微镜", location="A区", status="Available", csrf_token=token)
    assert admin.get("/admin/devices/new").status_code == 200
    assert admin.post("/admin/devices", data={**origin, "code":" Case01"}).status_code == 400
    assert admin.post("/admin/devices", data=origin).status_code == 303
    assert admin.post("/admin/devices", data=origin).status_code == 409
    assert admin.post("/admin/devices", data={**origin,"code":"case01"}).status_code == 303
    device = lab.rows("SELECT id FROM devices WHERE code='Case01'")[0]["id"]
    path = f"/admin/devices/{device}"
    assert admin.get(path + "/edit").status_code == 200
    for extra in (dict(code="replaced"), dict(status="Disabled")):
        assert admin.post(path + "/edit", data=dict(name="bad", location="bad", csrf_token=token, **extra)).status_code == 400
    data = dict(booking_date=future(), slot="PM", device_id=device, csrf_token=personal)
    detail = user.post("/bookings", data=data).location
    assert admin.post(path + "/edit", data=dict(name="新显微镜", location="B区", csrf_token=token)).status_code == 303
    assert admin.post(path + "/disable", data={"csrf_token":token}).status_code == 303
    assert "无需更改" in admin.post(path + "/disable", data={"csrf_token":token}, follow_redirects=True).text
    assert user.post("/bookings", data={**data,"slot":"AM"}).status_code == 409
    assert "新显微镜" in user.get(detail).text and "设备已停用" in user.get(detail).text
    affected = admin.get(path + "/affected-bookings")
    assert "新显微镜" in affected.text and lab.phones["reader"] not in affected.text
    listing = admin.get("/admin/bookings", query_string=dict(date_from=future(), date_to=future(),
                                                            device_id=device,status="Confirmed"))
    assert "新显微镜" in listing.text and lab.phones["reader"] not in listing.text
    assert admin.get("/admin/bookings?date_from=2027-01-02&date_to=2027-01-01").status_code == 400
    coord = "/admin" + detail + "/coordination"
    assert lab.phones["reader"] in admin.get(coord + "?user_id=999").text
    assert lab.phones["other"] not in admin.get(coord).text
    assert admin.post(path + "/enable", data={"csrf_token":token}).status_code == 303
    assert "暂无符合条件" in admin.get(path + "/affected-bookings").text
    assert user.post("/bookings", data={**data,"slot":"AM"}).status_code == 303


def test_authorization_and_csrf_matrix(system):
    lab = system
    anon, anonymous_token = lab.client()
    user, user_token = lab.client("reader")
    admin, admin_token = lab.client("manager")
    device = lab.device()
    admin_path = f"/admin/devices/{device}"
    own = user.post("/bookings", data=dict(device_id=device, booking_date=future(),slot="AM",
                                            csrf_token=user_token)).location
    admin_gets = ["/admin/devices/new",admin_path+"/edit","/admin/bookings",
                  admin_path+"/affected-bookings","/admin"+own+"/coordination"]
    user_gets = ["/bookings",own]
    shared = ["/devices", f"/devices/{device}/availability?date={future()}"]
    for path in admin_gets + user_gets + shared:
        assert anon.get(path).status_code == 302
        if path in admin_gets:
            assert user.get(path).status_code == 403
            assert admin.get(path).status_code == 200
        elif path in user_gets:
            assert admin.get(path).status_code == 403
            assert user.get(path).status_code == 200
        else:
            assert user.get(path).status_code == admin.get(path).status_code == 200
    admin_posts = ["/admin/devices",admin_path+"/edit",admin_path+"/enable",admin_path+"/disable"]
    user_posts = ["/bookings",own+"/cancel"]
    def snapshot():
        return [lab.rows(f"SELECT * FROM {table} ORDER BY id") for table in ("devices","bookings")]
    initial = snapshot()
    for path in user_posts + admin_posts + ["/login","/logout"]:
        for data in ({},{"csrf_token":"invalid"}):
            assert user.post(path, data=data).status_code == 400
        if path != "/login":
            assert anon.post(path, data={"csrf_token":anonymous_token}).status_code == 401
        if path in admin_posts:
            assert user.post(path, data={"csrf_token":user_token,"role":"admin"}).status_code == 403
        if path in user_posts:
            assert admin.post(path, data={"csrf_token":admin_token}).status_code == 403
    assert snapshot() == initial
    assert user.post("/logout", data={"csrf_token":user_token}).status_code == 303
    assert user.get("/devices").status_code == 302


def test_session_and_account_boundaries(system, monkeypatch):
    lab = system
    client, token = lab.client()
    bad = client.post("/login", data=dict(username="reader",password="wrong",csrf_token=token))
    assert bad.status_code == 401
    client, _ = lab.client("reader")
    response = client.get("/devices")
    assert lab.phones["reader"] in response.text and lab.phones["other"] not in response.text
    assert "no-store" in response.headers["Cache-Control"]
    with client.session_transaction() as session:
        deadline = session["expires_at"]
        assert lab.phones["reader"] not in repr(dict(session)) and "role" not in session
    real_time = auth_routes.time
    class Clock:
        @staticmethod
        def time():
            return deadline - 0.1
    monkeypatch.setattr(auth_routes, "time", Clock)
    assert client.get("/devices").status_code == 200
    monkeypatch.setattr(Clock, "time", lambda: deadline)
    assert client.get("/devices").status_code == 302
    monkeypatch.setattr(auth_routes, "time", real_time)
    client.set_cookie("session", "invalid-signature")
    assert client.get("/devices").status_code == 302
