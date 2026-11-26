"""Initial booking schema with stable history and confirmed-slot uniqueness."""
from alembic import op

revision = "0001"
down_revision = "0000"


def upgrade():
    op.execute("""
        CREATE TABLE bookings (
            id integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            user_id integer NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
            device_id integer NOT NULL REFERENCES devices(id) ON DELETE RESTRICT,
            booking_date date NOT NULL, slot varchar(2) NOT NULL, status varchar(16) NOT NULL,
            start_at timestamptz(6) NOT NULL, end_at timestamptz(6) NOT NULL,
            CONSTRAINT ck_bookings_slot CHECK (slot IN ('AM','PM')),
            CONSTRAINT ck_bookings_status CHECK (status IN ('Confirmed','Cancelled')),
            CONSTRAINT ck_bookings_times CHECK (start_at < end_at)
        )
    """)
    op.execute("CREATE UNIQUE INDEX uq_bookings_confirmed_slot ON bookings "
               "(device_id, booking_date, slot) WHERE status = 'Confirmed'")


def downgrade():
    raise RuntimeError("Restore a reviewed database backup to roll back the booking schema.")
