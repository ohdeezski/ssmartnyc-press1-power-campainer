"""Light load smoke: the health endpoint stays responsive under concurrency.

This is intentionally a fractional load test (small thread count, in-memory
DB) so it is safe in CI without live infrastructure. Scale assertions are
kept loose to avoid flaky gates on shared runners.
"""

from concurrent.futures import ThreadPoolExecutor

from app.extensions import db
from app.modules.auth.models import User


def _seed_user(app):
    with app.app_context():
        user = User(email="load@example.com", name="Load", role="admin")
        user.set_password("testpassword123")
        db.session.add(user)
        db.session.commit()


def test_concurrent_health_requests(client, app):
    _seed_user(app)

    def hit(_):
        return client.get("/api/health").status_code

    with ThreadPoolExecutor(max_workers=8) as pool:
        codes = list(pool.map(hit, range(24)))

    assert codes == [200] * 24


def test_authenticated_dashboard_stays_responsive(client, app):
    """Sequential dashboard renders stay 200 after login.

    Deliberately sequential: threaded requests against the in-memory test
    DB corrupt visibility of the session-scoped Notification count, and the
    goal here is a load/shape smoke, not a SQLite thread race.
    """
    _seed_user(app)
    client.post(
        "/auth/login",
        data={"email": "load@example.com", "password": "testpassword123"},
        follow_redirects=True,
    )

    codes = [client.get("/").status_code for _ in range(12)]

    assert all(code == 200 for code in codes)
