import pytest

from app import create_app
from app.extensions import db
from app.services.user_service import UserService
from app.models.user import User


@pytest.fixture
def app():
    app = create_app("testing")
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def session(app):
    with app.app_context():
        yield db.session


def test_create_and_get_user(session):
    user = UserService.create_user(name="Test User", email="test@example.com")
    assert user.id is not None

    fetched = UserService.get_user_by_id(user.id)
    assert fetched.email == "test@example.com"


def test_update_user(session):
    user = UserService.create_user(name="Old", email="old@example.com")
    updated = UserService.update_user(user.id, name="New Name")
    assert updated.name == "New Name"


def test_soft_delete_user(session):
    user = UserService.create_user(name="ToDelete", email="del@example.com")
    UserService.delete_user(user.id, soft_delete=True)
    assert User.find_by_id(user.id) is None
    # В БД запись осталась, но is_active = False
    db_user = User.query.filter_by(id=user.id).first()
    assert db_user is not None
    assert db_user.is_active is False
