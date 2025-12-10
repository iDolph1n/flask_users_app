import pytest

from app import create_app
from app.extensions import db


@pytest.fixture
def client():
    app = create_app("testing")
    with app.app_context():
        db.create_all()
        yield app.test_client()
        db.session.remove()
        db.drop_all()


def test_create_user_endpoint(client):
    resp = client.post(
        "/api/users",
        json={"name": "Api User", "email": "api@example.com"},
    )
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["success"] is True
    assert data["data"]["email"] == "api@example.com"


def test_get_users_endpoint(client):
    # Сначала создадим пользователя
    client.post(
        "/api/users",
        json={"name": "Api User", "email": "api2@example.com"},
    )

    resp = client.get("/api/users")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["success"] is True
    assert isinstance(data["data"], list)
    assert len(data["data"]) >= 1
