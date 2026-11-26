"""Permit ordinary application operations without granting history deletion."""
import os
from alembic import op
from labbooking.config import application_database

revision = "0002"
down_revision = "0001"


def runtime_role():
    username = application_database(os.environ).username
    return op.get_context().dialect.identifier_preparer.quote_identifier(username)


def upgrade():
    role = runtime_role()
    op.execute(f"GRANT USAGE ON SCHEMA public TO {role}")
    op.execute(f"GRANT SELECT ON users, devices, bookings TO {role}")
    op.execute(f"GRANT INSERT (code, name, location, status), UPDATE (name, location, status) ON devices TO {role}")
    op.execute(f"GRANT INSERT (user_id, device_id, booking_date, slot, status, start_at, end_at), "
               f"UPDATE (status) ON bookings TO {role}")


def downgrade():
    role = runtime_role()
    op.execute(f"REVOKE INSERT (code, name, location, status), UPDATE (name, location, status) ON devices FROM {role}")
    op.execute(f"REVOKE INSERT (user_id, device_id, booking_date, slot, status, start_at, end_at), "
               f"UPDATE (status) ON bookings FROM {role}")
    op.execute(f"REVOKE SELECT ON users, devices, bookings FROM {role}")
