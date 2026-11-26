from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import event

from .config import ConfigurationError


db = SQLAlchemy()


def validate_database(engine, *, application_role):
    """Check each physical connection before it reaches a request or a migration."""
    @event.listens_for(engine, "connect")
    def check_target(connection, _record):
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT current_database(), current_setting('server_version_num')::int, "
                "current_user, rolsuper FROM pg_roles WHERE rolname = current_user"
            )
            database, version, role, superuser = cursor.fetchone()
        connection.rollback()
        if database != engine.url.database or version // 10000 != 17:
            raise ConfigurationError("Connected database does not match the configured PostgreSQL 17 target")
        if role != engine.url.username or (application_role and superuser):
            raise ConfigurationError("Connected database role is unsuitable for this configuration")
