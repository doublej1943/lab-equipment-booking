from flask import Flask

from .auth.routes import auth
from .bookings.routes import bookings
from .config import flask_settings
from .devices.routes import devices
from .extensions import db, validate_database


def create_app(config=None):
    app = Flask(__name__)
    app.config.from_mapping(flask_settings(config))
    db.init_app(app)
    with app.app_context():
        validate_database(db.engine, application_role=True)
    for blueprint in (auth, devices, bookings):
        app.register_blueprint(blueprint)
    return app
