from sqlalchemy import CheckConstraint, Identity, UniqueConstraint
from labbooking.extensions import db


class Device(db.Model):
    __tablename__ = "devices"
    id = db.Column(db.Integer, Identity(always=True), primary_key=True)
    code = db.Column(db.String(64, collation="C"), nullable=False)
    name = db.Column(db.String(128), nullable=False)
    location = db.Column(db.String(128), nullable=False)
    status = db.Column(db.String(16), nullable=False)
    bookings = db.relationship("Booking", back_populates="device", passive_deletes="all")
    __table_args__ = (
        UniqueConstraint("code", name="uq_devices_code"),
        CheckConstraint("code <> '' AND code !~ '^[[:space:]]|[[:space:]]$'", name="ck_devices_code"),
        CheckConstraint("name ~ '[^[:space:]]' AND location ~ '[^[:space:]]'", name="ck_devices_text"),
        CheckConstraint("status IN ('Available','Disabled')", name="ck_devices_status"),
    )
