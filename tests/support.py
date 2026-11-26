import re
from dataclasses import dataclass
from datetime import timedelta, datetime
from secrets import token_urlsafe
from uuid import uuid4

from sqlalchemy import text
from labbooking.time_rules import ZONE


def future(days=7):
    return (datetime.now(ZONE).date() + timedelta(days=days)).isoformat()


def csrf(response):
    match = re.search(rb'name="csrf_token" value="([^"]+)"', response.data)
    assert match, (response.status_code, "expected CSRF form")
    return match[1].decode()


@dataclass
class Lab:
    app: object
    maintenance: object
    passwords: dict
    phones: dict

    def client(self, username=None):
        client = self.app.test_client()
        token = csrf(client.get("/login"))
        if username:
            response = client.post("/login", data=dict(username=username, password=self.passwords[username],
                                                       csrf_token=token))
            assert response.status_code == 303
            token = csrf(client.get("/devices"))
        return client, token

    def device(self, status="Available"):
        with self.maintenance.begin() as conn:
            return conn.scalar(text("INSERT INTO devices(code,name,location,status) VALUES"
                                    "(:code,'试验设备','实验室',:status) RETURNING id"),
                               dict(code="D-" + uuid4().hex, status=status))

    def rows(self, sql, **params):
        with self.maintenance.connect() as conn:
            return conn.execute(text(sql), params).mappings().all()


def accounts():
    passwords = {name: token_urlsafe(24) for name in ("reader", "other", "manager")}
    phones = {name: "139" + str(index).zfill(8) for index, name in enumerate(passwords, 1)}
    records = [dict(username=name, phone=phones[name], password=password,
                    role="admin" if name == "manager" else "user") for name, password in passwords.items()]
    return passwords, phones, records
