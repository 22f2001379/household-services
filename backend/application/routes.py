from datetime import datetime

from flask import current_app as app, jsonify, request
from flask_security import auth_required, current_user, hash_password, roles_required
from flask_security.utils import verify_password
from sqlalchemy.exc import IntegrityError

from .database import db
from .models import Review, Role, Service, ServiceRequest, User

ALLOWED_ROLES = {"customer", "professional"}
SERVICE_STATUSES = {"requested", "accepted", "rejected", "closed"}


def payload():
    return request.get_json(silent=True) or {}


def error(message, status=400):
    return jsonify({"error": message}), status


def parse_iso_datetime(value, field_name):
    if not value:
        return None
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        raise ValueError(f"{field_name} must be an ISO-8601 date or datetime")


def role_names(user):
    return [role.name for role in user.roles]


def serialize_user(user):
    return {
        "id": user.id,
        "email": user.email,
        "name": user.user_name,
        "location": user.location,
        "service": user.service,
        "experience": user.experience,
        "roles": role_names(user),
        "active": user.active,
        "approved": user.approved,
    }


def serialize_service(service):
    return {
        "id": service.id,
        "name": service.name,
        "price": service.base_price,
        "timeRequired": service.time_required,
        "description": service.description or "",
        "user_id": service.user_id,
    }


def average_rating_for_professional(professional_id):
    reviews = (
        Review.query.join(ServiceRequest)
        .filter(ServiceRequest.professional_id == professional_id)
        .all()
    )
    if not reviews:
        return None
    return round(sum(review.rating for review in reviews) / len(reviews), 1)


def serialize_professional(user):
    return {
        "id": user.id,
        "email": user.email,
        "service": user.service,
        "name": user.user_name,
        "location": user.location,
        "experience": user.experience,
        "approved": user.approved,
        "rating": average_rating_for_professional(user.id),
    }


def serialize_service_request(service_request):
    return {
        "id": service_request.id,
        "service_id": service_request.service_id,
        "customer_id": service_request.customer_id,
        "professional_id": service_request.professional_id,
        "date_of_request": service_request.date_of_request.isoformat(),
        "date_of_completion": (
            service_request.date_of_completion.isoformat()
            if service_request.date_of_completion
            else None
        ),
        "service_status": service_request.service_status,
        "remarks": service_request.remarks or "",
        "service": service_request.service.name if service_request.service else None,
        "rating": service_request.review[0].rating if service_request.review else None,
    }


def user_has_role(user, role_name):
    return role_name in role_names(user)


@app.errorhandler(IntegrityError)
def handle_integrity_error(exc):
    db.session.rollback()
    return error("Request conflicts with existing data", 409)


@app.errorhandler(404)
def handle_not_found(exc):
    return error("Resource not found", 404)


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200


@app.route("/api/login", methods=["POST"])
def login_user():
    data = payload()
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    if not email or not password:
        return error("Email and password are required")

    user = app.security.datastore.find_user(email=email)
    if not user or not verify_password(password, user.password):
        return error("Invalid email or password", 401)

    if user_has_role(user, "professional") and not user.approved:
        return error("Account is not approved. Please contact admin.", 403)

    return jsonify(
        {
            "message": "Login successful",
            "token": user.get_auth_token(),
            "user": serialize_user(user),
        }
    ), 200


@app.route("/api/register", methods=["POST"])
def create_user():
    data = payload()
    name = (data.get("name") or "").strip()
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    location = (data.get("location") or "").strip()
    role_name = data.get("role", "customer")

    if role_name not in ALLOWED_ROLES:
        return error("Role must be customer or professional")
    if not name or not email or not password or not location:
        return error("Name, email, password, and location are required")
    if len(password) < 8:
        return error("Password must be at least 8 characters")
    if app.security.datastore.find_user(email=email):
        return error("Email already registered", 409)

    role = Role.query.filter_by(name=role_name).first()
    user = app.security.datastore.create_user(
        email=email,
        password=hash_password(password),
        roles=[role],
        approved=role_name != "professional",
        role_id=role.id,
        user_name=name,
        location=location,
        service=(data.get("service") or "").strip() if role_name == "professional" else None,
        experience=str(data.get("experience") or "").strip() if role_name == "professional" else None,
    )
    db.session.commit()
    return jsonify({"message": "User created successfully", "user": serialize_user(user)}), 201


@app.route("/api/admin/users", methods=["GET"])
@auth_required("token")
@roles_required("admin")
def list_users():
    return jsonify([serialize_user(user) for user in User.query.order_by(User.id).all()]), 200


@app.route("/api/get/customers", methods=["GET"])
@auth_required("token")
@roles_required("admin")
def get_customers():
    users = User.query.join(User.roles).filter(Role.name == "customer").order_by(User.id).all()
    return jsonify([serialize_user(user) for user in users]), 200


