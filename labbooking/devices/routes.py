from datetime import datetime
from flask import Blueprint, flash, redirect, render_template, request, url_for
from labbooking.time_rules import ZONE
from labbooking.auth.services import account_info
from labbooking.web import access, field
from . import services

devices = Blueprint("devices", __name__)


@devices.get("/devices")
@access("user", "admin")
def catalog(actor):
    return render_template("devices.html", rows=services.catalog(actor), account=account_info(actor),
                           role=actor.role, today=datetime.now(ZONE).date())


@devices.get("/admin/devices/new")
@access("admin")
def new(actor):
    return render_template("device_form.html", device=None, role=actor.role)


def fields():
    return {key: field(request.form, key) for key in request.form if key != "csrf_token"}


@devices.post("/admin/devices")
@access("admin")
def create(actor):
    services.save(actor, fields())
    return redirect(url_for("devices.catalog"), code=303)


@devices.route("/admin/devices/<int:device_id>/edit", methods=["GET", "POST"])
@access("admin")
def edit(actor, device_id):
    if request.method == "GET":
        return render_template("device_form.html", device=services.one(actor, device_id), role=actor.role)
    services.save(actor, fields(), device_id)
    return redirect(url_for("devices.catalog"), code=303)


@devices.post("/admin/devices/<int:device_id>/enable", defaults={"enabled": True})
@devices.post("/admin/devices/<int:device_id>/disable", defaults={"enabled": False})
@access("admin")
def toggle(actor, device_id, enabled):
    changed = services.set_enabled(actor, device_id, enabled)
    label = "启用" if enabled else "停用"
    flash(f"设备已{label}。" if changed else f"设备当前已{label}，无需更改。")
    return redirect(url_for("devices.catalog"), code=303)
