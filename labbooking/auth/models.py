from sqlalchemy import CheckConstraint, Identity, UniqueConstraint
from labbooking.extensions import db


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, Identity(always=True), primary_key=True)
    username = db.Column(db.String(64), nullable=False)
    password_hash = db.Column(db.Text, nullable=False)
    role = db.Column(db.String(16), nullable=False)
    phone = db.Column(db.String(11), nullable=False)
    bookings = db.relationship("Booking", back_populates="user", passive_deletes="all")
    __table_args__ = (
        UniqueConstraint("username", name="uq_users_username"),
        CheckConstraint("username <> '' AND username = lower(username) AND username !~ '^[[:space:]]|[[:space:]]$'", name="ck_users_username"),
        CheckConstraint("password_hash ~ '[^[:space:]]'", name="ck_users_hash"),
        CheckConstraint("role IN ('user','admin')", name="ck_users_role"),
        CheckConstraint("phone ~ '^1[3-9][0-9]{9}$'", name="ck_users_phone"),
    )