@app.route("/api/get/professionals", methods=["GET"])
@auth_required("token")
def get_professionals():
    query = User.query.join(User.roles).filter(Role.name == "professional")
    if user_has_role(current_user, "customer"):
        query = query.filter(User.approved.is_(True), User.active.is_(True))
    professionals = query.order_by(User.id).all()
    return jsonify([serialize_professional(user) for user in professionals]), 200


@app.route("/api/update/user/<int:user_id>", methods=["PUT"])
@auth_required("token")
@roles_required("admin")
def update_user(user_id):
    user = User.query.get_or_404(user_id)
    data = payload()

    if "name" in data:
        user.user_name = (data.get("name") or "").strip()
    if "email" in data:
        email = (data.get("email") or "").strip().lower()
        if not email:
            return error("Email cannot be empty")
        existing = User.query.filter(User.email == email, User.id != user_id).first()
        if existing:
            return error("Email already in use", 409)
        user.email = email
    if data.get("password"):
        if len(data["password"]) < 8:
            return error("Password must be at least 8 characters")
        user.password = hash_password(data["password"])
    for field in ("location", "service", "experience"):
        if field in data:
            setattr(user, field, data.get(field))
    if "approved" in data:
        user.approved = bool(data["approved"])

    db.session.commit()
    return jsonify({"message": "User updated successfully", "user": serialize_user(user)}), 200


@app.route("/api/delete/user/<int:user_id>", methods=["DELETE"])
@auth_required("token")
@roles_required("admin")
def delete_user(user_id):
    if user_id == current_user.id:
        return error("Admins cannot delete their own account")
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": "User deleted successfully", "user_id": user_id}), 200


@app.route("/api/add/services", methods=["POST"])
@auth_required("token")
@roles_required("admin")
def add_service():
    data = payload()
    name = (data.get("name") or "").strip()
    time_required = (data.get("timeRequired") or "").strip()
    if not name or not time_required:
        return error("Service name and time required are required")

    try:
        price = float(data.get("price"))
    except (TypeError, ValueError):
        return error("Price must be a number")
    if price <= 0:
        return error("Price must be positive")

    service = Service(
        name=name,
        base_price=price,
        time_required=time_required,
        description=(data.get("description") or "").strip(),
        user_id=data.get("user_id"),
    )
    db.session.add(service)
    db.session.commit()
    return jsonify({"message": "Service added successfully", "service": serialize_service(service)}), 201


@app.route("/api/get/services", methods=["GET"])
def get_services():
    services = Service.query.order_by(Service.name).all()
    return jsonify([serialize_service(service) for service in services]), 200


@app.route("/api/update/services/<int:service_id>", methods=["PUT"])
@auth_required("token")
@roles_required("admin")
def update_service(service_id):
    service = Service.query.get_or_404(service_id)
    data = payload()
    if "name" in data:
        service.name = (data.get("name") or "").strip()
    if "timeRequired" in data:
        service.time_required = (data.get("timeRequired") or "").strip()
    if "description" in data:
        service.description = data.get("description") or ""
    if "price" in data:
        try:
            price = float(data["price"])
        except (TypeError, ValueError):
            return error("Price must be a number")
        if price <= 0:
            return error("Price must be positive")
        service.base_price = price

    db.session.commit()
    return jsonify({"message": "Service updated successfully", "service": serialize_service(service)}), 200


@app.route("/api/delete/services/<int:service_id>", methods=["DELETE"])
@auth_required("token")
@roles_required("admin")
def delete_service(service_id):
    service = Service.query.get_or_404(service_id)
    db.session.delete(service)
    db.session.commit()
    return jsonify({"message": "Service deleted successfully", "service_id": service_id}), 200


@app.route("/api/add/service-request", methods=["POST"])
@auth_required("token")
@roles_required("customer")
def add_service_request():
    data = payload()
    service_name = (data.get("service") or "").strip()
    service = Service.query.filter_by(name=service_name).first()
    if not service:
        return error("Service not found", 404)

    professional_id = data.get("professionalId")
    professional = db.session.get(User, professional_id) if professional_id else None
    if not professional or not user_has_role(professional, "professional") or not professional.approved:
        return error("Approved professional is required")

    try:
        date_of_request = parse_iso_datetime(data.get("dateOfRequest"), "dateOfRequest") or datetime.utcnow()
        date_of_completion = parse_iso_datetime(data.get("dateOfCompletion"), "dateOfCompletion")
    except ValueError as exc:
        return error(str(exc))
    if date_of_completion and date_of_completion < date_of_request:
        return error("Completion date cannot be before request date")

    service_request = ServiceRequest(
        service_id=service.id,
        customer_id=current_user.id,
        professional_id=professional.id,
        date_of_request=date_of_request,
        date_of_completion=date_of_completion,
        service_status="requested",
        remarks=(data.get("remarks") or "").strip(),
    )
    db.session.add(service_request)
    db.session.commit()
    return jsonify(
        {
            "message": "Service request added successfully",
            "service_request": serialize_service_request(service_request),
        }
    ), 201


