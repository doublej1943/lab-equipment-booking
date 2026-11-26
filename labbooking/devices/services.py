from sqlalchemy import insert, select, update
from labbooking.errors import Conflict, Invalid, Missing, write_transaction
from labbooking.extensions import db
from .models import Device

COLUMNS = (Device.id, Device.code, Device.name, Device.location, Device.status)


def catalog(actor):
    actor.require("user", "admin")
    return db.session.execute(select(*COLUMNS).order_by(Device.code, Device.id)).mappings().all()


def one(actor, device_id):
    actor.require("admin")
    row = db.session.execute(select(*COLUMNS).where(Device.id == device_id)).mappings().first()
    if row is None:
        raise Missing("找不到设备。")
    return row


def save(actor, data, device_id=None):
    actor.require("admin")
    create = device_id is None
    keys = {"code", "name", "location", "status"} if create else {"name", "location"}
    if set(data) != keys or any(not data[k] or not data[k].strip() for k in keys):
        raise Invalid("请填写设备表单中的全部字段。")
    if any(len(data[k]) > 128 for k in ("name", "location")):
        raise Invalid("设备名称和位置最多各 128 个字符。")
    if create and (len(data["code"]) > 64 or data["code"] != data["code"].strip()
                   or data["status"] not in {"Available", "Disabled"}):
        raise Invalid("设备编号或状态无效。")
    with write_transaction("保存结果尚未确认，请查看设备列表核实。",
                           unique_name="uq_devices_code", make_conflict=lambda: Conflict("设备编号已存在。")):
        if create:
            db.session.execute(insert(Device).values(**data))
        else:
            changed = db.session.scalar(update(Device).where(Device.id == device_id)
                                        .values(**data).returning(Device.id))
            if changed is None:
                raise Missing("找不到设备。")


def set_enabled(actor, device_id, enabled):
    actor.require("admin")
    target, source = ("Available", "Disabled") if enabled else ("Disabled", "Available")
    with write_transaction("设备状态尚未确认，请查看设备列表核实。"):
        changed = db.session.scalar(update(Device).where(Device.id == device_id, Device.status == source)
                                    .values(status=target).returning(Device.id))
        if changed is not None:
            return True
        actual = db.session.scalar(select(Device.status).where(Device.id == device_id))
        if actual is None:
            raise Missing("找不到设备。")
        if actual != target:
            raise Conflict("设备状态再次变化，请刷新后核实。")
        return False
