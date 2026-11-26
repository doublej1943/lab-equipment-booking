from sqlalchemy import func, insert, select, update
from labbooking.auth.models import User
from labbooking.devices.models import Device
from labbooking.errors import Conflict, Missing, Occupied, write_transaction
from labbooking.extensions import db
from labbooking.time_rules import SLOTS, database_now, snapshot
from .models import Booking


def device_row(device_id, *, lock=False):
    query = select(Device.id, Device.code, Device.name, Device.location, Device.status).where(Device.id == device_id)
    if lock:
        query = query.with_for_update(read=True)
    row = db.session.execute(query).mappings().first()
    if row is None:
        raise Missing("找不到设备。")
    return row


def availability(actor, device_id, day):
    actor.require("user", "admin")
    device = device_row(device_id)
    taken = set(db.session.scalars(select(Booking.slot).where(
        Booking.device_id == device_id, Booking.booking_date == day, Booking.status == "Confirmed")))
    now = database_now()
    slots = []
    for slot in SLOTS:
        start, end = snapshot(day, slot)
        if device.status == "Disabled":
            state = "设备已停用"
        elif now >= start:
            state = "时段已开始"
        elif slot in taken:
            state = "已占用"
        else:
            state = "可预约"
        slots.append(dict(slot=slot, start=start, end=end, state=state))
    return device, slots


def create(actor, device_id, day, slot):
    actor.require("user")
    start, end = snapshot(day, slot)
    with write_transaction("预约结果尚未确认，请先查看本人预约记录核实。", recovery="bookings.mine",
                           unique_name="uq_bookings_confirmed_slot",
                           conflict=Occupied(f"设备 #{device_id} 在 {day} 的 {slot} 时段已被预约。")):
        device = device_row(device_id, lock=True)
        if device.status == "Disabled":
            raise Conflict("设备已停用。")
        if database_now() >= start:
            raise Conflict("时段已开始，无法预约。")
        return db.session.scalar(insert(Booking).values(user_id=actor.id, device_id=device_id,
                                 booking_date=day, slot=slot, status="Confirmed",
                                 start_at=start, end_at=end).returning(Booking.id))


def cancel(actor, booking_id):
    actor.require("user")
    with write_transaction("取消结果尚未确认，请先查看该预约详情核实。", recovery="bookings.detail", booking_id=booking_id):
        row = db.session.execute(select(Booking.status, Booking.start_at).where(
            Booking.id == booking_id, Booking.user_id == actor.id).with_for_update()).first()
        if row is None:
            raise Missing("找不到预约。")
        if row.status == "Cancelled":
            raise Conflict("已取消，本次未执行。")
        if database_now() >= row.start_at:
            raise Conflict("时段已开始，无法取消。")
        db.session.execute(update(Booking).where(Booking.id == booking_id).values(status="Cancelled"))


def records():
    return select(Booking.id, Booking.booking_date, Booking.slot, Booking.status, Booking.start_at,
                  Booking.end_at, Device.code, Device.name, Device.location,
                  Device.status.label("device_status"),
                  (Booking.end_at <= func.statement_timestamp()).label("ended")).join(Device, Device.id == Booking.device_id)


def page_rows(query, page, size, *, ascending=False):
    offset = (page - 1) * size
    if offset > 2**63 - 1:
        return [], False
    order = (Booking.start_at, Booking.id) if ascending else (Booking.start_at.desc(), Booking.id.desc())
    rows = db.session.execute(query.order_by(*order).offset(offset).limit(size + 1)).mappings().all()
    return rows[:size], len(rows) > size


def own_list(actor, status, page, size):
    actor.require("user")
    query = records().where(Booking.user_id == actor.id)
    if status:
        query = query.where(Booking.status == status)
    return page_rows(query, page, size)


def own_detail(actor, booking_id):
    actor.require("user")
    row = db.session.execute(records().where(Booking.user_id == actor.id, Booking.id == booking_id)
                             ).mappings().first()
    if row is None:
        raise Missing("找不到预约。")
    return dict(row, can_cancel=row.status == "Confirmed" and database_now() < row.start_at)


def admin_records():
    return records().join(User, User.id == Booking.user_id).add_columns(User.username)


def all_bookings(actor, start, end, device_id, status, page, size):
    actor.require("admin")
    query = admin_records()
    if start:
        query = query.where(Booking.booking_date >= start)
    if end:
        query = query.where(Booking.booking_date <= end)
    if device_id:
        query = query.where(Booking.device_id == device_id)
    if status:
        query = query.where(Booking.status == status)
    return page_rows(query, page, size)


def affected(actor, device_id, page, size):
    actor.require("admin")
    device = device_row(device_id)
    query = admin_records().where(Device.id == device_id, Device.status == "Disabled",
                                  Booking.status == "Confirmed", Booking.start_at > func.statement_timestamp())
    rows, more = page_rows(query, page, size, ascending=True)
    return device, rows, more


def coordination(actor, booking_id):
    actor.require("admin")
    query = admin_records().add_columns(User.phone).where(Booking.id == booking_id)
    row = db.session.execute(query).mappings().first()
    if row is None:
        raise Missing("找不到预约。")
    return row
