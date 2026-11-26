from sqlalchemy import CheckConstraint, Identity, Index, text
from sqlalchemy.dialects.postgresql import TIMESTAMP
from labbooking.extensions import db


class Booking(db.Model):
    __tablename__ = "bookings"
    id = db.Column(db.Integer, Identity(always=True), primary_key=True)
    user_id = db.Column(db.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    device_id = db.Column(db.ForeignKey("devices.id", ondelete="RESTRICT"), nullable=False)
    booking_date = db.Column(db.Date, nullable=False)
    slot = db.Column(db.String(2), nullable=False)
    status = db.Column(db.String(16), nullable=False)
    start_at = db.Column(TIMESTAMP(timezone=True, precision=6), nullable=False)
    end_at = db.Column(TIMESTAMP(timezone=True, precision=6), nullable=False)
    user = db.relationship("User", back_populates="bookings")
    device = db.relationship("Device", back_populates="bookings")
    __table_args__ = (
        CheckConstraint("slot IN ('AM','PM')", name="ck_bookings_slot"),
        CheckConstraint("status IN ('Confirmed','Cancelled')", name="ck_bookings_status"),
        CheckConstraint("start_at < end_at", name="ck_bookings_times"),
        Index("uq_bookings_confirmed_slot", "device_id", "booking_date", "slot", unique=True,
              postgresql_where=text("status = 'Confirmed'")),
    )
