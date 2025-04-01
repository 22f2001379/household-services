from flask import Flask
from application.database import db
from application.models import User, Role, UserRoles
from application.config import LocalDevelopmentConfig
from application.resources import *
from flask_security import Security, SQLAlchemyUserDatastore, hash_password
from celery import Celery
from flask_mail import Mail, Message
from flask_cors import CORS

# Creating the Flask app instance
app = Flask(__name__)

# Specify origins for security
CORS(app, supports_credentials=True, origins=["http://localhost:3000"])  # Allow only Vue.js frontend

# Configuring the app
app.config.from_object(LocalDevelopmentConfig) 



def create_app():
    app = Flask(__name__)
    app.config.from_object(LocalDevelopmentConfig)
    db.init_app(app)
    api.init_app(app)
    datastore = SQLAlchemyUserDatastore(db, User, Role)
    app.security = Security(app, datastore)
    app.app_context().push()
    return app

app = create_app()

with app.app_context():
    db.create_all()
    roles = [
        {"name": "admin", "description": "Administrator role with full access"},
        {"name": "customer", "description": "customer role"},
        {"name": "professional", "description": "Service professional role"}
    ]
    for role in roles:
        app.security.datastore.find_or_create_role(
            name=role["name"],
            description=role["description"]
        )
    admin_email = "admin@me.com"
    admin_password = "adminme"
    if not app.security.datastore.find_user(email=admin_email):
        admin_role = app.security.datastore.find_role("admin")
        app.security.datastore.create_user(
            email=admin_email,
            password=admin_password,
            roles=[admin_role]
        )
    db.session.commit()

from application.routes import *

if __name__ == "__main__":
    app.run(port=5001)