@app.route("/api/get/service-request", methods=["GET"])
@auth_required("token")
def get_service_requests():
    query = ServiceRequest.query
    if user_has_role(current_user, "customer"):
        query = query.filter_by(customer_id=current_user.id)
    elif user_has_role(current_user, "professional"):
        query = query.filter_by(professional_id=current_user.id)
    elif not user_has_role(current_user, "admin"):
        return error("Forbidden", 403)

    service_requests = query.order_by(ServiceRequest.date_of_request.desc()).all()
    return jsonify([serialize_service_request(item) for item in service_requests]), 200


@app.route("/api/get/professional-service-request/<int:professional_id>", methods=["GET"])
@auth_required("token")
def get_professional_service_requests(professional_id):
    if not user_has_role(current_user, "admin") and current_user.id != professional_id:
        return error("Forbidden", 403)
    service_requests = (
        ServiceRequest.query.filter_by(professional_id=professional_id)
        .order_by(ServiceRequest.date_of_request.desc())
        .all()
    )
    return jsonify([serialize_service_request(item) for item in service_requests]), 200


@app.route("/api/update/professional-service-request/<int:request_id>", methods=["PUT"])
@auth_required("token")
@roles_required("professional")
def update_professional_request_service(request_id):
    service_request = ServiceRequest.query.get_or_404(request_id)
    if service_request.professional_id != current_user.id:
        return error("Forbidden", 403)

    status = payload().get("service_status")
    if status not in {"accepted", "rejected"}:
        return error("Professional status must be accepted or rejected")
    service_request.service_status = status
    db.session.commit()
    return jsonify(serialize_service_request(service_request)), 200


@app.route("/api/update/service-request/<int:request_id>", methods=["PUT"])
@auth_required("token")
@roles_required("customer")
def update_service_requests(request_id):
    service_request = ServiceRequest.query.get_or_404(request_id)
    if service_request.customer_id != current_user.id:
        return error("Forbidden", 403)

    status = payload().get("service_status")
    if status != "closed":
        return error("Customers can only close requests")
    service_request.service_status = status
    service_request.date_of_completion = service_request.date_of_completion or datetime.utcnow()
    db.session.commit()
    return jsonify(serialize_service_request(service_request)), 200


@app.route("/api/delete/service-request/<int:request_id>", methods=["DELETE"])
@auth_required("token")
def delete_service_request(request_id):
    service_request = ServiceRequest.query.get_or_404(request_id)
    if not user_has_role(current_user, "admin") and service_request.customer_id != current_user.id:
        return error("Forbidden", 403)
    db.session.delete(service_request)
    db.session.commit()
    return jsonify({"message": "Service request deleted successfully", "request_id": request_id}), 200


@app.route("/api/get/reviews", methods=["GET"])
@auth_required("token")
def get_review():
    reviews = Review.query.order_by(Review.date_posted.desc()).all()
    return jsonify(
        {
            "reviews": [
                {
                    "id": review.id,
                    "service_request_id": review.service_request_id,
                    "rating": review.rating,
                    "review_text": review.review_text,
                    "date_posted": review.date_posted.isoformat(),
                }
                for review in reviews
            ]
        }
    ), 200


@app.route("/api/get/reviews", methods=["POST"])
@auth_required("token")
@roles_required("customer")
def add_review():
    data = payload()
    service_request_id = data.get("service_request_id")
    rating = data.get("rating")
    review_text = data.get("review_text") or data.get("reviewText") or ""

    try:
        rating = int(rating)
    except (TypeError, ValueError):
        return error("Rating must be an integer from 1 to 5")
    if rating < 1 or rating > 5:
        return error("Rating must be between 1 and 5")

    service_request = db.session.get(ServiceRequest, service_request_id)
    if not service_request or service_request.customer_id != current_user.id:
        return error("Invalid service_request_id", 404)
    if service_request.service_status != "closed":
        return error("Only closed requests can be reviewed")
    if service_request.review:
        return error("Request already reviewed", 409)

    review = Review(
        service_request_id=service_request_id,
        rating=rating,
        review_text=review_text.strip(),
    )
    db.session.add(review)
    db.session.commit()
    return jsonify({"message": "Review added successfully", "review_id": review.id}), 201
