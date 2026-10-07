"""Guest mode: anonymous Supabase users who keep a scan history.

Run from the repository root:
    ./venv/Scripts/python.exe -m unittest tests.test_guest_mode -v
"""
import os
import time
import unittest
from types import SimpleNamespace
from unittest import mock

from app import app

SUPABASE_ENV = {"SUPABASE_URL": "https://example.supabase.co", "SUPABASE_PUBLISHABLE_KEY": "test-key"}


def FakeUser(uid="guest-1", email=None, anon=True, name=""):
    return SimpleNamespace(id=uid, email=email, is_anonymous=anon, user_metadata={"full_name": name} if name else {})


def fake_session(user):
    return SimpleNamespace(access_token="at", refresh_token="rt", expires_at=int(time.time()) + 3600, user=user)


class GuestTestCase(unittest.TestCase):
    def setUp(self):
        env = mock.patch.dict(os.environ, SUPABASE_ENV)
        env.start()
        self.addCleanup(env.stop)
        app.config["TESTING"] = True
        self.client = app.test_client()
        self.sb = mock.MagicMock()
        patcher = mock.patch("accounts.client", return_value=self.sb)
        patcher.start()
        self.addCleanup(patcher.stop)
        # The rate limiter keeps counts in memory across tests; let every test through
        limit = mock.patch("ratelimit.allow", return_value=True)
        limit.start()
        self.addCleanup(limit.stop)

    def csrf(self):
        with self.client.session_transaction() as s:
            s["_csrf"] = "tok"
        return "tok"

    def sign_in(self, anon=True, email=None, name=""):
        with self.client.session_transaction() as s:
            s["auth"] = {"at": "at", "rt": "rt", "exp": int(time.time()) + 3600, "uid": "guest-1",
                         "email": email, "name": name, "anon": anon}

    def auth(self):
        with self.client.session_transaction() as s:
            return s.get("auth")


class StartGuestTest(GuestTestCase):
    def test_continue_as_guest_creates_anonymous_session(self):
        self.sb.auth.sign_in_anonymously.return_value = SimpleNamespace(
            session=fake_session(FakeUser()), user=FakeUser())
        res = self.client.post("/guest", data={"csrf_token": self.csrf()})
        self.assertEqual(res.status_code, 302)
        self.assertTrue(res.headers["Location"].endswith("/scan"))
        auth = self.auth()
        self.assertTrue(auth["anon"])
        self.assertEqual(auth["uid"], "guest-1")

    def test_guest_needs_csrf(self):
        res = self.client.post("/guest", data={})
        self.assertEqual(res.status_code, 400)
        self.sb.auth.sign_in_anonymously.assert_not_called()

    def test_supabase_refusal_keeps_visitor_signed_out(self):
        self.sb.auth.sign_in_anonymously.side_effect = Exception("Anonymous sign-ins are disabled")
        res = self.client.post("/guest", data={"csrf_token": self.csrf()}, follow_redirects=True)
        self.assertIn("Guest mode is not available right now.", res.get_data(as_text=True))
        self.assertIsNone(self.auth())

    def test_email_login_is_not_anonymous(self):
        self.sb.auth.sign_in_with_password.return_value = SimpleNamespace(
            session=fake_session(FakeUser("u2", "a@b.co", anon=False)), user=FakeUser("u2", "a@b.co", anon=False))
        self.client.post("/login", data={"csrf_token": self.csrf(), "email": "a@b.co", "password": "secret123"})
        self.assertFalse(self.auth()["anon"])

    def test_entry_buttons_on_login_signup_and_landing(self):
        for path in ("/login", "/signup", "/"):
            html = self.client.get(path).get_data(as_text=True)
            self.assertIn("Continue as guest", html, path)
            self.assertIn('action="/guest"', html, path)


class GuestSettingsTest(GuestTestCase):
    def test_guest_delete_rejects_empty_confirm(self):
        self.sign_in(anon=True)
        self.client.post("/account/delete", data={"csrf_token": self.csrf(), "confirm": ""})
        self.sb.rpc.assert_not_called()
        self.assertIsNotNone(self.auth())

    def test_guest_delete_accepts_guest_word(self):
        self.sign_in(anon=True)
        self.sb.table.return_value.select.return_value.execute.return_value = SimpleNamespace(data=[])
        self.client.post("/account/delete", data={"csrf_token": self.csrf(), "confirm": " Guest "})
        self.sb.rpc.assert_called_once_with("delete_own_account")
        self.assertIsNone(self.auth())

    def test_settings_for_guest(self):
        self.sign_in(anon=True)
        html = self.client.get("/settings").get_data(as_text=True)
        self.assertIn("Leave guest mode", html)
        self.assertIn("Your guest scans will be lost", html)
        self.assertIn("Create account", html)
        self.assertNotIn("Change password", html)
        self.assertIn('data-expect="guest"', html)

    def test_settings_for_email_user_unchanged(self):
        self.sign_in(anon=False, email="a@b.co", name="Juan")
        html = self.client.get("/settings").get_data(as_text=True)
        self.assertIn("Log out", html)
        self.assertNotIn("Leave guest mode", html)
        self.assertIn('data-expect="Juan"', html)

    def test_scans_page_tells_guest_to_create_account(self):
        self.sign_in(anon=True)
        q = self.sb.table.return_value.select.return_value.order.return_value.limit.return_value
        q.execute.return_value = SimpleNamespace(data=[])
        html = self.client.get("/scans").get_data(as_text=True)
        self.assertIn("You are using MangoScan as a guest.", html)


if __name__ == "__main__":
    unittest.main()
