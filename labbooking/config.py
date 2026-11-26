"""Private settings shared by the application factory and Alembic."""

import os
from collections.abc import Mapping

from sqlalchemy import URL, make_url
from sqlalchemy.exc import ArgumentError


class ConfigurationError(ValueError):
    """A configuration problem that can be displayed without credentials."""


def required(settings, key):
    value = settings.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ConfigurationError(f"Missing or empty setting: {key}")
    return value


def database_url(settings, key):
    raw = required(settings, key)
    try:
        url = make_url(raw)
    except (ArgumentError, ValueError):
        raise ConfigurationError(f"Invalid PostgreSQL URL in {key}") from None
    if (url.drivername != "postgresql+psycopg" or not url.host or not url.database
            or not url.username or url.port == 0):
        raise ConfigurationError(f"{key} requires a postgresql+psycopg URL with user, host and database")
    if url.query.keys() & {"dbname", "database", "user", "password", "host", "hostaddr", "port", "service"}:
        raise ConfigurationError(f"{key} must specify the database target and role in the URL, once")
    return url.set(port=5432 if url.port is None else url.port)


def application_database(settings):
    profile = required(settings, "LABBOOKING_ENV")
    if profile not in {"development", "test"}:
        raise ConfigurationError("LABBOOKING_ENV must be development or test")
    development = database_url(settings, "LABBOOKING_DEV_DATABASE_URL")
    if profile == "development":
        return development
    test = database_url(settings, "LABBOOKING_TEST_DATABASE_URL")
    if test.database == development.database:
        raise ConfigurationError("The test database must have a distinct name from the development database")
    return test


def migration_database(settings) -> URL:
    runtime = application_database(settings)
    migration = database_url(settings, "LABBOOKING_MIGRATION_DATABASE_URL")
    if (runtime.host.lower(), runtime.port, runtime.database) != (
        migration.host.lower(), migration.port, migration.database
    ):
        raise ConfigurationError("Migration and application connections must select the same database target")
    if migration.username == runtime.username:
        raise ConfigurationError("Use a separate database role for migrations")
    return migration


def flask_settings(overrides: Mapping | None):
    settings = dict(os.environ)
    if overrides is not None:
        settings.update(overrides)
        if "TESTING" in overrides:
            testing = overrides["TESTING"]
            if not isinstance(testing, bool):
                raise ConfigurationError("TESTING must be a boolean")
            profile = "test" if testing else "development"
            if overrides.get("LABBOOKING_ENV", profile) != profile:
                raise ConfigurationError("TESTING and LABBOOKING_ENV disagree")
            settings["LABBOOKING_ENV"] = profile
    cookie_mode = settings.get("LABBOOKING_TRANSPORT", "https")
    if cookie_mode not in {"https", "local-http"}:
        raise ConfigurationError("LABBOOKING_TRANSPORT must be https or local-http")
    try:
        pool_size = int(settings.get("LABBOOKING_POOL_SIZE", "5"))
        if pool_size <= 0:
            raise ValueError
    except (ValueError, TypeError):
        raise ConfigurationError("LABBOOKING_POOL_SIZE must be a positive integer") from None
    return {
        "DEBUG": False,
        "SESSION_COOKIE_SECURE": cookie_mode == "https",
        "SECRET_KEY": required(settings, "LABBOOKING_SECRET_KEY"),
        "SQLALCHEMY_DATABASE_URI": application_database(settings),
        "SQLALCHEMY_ENGINE_OPTIONS": {
            "isolation_level": "READ COMMITTED",
            "pool_size": pool_size,
            "max_overflow": 0,
            "pool_timeout": 10,
            "hide_parameters": True,
            "connect_args": {"connect_timeout": 10, "options": "-c lock_timeout=10s -c statement_timeout=30s"},
        },
        "TESTING": settings["LABBOOKING_ENV"] == "test",
    }
