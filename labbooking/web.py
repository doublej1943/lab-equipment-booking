import re
from datetime import date
from functools import wraps
from flask import abort, redirect, request, url_for
from flask_login import current_user
from .errors import Invalid


def access(*roles):
    def decorate(view):
        @wraps(view)
        def protected(*args, **kwargs):
            if not current_user.is_authenticated:
                if request.method in {"GET", "HEAD"}:
                    return redirect(url_for("auth.login"))
                abort(401)
            actor = current_user._get_current_object()
            actor.require(*roles)
            return view(actor, *args, **kwargs)
        return protected
    return decorate


def field(values, key, default=None):
    items = values.getlist(key)
    if not items:
        return default
    if len(items) != 1 or not items[0] or "\x00" in items[0]:
        raise Invalid("参数为空、重复或格式不正确。")
    return items[0]


def positive(value):
    if value is None or not re.fullmatch(r"[0-9]+", value):
        raise Invalid("请输入正整数。")
    digits = value.lstrip("0")
    if not digits:
        raise Invalid("请输入正整数。")
    return int(digits) if len(digits) <= 19 else 10**19


def day_value(value):
    if not value or not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", value):
        raise Invalid("日期格式应为 YYYY-MM-DD。")
    try:
        return date.fromisoformat(value)
    except ValueError:
        raise Invalid("日期无效。") from None


def pagination(values):
    page = positive(field(values, "page", "1"))
    size = positive(field(values, "page_size", "20"))
    if size > 100:
        raise Invalid("每页最多显示 100 条记录。")
    return page, size
