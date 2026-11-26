"""Create the account and device tables before booking history is introduced."""
from alembic import op

revision = "0000"
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


def downgrade():
    raise RuntimeError("Restore a reviewed database backup to roll back accounts and devices.")
