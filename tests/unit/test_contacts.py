"""Tests for the contacts module."""

import pytest
from app import create_app, db
from app.modules.contacts.models import Contact, ContactList
from app.modules.contacts.services import ContactImportService, normalize_phone


@pytest.fixture
def app():
    app = create_app("testing")
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def user(app):
    from app.modules.auth.models import User

    u = User(email="test@test.com", name="Test User", role="admin")
    u.set_password("password")
    db.session.add(u)
    db.session.commit()
    return u


@pytest.fixture
def logged_in(client, user):
    client.post(
        "/auth/login",
        data={"email": "test@test.com", "password": "password"},
        follow_redirects=True,
    )
    return client


class TestNormalizePhone:
    def test_valid_e164(self):
        assert normalize_phone("+15551234567") == "+15551234567"

    def test_us_number_with_parens(self):
        assert normalize_phone("(555) 123-4567") == "+15551234567"

    def test_us_number_with_dashes(self):
        assert normalize_phone("555-123-4567") == "+15551234567"

    def test_invalid_returns_none(self):
        assert normalize_phone("not-a-phone") is None

    def test_empty_returns_none(self):
        assert normalize_phone("") is None


class TestContactListCRUD:
    def test_create_list(self, logged_in):
        resp = logged_in.post(
            "/api/contacts/lists",
            json={"name": "My List"},
        )
        assert resp.status_code == 201
        data = resp.get_json()
        assert data["name"] == "My List"
        assert data["status"] == "uploaded"

    def test_list_lists(self, logged_in, user):
        cl = ContactList(name="Existing", created_by=user.id)
        db.session.add(cl)
        db.session.commit()

        resp = logged_in.get("/api/contacts/lists")
        assert resp.status_code == 200
        data = resp.get_json()
        assert len(data) == 1
        assert data[0]["name"] == "Existing"


class TestContactImportService:
    def test_parse_txt(self, tmp_path):
        f = tmp_path / "numbers.txt"
        f.write_text("+15551234567\n+15559876543\n")
        numbers = ContactImportService.parse_file(str(f), "txt")
        assert len(numbers) == 2
        assert "+15551234567" in numbers

    def test_parse_csv(self, tmp_path):
        f = tmp_path / "contacts.csv"
        f.write_text("phone,name\n+15551234567,John\n+15559876543,Jane\n")
        numbers = ContactImportService.parse_file(str(f), "csv")
        assert len(numbers) == 2

    def test_parse_xlsx(self, tmp_path):
        from openpyxl import Workbook

        wb = Workbook()
        ws = wb.active
        ws.append(["phone", "name"])
        ws.append(["+15551234567", "John"])
        ws.append(["+15559876543", "Jane"])
        f = tmp_path / "contacts.xlsx"
        wb.save(str(f))
        wb.close()
        numbers = ContactImportService.parse_file(str(f), "xlsx")
        assert len(numbers) == 2

    def test_process_dedupes(self, app):
        raw = ["+15551234567", "+15551234567", "+15559876543"]
        stats, contacts = ContactImportService.process(raw, 1, 1)
        assert stats["loaded"] == 3
        assert stats["duplicates"] == 1
        assert stats["remaining"] == 2

    def test_process_invalid_numbers(self, app):
        raw = ["not-a-phone", "+15551234567"]
        stats, contacts = ContactImportService.process(raw, 1, 1)
        assert stats["invalid"] == 1
        assert stats["remaining"] == 1

    def test_commit_contacts(self, app):
        cl = ContactList(name="Test", created_by=1)
        db.session.add(cl)
        db.session.commit()
        contacts = [
            Contact(contact_list_id=cl.id, phone="+15551234567"),
            Contact(contact_list_id=cl.id, phone="+15559876543"),
        ]
        count = ContactImportService.commit_contacts(cl.id, contacts)
        assert count == 2
        assert Contact.query.filter_by(contact_list_id=cl.id).count() == 2
