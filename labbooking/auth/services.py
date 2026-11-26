import re
from sqlalchemy import select
from labbooking.actor import Actor
from labbooking.errors import Invalid
from labbooking.extensions import db
from .models import User
from .passwords import hash_password, verify_password


def normalize(username):
    return username.strip().lower()


def authenticate(username, password):
    row = db.session.execute(select(User.id, User.role, User.password_hash)
                             .where(User.username == normalize(username))).one_or_none()
    if row and verify_password(row.password_hash, password):
        return Actor(row.id, row.role)
    return None


def load_actor(user_id):
    if not user_id.isascii() or not user_id.isdigit() or len(user_id) > 10:
        return None
    row = db.session.execute(select(User.id, User.role).where(User.id == int(user_id))).one_or_none()
    return Actor(*row) if row else None


def account_info(actor):
    return db.session.execute(select(User.username, User.phone)
                              .where(User.id == actor.id)).mappings().one()


def preset_rows(records):
    if not isinstance(records, list) or not records:
        raise Invalid("请选择非空的账号列表。")
    rows = []
    names = set()
    for record in records:
        keys = {"username", "password", "role", "phone"}
        if (not isinstance(record, dict) or set(record) != keys
                or any(not isinstance(record[k], str) or not record[k].strip()
                       or "\x00" in record[k] for k in keys)):
            raise Invalid("账号字段缺失或无效。")
        name = normalize(record["username"])
        if (len(name) > 64 or name in names or record["role"] not in {"admin", "user"}
                or not re.fullmatch(r"1[3-9][0-9]{9}", record["phone"])):
            raise Invalid("账号名称重复或账号资料格式不正确。")
        names.add(name)
        rows.append(dict(username=name, password_hash=hash_password(record["password"]),
                         role=record["role"], phone=record["phone"]))
    return rows
