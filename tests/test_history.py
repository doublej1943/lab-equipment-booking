"""Check upgrades against existing history and the actual database permission boundary."""
import json
from datetime import date
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, select, text
from sqlalchemy.exc import IntegrityError, ProgrammingError
from sqlalchemy.orm import Session
from labbooking.auth.models import User
from labbooking.devices.models import Device
from labbooking.extensions import db
from labbooking.time_rules import snapshot
from .support import accounts


def test_history_survives_migrations_and_role_changes(databases, monkeypatch):
    for key, value in databases.items():
        monkeypatch.setenv(key, value)
    cfg = Config(str(Path(__file__).resolve().parents[1] / "alembic.ini"))
    command.upgrade(cfg, "0001")
    engine = create_engine(databases["LABBOOKING_MIGRATION_DATABASE_URL"])
    runtime = create_engine(databases["LABBOOKING_TEST_DATABASE_URL"])
    try:
        with engine.begin() as conn:
            conn.execute(text("INSERT INTO users(username,password_hash,role,phone) "
                              "VALUES ('historical','unusable','user',:phone)"), {"phone":accounts()[1]["reader"]})
            conn.execute(text("INSERT INTO devices(code,name,location,status) VALUES ('H','旧设备','旧址','Disabled')"))
            for day, status in ((date(2020,1,1), "Confirmed"), (date(2035,1,1), "Cancelled"),
                                (date(2035,1,1), "Confirmed")):
                start, end = snapshot(day, "AM")
                conn.execute(text("INSERT INTO bookings(user_id,device_id,booking_date,slot,status,start_at,end_at) "
                                  "VALUES (1,1,:day,'AM',:status,:start,:end)"),
                             dict(day=day,status=status,start=start,end=end))
        def contents():
            with engine.connect() as conn:
                return [conn.execute(text(f"SELECT * FROM {table} ORDER BY id")).all()
                        for table in ("users","devices","bookings")]
        original = contents()
        for target in ("head", "0001", "head"):
            if target == "head":
                command.upgrade(cfg, target)
            else:
                command.downgrade(cfg, target)
            assert contents() == original
            with runtime.connect() as conn:
                assert conn.scalar(text("SELECT has_table_privilege(current_user,'bookings','SELECT')")) == (target == "head")
        with runtime.connect() as conn:
            assert conn.scalar(text("SELECT has_column_privilege(current_user,'bookings','status','UPDATE')"))
            for denied in ("DELETE FROM bookings", "UPDATE bookings SET user_id=user_id",
                           "UPDATE devices SET code=code", "UPDATE users SET phone=phone",
                           "DROP TABLE bookings"):
                with pytest.raises(ProgrammingError) as error:
                    conn.execute(text(denied))
                assert error.value.orig.sqlstate == "42501"
                conn.rollback()
        for model in (User, Device):
            for action in ("unloaded", "loaded", "remove"):
                with Session(engine) as session:
                    parent = session.scalars(select(model)).one()
                    if action != "unloaded":
                        assert len(parent.bookings) == 3
                    if action == "remove":
                        parent.bookings.pop()
                    else:
                        session.delete(parent)
                    with pytest.raises(IntegrityError) as error:
                        session.flush()
                    assert error.value.orig.sqlstate == ("23502" if action == "remove" else "23503")
                    session.rollback()
                assert contents() == original
    finally:
        runtime.dispose()
        engine.dispose()


def test_atomic_preset_import(system):
    lab = system
    runner = lab.app.test_cli_runner()
    _, _, records = accounts()
    fresh = dict(records[0], username="  新User  ")
    repeated = dict(records[1], username="  READER ")
    def run(records):
        return runner.invoke(args=["init-users", "-"], input=json.dumps(records, ensure_ascii=False))
    for bad in (repeated, dict(fresh), dict(fresh, role="User"),
                dict(fresh, phone="abc"), {k:v for k,v in fresh.items() if k != "phone"}):
        result = run([fresh, bad])
        assert result.exit_code != 0 and fresh["password"] not in result.output and fresh["phone"] not in result.output
        assert not lab.rows("SELECT id FROM users WHERE username='新user'")
    assert run([fresh]).exit_code == 0
    row = lab.rows("SELECT * FROM users WHERE username='新user'")[0]
    assert row["phone"] == fresh["phone"] and row["password_hash"].startswith("scrypt:32768:8:3$")
    assert fresh["password"] not in row["password_hash"]
