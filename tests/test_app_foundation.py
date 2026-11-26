import os
import socket
import subprocess
import sys
import time
from pathlib import Path

from urllib.error import URLError
from urllib.request import ProxyHandler, build_opener

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import text

from labbooking import create_app
from labbooking.config import ConfigurationError
from labbooking.extensions import db


ROOT = Path(__file__).resolve().parents[1]
DEV = "LABBOOKING_DEV_DATABASE_URL"
TEST = "LABBOOKING_TEST_DATABASE_URL"
MIGRATION = "LABBOOKING_MIGRATION_DATABASE_URL"


def test_configuration_errors_are_safe(monkeypatch):
    monkeypatch.delenv("LABBOOKING_SECRET_KEY", raising=False)
    with pytest.raises(ConfigurationError, match="LABBOOKING_SECRET_KEY"):
        create_app()
    marker = "synthetic-sensitive-value"
    cfg = {"LABBOOKING_SECRET_KEY": marker, "TESTING": True,
           DEV: "postgresql+psycopg://dev@localhost/dev_db", TEST: marker}
    for bad_url in (marker, f"postgresql+psycopg://user:{marker}@localhost:invalid/test_db",
                    f"postgresql+psycopg://user:{marker}@localhost/test_db?dbname=dev_db"):
        with pytest.raises(ConfigurationError, match=TEST) as exc:
            create_app({**cfg, TEST: bad_url})
        assert marker not in str(exc.value)
    with pytest.raises(ConfigurationError, match="distinct name"):
        create_app({**cfg, TEST: "postgresql+psycopg://other@127.0.0.1/dev_db"})
    with pytest.raises(ConfigurationError, match="disagree"):
        create_app({**cfg, "LABBOOKING_ENV": "development"})


def test_request_sessions_and_database_isolation(databases):
    dev_app = create_app({**databases, "LABBOOKING_ENV": "development"})
    with dev_app.app_context():
        assert db.session.scalar(text("SELECT current_database()")) == "dev_db"
        db.session.remove()
        db.engine.dispose()

    app = create_app(databases)
    assert app.testing and not app.debug
    assert set(app.blueprints) == {"auth", "devices", "bookings"}
    assert set(db.metadata.tables) == {"users", "devices", "bookings"}
    sessions = []

    @app.get("/_test_probe")
    def probe():
        sessions.append(db.session())
        database, isolation, backend, name = db.session.execute(text(
            "SELECT current_database(), current_setting('transaction_isolation'), "
            "pg_backend_pid(), current_setting('application_name')"
        )).one()
        db.session.execute(text("SELECT set_config('application_name', 'story_1_1_request', true)"))
        return dict(database=database, isolation=isolation, backend=backend, name=name)

    client = app.test_client()
    try:
        first, second = [client.get("/_test_probe").get_json() for _ in range(2)]
        assert first == second
        assert first["database"] == "test_db" and first["isolation"] == "read committed"
        assert first["name"] != "story_1_1_request"
        assert sessions[0] is not sessions[1]
        assert all(not session.in_transaction() for session in sessions)
        with app.app_context():
            assert db.engine.pool.checkedout() == 0
    finally:
        with app.app_context():
            db.engine.dispose()


def test_alembic_uses_only_the_selected_database(databases, monkeypatch):
    for key, value in databases.items():
        monkeypatch.setenv(key, value)
    cfg = Config(str(ROOT / "alembic.ini"))
    monkeypatch.setenv(TEST, databases[DEV])
    with pytest.raises(ConfigurationError, match="distinct name"):
        command.upgrade(cfg, "head")
    monkeypatch.setenv(TEST, databases[TEST])
    monkeypatch.setenv(MIGRATION, databases[MIGRATION].replace("/test_db", "/dev_db"))
    with pytest.raises(ConfigurationError, match="same database target"):
        command.upgrade(cfg, "head")
    monkeypatch.setenv(MIGRATION, databases[TEST])
    with pytest.raises(ConfigurationError, match="separate database role"):
        command.upgrade(cfg, "head")
    monkeypatch.setenv(MIGRATION, databases[MIGRATION])
    command.upgrade(cfg, "head")
    command.ensure_version(cfg)
    for profile, expected in (("development", None), ("test", "alembic_version")):
        app = create_app({**databases, "LABBOOKING_ENV": profile})
        with app.app_context():
            assert db.session.scalar(text("SELECT to_regclass('public.alembic_version')::text")) == expected
            db.session.remove()
            db.engine.dispose()


def test_waitress_factory_serves_login(databases):
    with socket.socket() as available:
        available.bind(("127.0.0.1", 0))
        port = available.getsockname()[1]
    args = [sys.executable, "-m", "waitress", f"--listen=127.0.0.1:{port}",
            "--call", "labbooking:create_app"]
    process = subprocess.Popen(args, cwd=ROOT, env={**os.environ, **databases})
    opener = build_opener(ProxyHandler({}))
    try:
        deadline = time.monotonic() + 30
        while time.monotonic() < deadline:
            assert process.poll() is None, "Waitress exited before serving"
            try:
                with opener.open(f"http://127.0.0.1:{port}/login", timeout=2) as response:
                    assert response.status == 200 and b'csrf_token' in response.read()
                    return
            except URLError:
                time.sleep(0.1)
        pytest.fail("Waitress did not respond within 30 seconds")
    finally:
        process.terminate()
        process.wait(timeout=10)
