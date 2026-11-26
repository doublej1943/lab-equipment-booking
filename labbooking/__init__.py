from datetime import timedelta
from flask import Flask, render_template, url_for
from flask_wtf.csrf import CSRFProtect
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.exceptions import HTTPException

from .auth.routes import auth, expire_session, init_users, login_manager
from .bookings.routes import bookings
from .config import flask_settings
from .devices.routes import devices
from .errors import BusinessError, Conflict, Forbidden, Invalid, Missing, UnknownCommit, temporary_failure
from .extensions import db, validate_database
from .time_rules import ZONE


def create_app(config=None):
    app = Flask(__name__)
    app.config.from_mapping(flask_settings(config))
    app.config.update(SESSION_COOKIE_HTTPONLY=True, SESSION_COOKIE_SAMESITE="Lax",
                      PERMANENT_SESSION_LIFETIME=timedelta(hours=2), SESSION_REFRESH_EACH_REQUEST=False,
                      WTF_CSRF_TIME_LIMIT=timedelta(hours=2))
    db.init_app(app)
    with app.app_context():
        validate_database(db.engine, application_role=True)
    login_manager.init_app(app, add_context_processor=False)
    app.before_request(expire_session)
    CSRFProtect(app)
    for blueprint in (auth, devices, bookings):
        app.register_blueprint(blueprint)
    app.cli.add_command(init_users)
    app.add_template_filter(lambda value: value.astimezone(ZONE).strftime("%Y-%m-%d %H:%M"), "localtime")

    @app.after_request
    def private_response(response):
        response.headers["Cache-Control"] = "private, no-store"
        response.headers["X-Content-Type-Options"] = "nosniff"
        return response

    @app.errorhandler(BusinessError)
    def business_error(error):
        recovery = None
        if isinstance(error, UnknownCommit):
            status = 503
            if error.booking_id is not None:
                recovery = url_for("bookings.detail", booking_id=error.booking_id)
            elif "预约" in str(error):
                recovery = url_for("bookings.mine")
            else:
                recovery = url_for("devices.catalog")
        elif isinstance(error, Conflict):
            status = 409
        else:
            status = {Invalid: 400, Forbidden: 403, Missing: 404}[type(error)]
        return render_template("error.html", message=str(error), recovery=recovery), status

    @app.errorhandler(SQLAlchemyError)
    def database_error(error):
        status = 503 if temporary_failure(error) else 500
        app.logger.warning("Database request failed (%s)", type(error).__name__)
        return render_template("error.html", message="数据库请求未完成，请稍后再查看。"), status

    @app.errorhandler(HTTPException)
    def http_error(error):
        labels = {400: "表单无效，请刷新页面后重新填写。", 401: "请重新登录或核对账号密码。",
                  403: "当前账号无权执行此操作。", 404: "找不到此资源。"}
        response = error.get_response()
        response.set_data(render_template("error.html", message=labels.get(error.code, "请求无法完成。")))
        return response

    return app
