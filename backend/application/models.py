from .database import db
from flask_security import UserMixin, RoleMixin
from werkzeug.security import check_password_hash  # To manually check the password hash

# User Table
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    fs_uniquifier = db.Column(db.String, unique=True, nullable=False)
    active = db.Column(db.Boolean, nullable=False, default=True)
    roles = db.relationship('Role', secondary='user_roles', backref=db.backref('users', lazy='dynamic'))
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'))
    user_name = db.Column(db.String(50), nullable=True)
    service = db.Column(db.String(50), nullable=True)
    location = db.Column(db.String(50), nullable=True)
    approved = db.Column(db.Boolean, default=False, nullable=False)
    experience = db.Column(db.String(50), nullable = True)
    # documents = db.Column(db.String(50), nullable = True)
    
    # Adding a relationship to Service
    services = db.relationship('Service', backref='user', lazy=True)
        # Manually define verify_password if necessary
    # def verify_password(self, password):
    #     # Use werkzeug's check_password_hash method to compare hashed passwords
    #     return check_password_hash(self.password, password)

# Role Table
class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.String)

# Many-to-Many Relationship Table for User and Role
class UserRoles(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'))

class Service(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    base_price = db.Column(db.Float, nullable=False)
    time_required = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(255))
    
    # Adding a foreign key to User
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

class ServiceRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    professional_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    date_of_request = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())
    date_of_completion = db.Column(db.DateTime)
    service_status = db.Column(db.String(50), nullable=False, default='requested') 
    remarks = db.Column(db.String(255))
    status = db.Column(db.String(255))

    # Relationships
    service = db.relationship('Service', backref=db.backref('requests', lazy=True))
    customer = db.relationship('User', foreign_keys=[customer_id], backref=db.backref('customer_requests', lazy=True))
    professional = db.relationship('User', foreign_keys=[professional_id], backref=db.backref('professional_requests', lazy=True))

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    service_request_id = db.Column(db.Integer, db.ForeignKey('service_request.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # e.g., 1 to 5
    review_text = db.Column(db.String(255))
    date_posted = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())

    # Relationships
    service_request = db.relationship('ServiceRequest', backref=db.backref('review', lazy=True))