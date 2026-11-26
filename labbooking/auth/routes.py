import json
import os
import time

import click
from flask import Blueprint, abort, redirect, render_template, request, session, url_for
from flask_login import LoginManager, current_user, login_user, logout_user
from sqlalchemy import create_engine, insert
from sqlalchemy.exc import SQLAlchemyError
from labbooking.config import migration_database
from labbooking.errors import Invalid
from labbooking.extensions import validate_database
from labbooking.web import access, field
from . import services
from .models import User

auth = Blueprint("auth", __name__)
login_manager = LoginManager()
login_manager.user_loader(services.load_actor)


def expire_session():
    if "_user_id" in session and time.time() >= session.get("expires_at", 0):
        for key in ("_user_id", "_fresh", "_id", "expires_at"):
            session.pop(key, None)


@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        if current_user.is_authenticated:
            return redirect(url_for("devices.catalog"))
        return render_template("login.html")
    actor = services.authenticate(field(request.form, "username", ""), field(request.form, "password", ""))
    session.clear()
    if actor is None:
        abort(401, description="账号或密码不正确。")
    login_user(actor, remember=False)
    session.permanent = True
    session["expires_at"] = time.time() + 7200
    return redirect(url_for("devices.catalog"), code=303)


@auth.post("/logout")
@access("user", "admin")
def logout(actor):
    logout_user()
    session.clear()
    return redirect(url_for("auth.login"), code=303)


@click.command("init-users")
@click.argument("source", type=click.File("r", encoding="utf-8"))
def init_users(source):
    """Import private preset accounts atomically using the maintenance connection."""
    try:
        rows = services.preset_rows(json.load(source))
    except (ValueError, Invalid):
        raise click.ClickException("账号文件格式错误或存在重复账号。") from None
    engine = create_engine(migration_database(os.environ), hide_parameters=True)
    validate_database(engine, application_role=False)
    try:
        with engine.begin() as connection:
            connection.execute(insert(User), rows)
    except SQLAlchemyError:
        raise click.ClickException("导入失败，请核对数据库状态和账号列表。") from None
    finally:
        engine.dispose()
    click.echo(f"已导入 {len(rows)} 个预设账号。")
