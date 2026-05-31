import sys
from pathlib import Path
import os

import pytest

os.environ["HOUSEHOLD_SKIP_AUTO_APP"] = "1"
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app import create_app
from application.config import TestingConfig
from application.database import db

@pytest.fixture()
def client():
    app = create_app(TestingConfig)
    app.config.update(SERVER_NAME="localhost")
    test_client = app.test_client(use_cookies=False)
    yield test_client
    with app.app_context():
        db.session.remove()
        db.drop_all()


def register(client, role, email, password="password123", **extra):
    payload = {
        "name": extra.pop("name", role.title()),
        "email": email,
        "password": password,
        "location": extra.pop("location", "Chennai"),
        "role": role,
        **extra,
    }
    return client.post("/api/register", json=payload)


def login(client, email, password="password123"):
    response = client.post("/api/login", json={"email": email, "password": password})
    assert response.status_code == 200
    return response.get_json()["token"], response.get_json()["user"]


def auth_headers(token):
    return {"Authentication-Token": token}


def test_register_hashes_password_and_login_returns_token(client):
    response = register(client, "customer", "customer@example.com")
    assert response.status_code == 201

    token, user = login(client, "customer@example.com")
    assert token
    assert user["roles"] == ["customer"]


def test_professional_requires_approval_before_login(client):
    response = register(
        client,
        "professional",
        "pro@example.com",
        service="Plumbing",
        experience="4",
    )
    assert response.status_code == 201

    login_response = client.post(
        "/api/login",
        json={"email": "pro@example.com", "password": "password123"},
    )
    assert login_response.status_code == 403


def test_service_mutations_require_admin_token(client):
    response = client.post(
        "/api/add/services",
        json={"name": "Plumbing", "price": 300, "timeRequired": "1 hour"},
    )
    assert response.status_code in {401, 403}


def test_customer_can_create_close_and_review_request(client):
    admin_token, _ = login(client, "admin@example.com", "adminpassword")
    register(client, "customer", "customer@example.com")
    register(
        client,
        "professional",
        "pro@example.com",
        service="Plumbing",
        experience="4",
    )

    professionals = client.get(
        "/api/get/professionals",
        headers=auth_headers(admin_token),
    ).get_json()
    professional = professionals[0]
    admin_token, _ = login(client, "admin@example.com", "adminpassword")
    approval_response = client.put(
        f"/api/update/user/{professional['id']}",
        json={"approved": True},
        headers=auth_headers(admin_token),
    )
    assert approval_response.status_code == 200, approval_response.get_data(as_text=True)
    admin_token, _ = login(client, "admin@example.com", "adminpassword")

    service_response = client.post(
        "/api/add/services",
        json={"name": "Plumbing", "price": 300, "timeRequired": "1 hour"},
        headers=auth_headers(admin_token),
    )
    assert service_response.status_code == 201

    customer_token, _ = login(client, "customer@example.com")
    request_response = client.post(
        "/api/add/service-request",
        json={
            "professionalId": professional["id"],
            "dateOfRequest": "2026-06-01",
            "dateOfCompletion": "2026-06-02",
            "remarks": "Kitchen sink leak",
            "service": "Plumbing",
        },
        headers=auth_headers(customer_token),
    )
    assert request_response.status_code == 201
    service_request = request_response.get_json()["service_request"]

    close_response = client.put(
        f"/api/update/service-request/{service_request['id']}",
        json={"service_status": "closed"},
        headers=auth_headers(customer_token),
    )
    assert close_response.status_code == 200

    review_response = client.post(
        "/api/get/reviews",
        json={
            "service_request_id": service_request["id"],
            "rating": 5,
            "review_text": "Great service",
        },
        headers=auth_headers(customer_token),
    )
    assert review_response.status_code == 201
