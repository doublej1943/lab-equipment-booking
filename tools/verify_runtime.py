"""Run from the repository root with python -m tools.verify_runtime on Windows."""

import json
import os
import sys
from contextlib import contextmanager
from datetime import datetime
from importlib.metadata import version
from pathlib import Path
from secrets import token_urlsafe
from socket import socket
from subprocess import run
from tempfile import TemporaryDirectory
from threading import Thread
from time import perf_counter
from urllib.request import ProxyHandler, build_opener
from zoneinfo import ZoneInfo

import psycopg
from flask import Flask, render_template_string
from flask_sqlalchemy import SQLAlchemy
from psycopg import sql
from sqlalchemy import URL, text
from waitress import create_server

from labbooking.auth.passwords import SALT_LENGTH, SCRYPT_METHOD, hash_password, verify_password


def check(condition, message):
    if not condition:
        raise RuntimeError(message)


def check_conda_lock():
    lock = Path(__file__).resolve().parents[1] / "conda-win-64.lock"
    expected = {row for row in lock.read_text().splitlines() if row.startswith("https://")}
    installed = set()
    for path in (Path(sys.prefix) / "conda-meta").glob("*.json"):
        record = json.loads(path.read_text(encoding="utf-8"))
        installed.add(f"{record['url']}#{record['sha256']}")
    check(expected and expected == installed, "Installed Conda builds differ from win-64 lock")
    print(f"Matched {len(installed)} Conda builds, Python {sys.version.split()[0]}")


def password_probe():
    password = token_urlsafe(24)
    start = perf_counter()
    encoded = hash_password(password)
    generated = perf_counter()
    valid = verify_password(encoded, password)
    verified = perf_counter()
    method, salt, _ = encoded.split("$")
    check(method == SCRYPT_METHOD and len(salt) == SALT_LENGTH, "Encoded policy mismatch")
    check(valid and not verify_password(encoded, password + "x"), "Password check failed")
    check(hash_password(password).split("$")[1] != salt, "Two fresh salts matched")
    return {"werkzeug": version("werkzeug"), "method": method, "salt_chars": len(salt),
            "generate_ms": round(1000 * (generated - start), 1),
            "verify_ms": round(1000 * (verified - generated), 1)}


@contextmanager
def temporary_postgres_cluster():
    pg_bin = Path(os.environ["LABBOOKING_PG_BIN"]).resolve(strict=True)
    with TemporaryDirectory(prefix="labbooking-dp01-") as directory:
        base = Path(directory)
        data = str(base / "data")
        secret_file = base / "init.pw"
        admin_secret = token_urlsafe(32)
        secret_file.write_text(admin_secret, encoding="ascii")
        try:
            run([pg_bin / "initdb.exe", "-D", data, "-U", "prep_admin", "-A", "scram-sha-256",
                 "--pwfile", str(secret_file), "--encoding=UTF8", "--locale=C"],
                cwd=base, check=True)
        finally:
            secret_file.unlink(missing_ok=True)
        with socket() as port_probe:
            port_probe.bind(("127.0.0.1", 0))
            port = port_probe.getsockname()[1]
        server_args = f"-h 127.0.0.1 -p {port} -c timezone=Asia/Shanghai"
        run([pg_bin / "pg_ctl.exe", "-D", data, "-l", str(base / "postgres.log"), "-o", server_args,
             "-w", "start"], cwd=base, check=True)
        try:
            yield URL.create("postgresql+psycopg", username="prep_admin", password=admin_secret,
                             host="127.0.0.1", port=port, database="postgres")
        finally:
            run([pg_bin / "pg_ctl.exe", "-D", data, "-m", "fast", "-w", "stop"],
                cwd=base, check=True)


@contextmanager
def temporary_postgres():
    with temporary_postgres_cluster() as admin:
        password = token_urlsafe(32)
        with psycopg.connect(**admin.translate_connect_args(username="user", database="dbname")) as conn:
            conn.execute(sql.SQL("CREATE ROLE prep_reader LOGIN PASSWORD {}").format(
                sql.Literal(password)))
        yield admin.set(username="prep_reader", password=password)


def runtime_probe(url):
    app = Flask(__name__)
    app.config.update(SQLALCHEMY_DATABASE_URI=url, SQLALCHEMY_ENGINE_OPTIONS={
        "isolation_level": "READ COMMITTED", "pool_size": 1, "max_overflow": 0})
    db = SQLAlchemy(app)

    @app.get("/")
    def probe():
        isolation, backend = db.session.execute(text(
            "SELECT current_setting('transaction_isolation'), pg_backend_pid()"
        )).one()
        return render_template_string("{{ isolation }}|{{ backend }}", isolation=isolation,
                                      backend=backend)

    with app.app_context():
        report = dict(db.session.execute(text(
            "SELECT current_setting('server_version') AS postgres, "
            "current_setting('TimeZone') AS timezone, "
            "(SELECT datcollate FROM pg_database WHERE datname=current_database()) AS collation, "
            "current_user AS database_user"
        )).mappings().one())
    check(report["postgres"].split()[0] == "17.12", "Expected PostgreSQL 17.12")
    check(report["timezone"] == "Asia/Shanghai", "Database timezone mismatch")
    check(report["database_user"] == "prep_reader", "Unexpected database user")
    server = create_server(app, host="127.0.0.1", port=0, threads=2, asyncore_loop_timeout=1)
    worker = Thread(target=server.run, daemon=True)
    worker.start()
    try:
        opener = build_opener(ProxyHandler({}))
        backends = set()
        for _ in range(2):
            with opener.open(f"http://127.0.0.1:{server.effective_port}/", timeout=10) as resp:
                isolation, backend = resp.read().decode("ascii").split("|")
                check(resp.status == 200 and isolation == "read committed", "HTTP probe failed")
                backends.add(int(backend))
        check(len(backends) == 1, "Expected two checkouts of the same database connection")
    finally:
        server.task_dispatcher.shutdown()
        server.close()
        worker.join(timeout=5)
        with app.app_context():
            db.engine.dispose()
    return report


if __name__ == "__main__":
    check_conda_lock()
    print(json.dumps(password_probe()))
    offset = datetime(2026, 1, 1, tzinfo=ZoneInfo("Asia/Shanghai")).utcoffset()
    check(offset.total_seconds() == 28800, "IANA timezone mismatch")
    with temporary_postgres() as url:
        print(json.dumps(runtime_probe(url)))
    print("PASS: scrypt, IANA, PostgreSQL, Flask/Jinja, Waitress HTTP and pooled sessions")
