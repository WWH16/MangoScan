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


class UpgradeGuestTest(GuestTestCase):
    def test_signup_form_for_guest_has_no_password_field(self):
        self.sign_in(anon=True)
        html = self.client.get("/signup").get_data(as_text=True)
        self.assertIn("Your guest scans move to this account.", html)
        self.assertNotIn('name="password"', html)

    def test_guest_signup_adds_email_to_same_user(self):
        self.sign_in(anon=True)
        self.sb.auth.set_session.return_value = None
        res = self.client.post("/signup", data={"csrf_token": self.csrf(), "name": "Juan", "email": "juan@b.co"})
        self.assertEqual(res.status_code, 302)
        self.assertTrue(res.headers["Location"].endswith("/auth/check-email"))
        args, kwargs = self.sb.auth.update_user.call_args
        self.assertEqual(args[0], {"email": "juan@b.co", "data": {"full_name": "Juan"}})
        self.assertIn("email_redirect_to", args[1])
        self.sb.auth.sign_up.assert_not_called()
        with self.client.session_transaction() as s:
            self.assertTrue(s["upgrade_pending"])
            self.assertEqual(s["auth"]["uid"], "guest-1")

    def test_guest_signup_with_taken_email_keeps_guest(self):
        self.sign_in(anon=True)
        self.sb.auth.set_session.return_value = None
        self.sb.auth.update_user.side_effect = Exception("A user with this email address has already been registered")
        res = self.client.post("/signup", data={"csrf_token": self.csrf(), "name": "Juan", "email": "juan@b.co"})
        self.assertIn("An account with this email already exists. Log in instead.", res.get_data(as_text=True))
        self.assertTrue(self.auth()["anon"])

    def test_confirm_after_upgrade_asks_for_password(self):
        self.sign_in(anon=True)
        with self.client.session_transaction() as s:
            s["upgrade_pending"] = True
        user = FakeUser(email="juan@b.co", anon=False, name="Juan")
        self.sb.auth.verify_otp.return_value = SimpleNamespace(session=fake_session(user), user=user)
        res = self.client.get("/auth/confirm?token_hash=abc&type=email_change")
        self.assertTrue(res.headers["Location"].endswith("/reset-password"))
        self.assertFalse(self.auth()["anon"])
        self.assertEqual(self.auth()["uid"], "guest-1")

    def test_confirm_without_flag_goes_to_scan(self):
        user = FakeUser(email="juan@b.co", anon=False)
        self.sb.auth.verify_otp.return_value = SimpleNamespace(session=fake_session(user), user=user)
        res = self.client.get("/auth/confirm?token_hash=abc&type=email_change")
        self.assertTrue(res.headers["Location"].endswith("/scan"))

    def test_guest_can_open_login_and_is_warned(self):
        self.sign_in(anon=True)
        res = self.client.get("/login")
        self.assertEqual(res.status_code, 200)
        self.assertIn("Your guest scans stay with the guest", res.get_data(as_text=True))


class ReviewFixesTest(GuestTestCase):
    def test_resend_for_upgrading_guest_sends_email_change(self):
        self.sign_in(anon=True)
        with self.client.session_transaction() as s:
            s["upgrade_pending"] = True
        self.client.post("/auth/resend", data={"csrf_token": self.csrf(), "email": "juan@b.co"})
        self.assertEqual(self.sb.auth.resend.call_args[0][0]["type"], "email_change")

    def test_check_email_for_upgrading_guest_says_choose_password(self):
        self.sign_in(anon=True)
        with self.client.session_transaction() as s:
            s["upgrade_pending"] = True
            s["pending_email"] = "juan@b.co"
        html = self.client.get("/auth/check-email").get_data(as_text=True)
        self.assertIn("then choose a password", html)
        self.assertNotIn("then log in", html)

    def test_leaving_guest_mode_clears_upgrade_pending(self):
        self.sign_in(anon=True)
        with self.client.session_transaction() as s:
            s["upgrade_pending"] = True
        self.client.post("/logout", data={"csrf_token": self.csrf()})
        with self.client.session_transaction() as s:
            self.assertNotIn("upgrade_pending", s)

    def test_login_clears_upgrade_pending(self):
        self.sign_in(anon=True)
        with self.client.session_transaction() as s:
            s["upgrade_pending"] = True
        user = FakeUser("u2", "a@b.co", anon=False)
        self.sb.auth.sign_in_with_password.return_value = SimpleNamespace(session=fake_session(user), user=user)
        self.client.post("/login", data={"csrf_token": self.csrf(), "email": "a@b.co", "password": "secret123"})
        with self.client.session_transaction() as s:
            self.assertNotIn("upgrade_pending", s)

    def test_guest_word_cannot_delete_account_upgraded_elsewhere(self):
        # The cookie still says guest, but the email was confirmed on another phone
        self.sign_in(anon=True)
        self.sb.auth.get_user.return_value = SimpleNamespace(user=FakeUser(email="juan@b.co", anon=False))
        self.client.post("/account/delete", data={"csrf_token": self.csrf(), "confirm": "guest"})
        self.sb.rpc.assert_not_called()


