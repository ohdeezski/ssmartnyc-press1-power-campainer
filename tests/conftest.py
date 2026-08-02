import pytest

from app import create_app
from app import db as _db
from app.modules.auth.models import User


@pytest.fixture
def app():
    app = create_app("testing")
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["WTF_CSRF_ENABLED"] = False
    with app.app_context():
        _db.create_all()
        yield app
        _db.session.remove()
        _db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def auth_client(client):
    with client.application.app_context():
        user = User(email="test@test.com", name="Test User", role="admin")
        user.set_password("testpassword")
        _db.session.add(user)
        _db.session.commit()
    return client


@pytest.fixture
def test_client(client):
    """Alias of `client` for tests written against the legacy fixture name."""
    return client


@pytest.fixture
def auth_user(client):
    """Create an admin user and log them in. Returns the logged-in client."""
    with client.application.app_context():
        user = User(email="test@test.com", name="Test User", role="admin")
        user.set_password("testpassword")
        _db.session.add(user)
        _db.session.commit()
    client.post(
        "/auth/login",
        data={
            "email": "test@test.com",
            "password": "testpassword",
        },
    )
    return client


@pytest.fixture
def test_admin_user(client):
    """Create a second admin user (not logged in). Returns the user's id."""
    with client.application.app_context():
        user = User(email="admin@test.com", name="Admin User", role="admin")
        user.set_password("adminpassword")
        _db.session.add(user)
        _db.session.commit()
        return user.id
