from secrets import token_urlsafe
import json
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine
from labbooking import create_app
from labbooking.extensions import db
from tests.support import Lab, accounts

DEV = 'LABBOOKING_DEV_DATABASE_URL'
TEST = 'LABBOOKING_TEST_DATABASE_URL'
MIGRATION = 'LABBOOKING_MIGRATION_DATABASE_URL'


@pytest.fixture(scope="module")
def databases():
    import psycopg
    from psycopg import sql
    from tools.verify_runtime import temporary_postgres_cluster

    with temporary_postgres_cluster() as admin:
        with psycopg.connect(**admin.translate_connect_args(username="user", database="dbname"),
                             autocommit=True) as conn:
            roles = {}
            for name in ("app_user", "migration_user"):
                password = token_urlsafe(24)
                conn.execute(sql.SQL("CREATE ROLE {} LOGIN PASSWORD {}").format(
                    sql.Identifier(name), sql.Literal(password)))
                roles[name] = admin.set(username=name, password=password)
            for name in ("dev_db", "test_db"):
                conn.execute(sql.SQL("CREATE DATABASE {} OWNER migration_user").format(sql.Identifier(name)))
        yield {
            "LABBOOKING_ENV": "test",
            "LABBOOKING_SECRET_KEY": token_urlsafe(32),
            DEV: roles["app_user"].set(database="dev_db").render_as_string(hide_password=False),
            TEST: roles["app_user"].set(database="test_db").render_as_string(hide_password=False),
            MIGRATION: roles["migration_user"].set(database="test_db").render_as_string(hide_password=False),
        }


@pytest.fixture(scope="module")
def system(databases):
    config = {**databases, "LABBOOKING_TRANSPORT": "local-http", "LABBOOKING_POOL_SIZE": "24"}
    with pytest.MonkeyPatch.context() as patch:
        for key, value in config.items():
            patch.setenv(key, value)
        command.upgrade(Config(str(Path(__file__).resolve().parents[1] / "alembic.ini")), "head")
        app = create_app(config)
        maintenance = create_engine(config[MIGRATION], hide_parameters=True)
        passwords, phones, records = accounts()
        result = app.test_cli_runner().invoke(args=["init-users", "-"], input=json.dumps(records))
        assert result.exit_code == 0, result.output
        try:
            yield Lab(app, maintenance, passwords, phones)
        finally:
            with app.app_context():
                db.engine.dispose()
            maintenance.dispose()