class GuestEdgeCasesTest(GuestTestCase):
    """Edge cases around starting, using, upgrading and leaving guest mode."""

    def guest_signin_ok(self):
        self.sb.auth.sign_in_anonymously.return_value = SimpleNamespace(
            session=fake_session(FakeUser()), user=FakeUser())

    # ---------- Starting guest mode ----------

    def test_second_tap_does_not_create_another_guest(self):
        self.sign_in(anon=True)
        res = self.client.post("/guest", data={"csrf_token": self.csrf()})
        self.assertEqual(res.status_code, 302)
        self.sb.auth.sign_in_anonymously.assert_not_called()

    def test_email_user_tapping_guest_stays_signed_in(self):
        self.sign_in(anon=False, email="a@b.co")
        self.client.post("/guest", data={"csrf_token": self.csrf()})
        self.sb.auth.sign_in_anonymously.assert_not_called()
        self.assertFalse(self.auth()["anon"])

    def test_rate_limited_guest_start_calls_nothing(self):
        with mock.patch("ratelimit.allow", return_value=False):
            res = self.client.post("/guest", data={"csrf_token": self.csrf()}, follow_redirects=True)
        self.sb.auth.sign_in_anonymously.assert_not_called()
        self.assertIn("Too many tries.", res.get_data(as_text=True))
        self.assertIsNone(self.auth())

    def test_guest_get_does_not_start_guest(self):
        res = self.client.get("/guest")
        self.assertEqual(res.status_code, 302)  # the app turns 405 into a redirect to /scan
        self.sb.auth.sign_in_anonymously.assert_not_called()

    def test_guest_without_supabase_config_is_unavailable(self):
        with mock.patch.dict(os.environ, {"SUPABASE_URL": ""}):
            res = self.client.post("/guest", data={"csrf_token": self.csrf()})
            self.assertEqual(res.status_code, 503)
            self.assertNotIn('class="guest-form', self.client.get("/").get_data(as_text=True))
        self.sb.auth.sign_in_anonymously.assert_not_called()

    def test_guest_honours_same_site_next(self):
        self.guest_signin_ok()
        res = self.client.post("/guest?next=/scans", data={"csrf_token": self.csrf()})
        self.assertTrue(res.headers["Location"].endswith("/scans"))

    def test_guest_ignores_next_to_another_site(self):
        self.guest_signin_ok()
        for bad in ("//evil.example", "https://evil.example", "/\\evil.example"):
            res = self.client.post("/guest", query_string={"next": bad}, data={"csrf_token": self.csrf()})
            self.assertTrue(res.headers["Location"].endswith("/scan"), bad)
            with self.client.session_transaction() as s:
                s.pop("auth", None)

    def test_failed_guest_start_never_redirects_off_site(self):
        self.sb.auth.sign_in_anonymously.side_effect = Exception("disabled")
        res = self.client.post("/guest", data={"csrf_token": self.csrf()},
                               headers={"Referer": "https://evil.example/phish"})
        self.assertNotIn("evil.example", res.headers["Location"])

    def test_failed_guest_start_returns_to_same_site_page(self):
        self.sb.auth.sign_in_anonymously.side_effect = Exception("disabled")
        res = self.client.post("/guest", data={"csrf_token": self.csrf()},
                               headers={"Referer": "http://localhost/login"})
        self.assertTrue(res.headers["Location"].endswith("/login"))

    # ---------- Using guest mode ----------

    def test_guest_scan_is_saved_to_guest_account(self):
        import io
        import cv2
        import numpy as np
        self.sign_in(anon=True)
        img = np.full((64, 64, 3), 120, np.uint8)
        jpg = cv2.imencode(".jpg", img)[1].tobytes()
        scan_id = "11111111-1111-1111-1111-111111111111"
        with mock.patch("models.inference.overlay_mask", return_value=np.ones((64, 64), np.uint8)), \
             mock.patch("models.inference.check_photo", return_value=None), \
             mock.patch("models.inference.predict", return_value=("Healthy", 0.9)), \
             mock.patch("models.inference.generate_detection_overlay", return_value=(img, {}, {})), \
             mock.patch("accounts.save_scan", return_value=scan_id) as save:
            res = self.client.post("/predict", data={"image": (io.BytesIO(jpg), "m.jpg")},
                                   content_type="multipart/form-data")
        self.assertEqual(save.call_args[0][0]["uid"], "guest-1")
        self.assertTrue(res.headers["Location"].endswith("/scans/" + scan_id))

    def test_header_shows_my_scans_for_guest(self):
        self.sign_in(anon=True)
        html = self.client.get("/scan").get_data(as_text=True)
        self.assertIn('href="/scans"', html)
        self.assertNotIn('href="/login" class="nav-link"', html)

    def test_token_refresh_keeps_guest_flag(self):
        with self.client.session_transaction() as s:
            s["auth"] = {"at": "old", "rt": "rt", "exp": 0, "uid": "guest-1", "email": None, "name": "", "anon": True}
        self.sb.auth.refresh_session.return_value = SimpleNamespace(
            session=fake_session(FakeUser()), user=FakeUser())
        self.client.get("/settings")
        self.assertTrue(self.auth()["anon"])
        self.assertEqual(self.auth()["at"], "at")

    def test_old_cookie_without_anon_key_is_an_email_user(self):
        with self.client.session_transaction() as s:
            s["auth"] = {"at": "at", "rt": "rt", "exp": int(time.time()) + 3600,
                         "uid": "u1", "email": "a@b.co", "name": "Juan"}
        html = self.client.get("/settings").get_data(as_text=True)
        self.assertIn("Log out", html)
        self.assertNotIn("Leave guest mode", html)
        self.client.post("/account/delete", data={"csrf_token": self.csrf(), "confirm": "guest"})
        self.sb.rpc.assert_not_called()

    def test_guest_delete_refused_when_supabase_unreachable(self):
        self.sign_in(anon=True)
        self.sb.auth.get_user.side_effect = Exception("network down")
        self.client.post("/account/delete", data={"csrf_token": self.csrf(), "confirm": "guest"})
        self.sb.rpc.assert_not_called()
        self.assertIsNotNone(self.auth())

    def test_guest_cannot_change_password(self):
        self.sign_in(anon=True)
        # A guest has no email, so Supabase refuses the password check
        self.sb.auth.sign_in_with_password.side_effect = Exception("missing email")
        self.client.post("/settings/password", data={"csrf_token": self.csrf(),
                                                      "current_password": "x" * 8, "new_password": "y" * 8})
        self.sb.auth.update_user.assert_not_called()

    # ---------- Upgrading ----------

    def test_guest_signup_validates_name_and_email(self):
        self.sign_in(anon=True)
        for data in ({"name": "", "email": "juan@b.co"}, {"name": "Juan", "email": "not-an-email"}):
            res = self.client.post("/signup", data={"csrf_token": self.csrf(), **data})
            self.assertEqual(res.status_code, 200, data)
        self.sb.auth.update_user.assert_not_called()

    def test_guest_signup_ignores_posted_password(self):
        self.sign_in(anon=True)
        self.sb.auth.set_session.return_value = None
        self.client.post("/signup", data={"csrf_token": self.csrf(), "name": "Juan",
                                           "email": "juan@b.co", "password": "x"})
        self.assertNotIn("password", self.sb.auth.update_user.call_args[0][0])

    def test_guest_signup_normalises_email(self):
        self.sign_in(anon=True)
        self.sb.auth.set_session.return_value = None
        self.client.post("/signup", data={"csrf_token": self.csrf(), "name": " Juan ", "email": "  Juan@B.Co "})
        self.assertEqual(self.sb.auth.update_user.call_args[0][0],
                         {"email": "juan@b.co", "data": {"full_name": "Juan"}})

    def test_guest_signup_rate_limited(self):
        self.sign_in(anon=True)
        with mock.patch("ratelimit.allow", return_value=False):
            res = self.client.post("/signup", data={"csrf_token": self.csrf(), "name": "Juan", "email": "juan@b.co"})
        self.assertEqual(res.status_code, 429)
        self.sb.auth.update_user.assert_not_called()

    def test_guest_signup_needs_csrf(self):
        self.sign_in(anon=True)
        res = self.client.post("/signup", data={"name": "Juan", "email": "juan@b.co"})
        self.assertEqual(res.status_code, 400)
        self.sb.auth.update_user.assert_not_called()

    def test_recovery_link_is_not_hijacked_by_pending_upgrade(self):
        self.sign_in(anon=False, email="juan@b.co")
        with self.client.session_transaction() as s:
            s["upgrade_pending"] = True
        user = FakeUser(email="juan@b.co", anon=False)
        self.sb.auth.verify_otp.return_value = SimpleNamespace(session=fake_session(user), user=user)
        res = self.client.get("/auth/confirm?token_hash=abc&type=recovery")
        self.assertTrue(res.headers["Location"].endswith("/reset-password"))

    def test_bad_confirm_link_keeps_guest_and_pending_upgrade(self):
        self.sign_in(anon=True)
        with self.client.session_transaction() as s:
            s["upgrade_pending"] = True
        self.sb.auth.verify_otp.side_effect = Exception("Token has expired or is invalid")
        res = self.client.get("/auth/confirm?token_hash=abc&type=email_change")
        self.assertEqual(res.status_code, 400)
        self.assertTrue(self.auth()["anon"])
        with self.client.session_transaction() as s:
            self.assertTrue(s["upgrade_pending"])  # a fresh link still finishes the upgrade

    # ---------- Language ----------

    def test_guest_screens_in_filipino(self):
        self.client.set_cookie("lang", "fil")
        html = self.client.get("/").get_data(as_text=True)
        self.assertIn("Magpatuloy bilang bisita", html)
        self.assertNotIn("Continue as guest", html)
        self.sign_in(anon=True)
        html = self.client.get("/settings").get_data(as_text=True)
        self.assertIn("Umalis sa guest mode", html)
        self.assertNotIn("Leave guest mode", html)


