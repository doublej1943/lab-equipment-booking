from datetime import datetime, time
from zoneinfo import ZoneInfo
from sqlalchemy import func, select
from .extensions import db

ZONE = ZoneInfo("Asia/Shanghai")
SLOTS = {"AM": (time(8), time(12)), "PM": (time(13, 30), time(17, 30))}


def snapshot(day, slot):
    start, end = SLOTS[slot]
    return datetime.combine(day, start, ZONE), datetime.combine(day, end, ZONE)


def database_now():
    return db.session.scalar(select(func.clock_timestamp()))
