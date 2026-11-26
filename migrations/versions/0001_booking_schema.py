"""Initial booking schema with stable history and confirmed-slot uniqueness."""
from alembic import op

revision = "0001"
down_revision = None


def upgrade():
    op.execute("""
        CREATE TABLE users (
            id integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            username varchar(64) NOT NULL CONSTRAINT uq_users_username UNIQUE,
            password_hash text NOT NULL, role varchar(16) NOT NULL, phone varchar(11) NOT NULL,
            CONSTRAINT ck_users_username CHECK (username <> '' AND username = lower(username)
                AND username !~ '^[[:space:]]|[[:space:]]$'),
            CONSTRAINT ck_users_hash CHECK (password_hash ~ '[^[:space:]]'),
            CONSTRAINT ck_users_role CHECK (role IN ('user','admin')),
            CONSTRAINT ck_users_phone CHECK (phone ~ '^1[3-9][0-9]{9}$')
        )
    """)
    op.execute("""
        CREATE TABLE devices (
            id integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            code varchar(64) COLLATE "C" NOT NULL CONSTRAINT uq_devices_code UNIQUE,
            name varchar(128) NOT NULL, location varchar(128) NOT NULL, status varchar(16) NOT NULL,
            CONSTRAINT ck_devices_code CHECK (code <> '' AND code !~ '^[[:space:]]|[[:space:]]$'),
            CONSTRAINT ck_devices_text CHECK (name ~ '[^[:space:]]' AND location ~ '[^[:space:]]'),
            CONSTRAINT ck_devices_status CHECK (status IN ('Available','Disabled'))
        )
    """)
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