class MinorFixesTest(GuestTestCase):
    def guest_settings(self):
        self.sign_in(anon=True)
        return self.client.get("/settings").get_data(as_text=True)

    def test_guest_button_keeps_next_page(self):
        html = self.client.get("/login?next=/scans").get_data(as_text=True)
        self.assertIn('action="/guest?next=/scans"', html)

    def test_guest_delete_dialog_talks_about_guest_scans(self):
        html = self.guest_settings()
        self.assertIn("Delete your guest scans?", html)
        self.assertNotIn("Delete your account?", html)

    def test_email_user_delete_dialog_unchanged(self):
        self.sign_in(anon=False, email="a@b.co", name="Juan")
        html = self.client.get("/settings").get_data(as_text=True)
        self.assertIn("Delete your account?", html)
        self.assertNotIn('id="leave-dialog"', html)

    def test_filipino_guest_types_bisita(self):
        self.client.set_cookie("lang", "fil")
        self.assertIn('data-expect="bisita"', self.guest_settings())
        self.sb.table.return_value.select.return_value.execute.return_value = SimpleNamespace(data=[])
        self.client.post("/account/delete", data={"csrf_token": self.csrf(), "confirm": " Bisita "})
        self.sb.rpc.assert_called_once_with("delete_own_account")

    def test_english_word_still_works_after_switching_language(self):
        self.client.set_cookie("lang", "fil")
        self.sign_in(anon=True)
        self.sb.table.return_value.select.return_value.execute.return_value = SimpleNamespace(data=[])
        self.client.post("/account/delete", data={"csrf_token": self.csrf(), "confirm": "guest"})
        self.sb.rpc.assert_called_once_with("delete_own_account")

    def test_guest_delete_still_rejects_empty_and_wrong_words(self):
        self.sign_in(anon=True)
        for word in ("", "bisita guest", "account"):
            self.client.post("/account/delete", data={"csrf_token": self.csrf(), "confirm": word})
        self.sb.rpc.assert_not_called()

    def test_reset_password_never_shows_none(self):
        self.sign_in(anon=True)
        html = self.client.get("/reset-password").get_data(as_text=True)
        self.assertNotIn("For None.", html)

    def test_leave_guest_mode_asks_first(self):
        html = self.guest_settings()
        self.assertIn('id="leave-dialog"', html)
        self.assertIn("Leave guest mode?", html)
        # Without JavaScript the plain form still posts to /logout
        self.assertIn('id="leave-form" method="POST" action="/logout"', html)


if __name__ == "__main__":
    unittest.main()
