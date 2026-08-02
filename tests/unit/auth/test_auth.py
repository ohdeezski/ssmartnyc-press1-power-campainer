def test_login_page(client):
    response = client.get("/auth/login")
    assert response.status_code == 200
    assert b"Log In" in response.data


def test_dashboard_requires_login(client):
    response = client.get("/")
    assert response.status_code in (302, 401, 403)
