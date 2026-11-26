from flask import Blueprint, redirect, render_template, request, url_for
from labbooking.errors import Invalid
from labbooking.time_rules import SLOTS
from labbooking.web import access, day_value, field, pagination, positive
from . import services

bookings = Blueprint("bookings", __name__)


@bookings.get("/devices/<int:device_id>/availability")
@access("user", "admin")
def availability(actor, device_id):
    day = day_value(field(request.args, "date"))
    device, slots = services.availability(actor, device_id, day)
    return render_template("availability.html", device=device, slots=slots, day=day, role=actor.role)


@bookings.post("/bookings")
@access("user")
def create(actor):
    slot = field(request.form, "slot")
    if slot not in SLOTS:
        raise Invalid("请选择 AM 或 PM。")
    booking_id = services.create(actor, positive(field(request.form, "device_id")),
                                 day_value(field(request.form, "booking_date")), slot)
    return redirect(url_for("bookings.detail", booking_id=booking_id), code=303)


def status_filter():
    status = field(request.args, "status")
    if status not in {None, "Confirmed", "Cancelled"}:
        raise Invalid("预约状态无效。")
    return status


def list_page(actor, title, rows, more, page, **extra):
    args = request.args.to_dict()
    def link(number):
        return url_for(request.endpoint, **request.view_args, **{**args, "page": number})
    return render_template("bookings.html", role=actor.role, title=title, rows=rows,
                           previous=link(page - 1) if page > 1 else None,
                           following=link(page + 1) if more else None, filters=args, **extra)


@bookings.get("/bookings")
@access("user")
def mine(actor):
    page, size = pagination(request.args)
    status = status_filter()
    if status == "Cancelled":
        raise Invalid("本人列表支持完整历史或 Confirmed 筛选。")
    rows, more = services.own_list(actor, status, page, size)
    return list_page(actor, "我的预约", rows, more, page)


@bookings.get("/bookings/<int:booking_id>")
@access("user")
def detail(actor, booking_id):
    return render_template("detail.html", item=services.own_detail(actor, booking_id), role=actor.role)


@bookings.post("/bookings/<int:booking_id>/cancel")
@access("user")
def cancel(actor, booking_id):
    services.cancel(actor, booking_id)
    return redirect(url_for("bookings.detail", booking_id=booking_id), code=303)


@bookings.get("/admin/bookings")
@access("admin")
def all_bookings(actor):
    page, size = pagination(request.args)
    start = field(request.args, "date_from")
    end = field(request.args, "date_to")
    start = day_value(start) if start else None
    end = day_value(end) if end else None
    if start and end and start > end:
        raise Invalid("开始日期不能晚于结束日期。")
    device = field(request.args, "device_id")
    rows, more = services.all_bookings(actor, start, end, positive(device) if device else None,
                                       status_filter(), page, size)
    return list_page(actor, "全部预约", rows, more, page, admin_filters=True)


@bookings.get("/admin/devices/<int:device_id>/affected-bookings")
@access("admin")
def affected(actor, device_id):
    page, size = pagination(request.args)
    device, rows, more = services.affected(actor, device_id, page, size)
    return list_page(actor, "受影响预约", rows, more, page, device=device)


@bookings.get("/admin/bookings/<int:booking_id>/coordination")
@access("admin")
def coordination(actor, booking_id):
    return render_template("detail.html", item=services.coordination(actor, booking_id), role=actor.role)
