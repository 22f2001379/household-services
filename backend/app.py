import importlib
import os
import sys
from pathlib import Path

from celery import Celery
from flask import Flask
from flask_cors import CORS
from flask_mail import Mail, Message
from flask_security import Security, SQLAlchemyUserDatastore, hash_password

from application.config import LocalDevelopmentConfig
from application.database import db
from application.models import Role, ServiceRequest, User
from application.resources import api

mail = Mail()
celery = Celery("household-services")


def create_app(config_object=LocalDevelopmentConfig):
    app = Flask(__name__)
    app.config.from_object(config_object)
    app.name = "household-services"
    if app.config["SQLALCHEMY_DATABASE_URI"].startswith("sqlite:///"):
        database_path = app.config["SQLALCHEMY_DATABASE_URI"].replace("sqlite:///", "", 1)
        if database_path != ":memory:":
            Path(database_path).parent.mkdir(parents=True, exist_ok=True)

    db.init_app(app)
    api.init_app(app)
    mail.init_app(app)
    CORS(app, supports_credentials=True, origins=app.config["CORS_ORIGINS"])

    datastore = SQLAlchemyUserDatastore(db, User, Role)
    app.security = Security(app, datastore)

    with app.app_context():
        if "application.routes" in sys.modules:
            importlib.reload(sys.modules["application.routes"])
        else:
            importlib.import_module("application.routes")

        db.create_all()
        seed_roles(datastore)
        seed_admin(app, datastore)

    celery.conf.update(app.config)
    return app


def seed_roles(datastore):
    roles = {
        "admin": "Administrator role with full access",
        "customer": "Customer role",
        "professional": "Service professional role",
    }
    for name, description in roles.items():
        datastore.find_or_create_role(name=name, description=description)
    db.session.commit()


def seed_admin(app, datastore):
    email = app.config.get("ADMIN_EMAIL")
    password = app.config.get("ADMIN_PASSWORD")
    if not email or not password or datastore.find_user(email=email):
        return

    admin_role = datastore.find_role("admin")
    datastore.create_user(
        email=email,
        password=hash_password(password),
        roles=[admin_role],
        role_id=admin_role.id,
        user_name="Admin",
        approved=True,
    )
    db.session.commit()


@celery.task
def send_daily_reminders():
    pending = ServiceRequest.query.filter_by(service_status="assigned").all()
    for service_request in pending:
        professional = service_request.professional
        if not professional or not professional.email:
            continue

        msg = Message("Pending Request Reminder", recipients=[professional.email])
        msg.body = f"Request ID: {service_request.id} is assigned to you. Act on it."
        mail.send(msg)


app = None if os.getenv("HOUSEHOLD_SKIP_AUTO_APP") == "1" else create_app()


if __name__ == "__main__":
    app.run(port=5001)
