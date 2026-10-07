"""Accounts for MangoScan: sign up, log in, password reset and saved scans.

Supabase Auth owns the users. Flask keeps the user's Supabase tokens in its
signed session cookie and talks to Supabase on the user's behalf, sending the
user's access token so Row Level Security decides what each request may touch.
Only the publishable (or legacy anon) key is used here; the secret key is never
needed by this app.
"""
import os
import re
import time
import secrets
from functools import wraps
from urllib.parse import urlsplit
from datetime import datetime, timezone

import ratelimit
from i18n import FIL, t
from flask import (
    Blueprint, abort, current_app, flash, g, redirect, render_template,
    request, session, url_for,
)

bp = Blueprint("accounts", __name__)

BUCKET = "scans"
SIGNED_URL_TTL = 60 * 60  # seconds a photo link stays valid
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
UUID_RE = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")
MIN_PASSWORD = 8
GUEST_CONFIRM_WORD = "guest"  # guests have no name or email to type


# ---------- Supabase client ----------

def _config():
    url = os.environ.get("SUPABASE_URL", "").strip()
    key = (os.environ.get("SUPABASE_PUBLISHABLE_KEY") or os.environ.get("SUPABASE_ANON_KEY") or "").strip()
    return url, key


def enabled():
    url, key = _config()
    return bool(url and key)


def client(access_token=None):
    """A fresh, stateless Supabase client, acting as the user when given their token."""
    from supabase import create_client, ClientOptions

    url, key = _config()
    headers = {"Authorization": f"Bearer {access_token}"} if access_token else {}
    return create_client(url, key, ClientOptions(
        auto_refresh_token=False,
        persist_session=False,
        headers=headers,
    ))


# ---------- Session ----------

def _store_session(sb_session, user=None):
    user = user or sb_session.user
    meta = user.user_metadata or {}
    session["auth"] = {
        "at": sb_session.access_token,
        "rt": sb_session.refresh_token,
        "exp": int(sb_session.expires_at or time.time() + 3600),
        "uid": user.id,
        "email": user.email,
        "name": (meta.get("full_name") or "").strip(),
        "anon": bool(getattr(user, "is_anonymous", False)),
    }
    session.permanent = True


def _clear_session():
    session.pop("auth", None)
    session.pop("upgrade_pending", None)


def _load_user():
    """The signed-in user from the cookie, refreshing the access token when it is about to expire."""
    auth = session.get("auth")
    if not auth or not enabled():
        return None
    if auth.get("exp", 0) - 60 < time.time():
        try:
            res = client().auth.refresh_session(auth["rt"])
        except Exception:
            _clear_session()
            return None
        if not res or not res.session:
            _clear_session()
            return None
        _store_session(res.session, res.user or res.session.user)
        auth = session["auth"]
    return auth


@bp.before_app_request
def _attach_user():
    g.user = _load_user()


@bp.app_context_processor
def _template_globals():
    return {"user": g.get("user"), "accounts_enabled": enabled(), "csrf_token": csrf_token,
            "guest_confirm_word": GUEST_CONFIRM_WORD}


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not g.get("user"):
            return redirect(url_for("accounts.login", next=request.full_path.rstrip("?")))
        return view(*args, **kwargs)
    return wrapped


def _require_enabled():
    if not enabled():
        abort(503, "Accounts are not set up. Add SUPABASE_URL and SUPABASE_PUBLISHABLE_KEY to .env.")


# ---------- CSRF for the account forms ----------

def csrf_token():
    if "_csrf" not in session:
        session["_csrf"] = secrets.token_urlsafe(32)
    return session["_csrf"]


def _check_csrf():
    sent = request.form.get("csrf_token", "")
    if not sent or not secrets.compare_digest(sent, session.get("_csrf", "")):
        abort(400, t("The form expired. Go back, reload the page and try again."))


AUTH_LIMIT = (10, 10 * 60)  # account form submissions per client per 10 minutes


def _too_many():
    """True when this client has sent too many account forms; the caller shows a message."""
    return not ratelimit.allow("auth", *AUTH_LIMIT)


def _safe_next(default="scan"):
    nxt = request.values.get("next", "")
    # Only same-site paths, never another host
    if nxt.startswith("/") and not nxt.startswith("//") and "\\" not in nxt:
        return nxt
    return url_for(default)


# ---------- Error wording ----------

def _auth_message(exc):
    text = str(getattr(exc, "message", "") or exc).lower()
    if "invalid login credentials" in text:
        return t("That email and password do not match. Check them and try again.")
    if "email not confirmed" in text:
        return t("Confirm your email first. Open the link we sent to your inbox.")
    if "already registered" in text or "already been registered" in text:
        return t("An account with this email already exists. Log in instead.")
    if "password" in text and ("weak" in text or "at least" in text or "characters" in text):
        return t("Choose a stronger password: at least {n} characters.", n=MIN_PASSWORD)
    # Supabase waits about a minute before emailing the same address again
    wait = re.search(r"after (\d+) seconds?", text)
    if "security purposes" in text and wait:
        return t("We just sent you an email. Wait {n} seconds before asking for another one.", n=wait.group(1))
    # The project as a whole may only send a few emails an hour
    if "email rate limit" in text:
        return t("We have sent too many emails for now. Try again in an hour.")
    if "rate limit" in text or "too many" in text or "security purposes" in text:
        return t("Too many tries. Wait a minute, then try again.")
    if "expired" in text or ("invalid" in text and "token" in text):
        return t("This link has expired or was already used. Ask for a new one.")
    if "error sending" in text or "not authorized" in text:
        # Supabase could not send the email (its built-in sender only mails the project team)
        current_app.logger.warning("Supabase could not send an email: %s", exc)
        return t("We could not send the email right now. Try again later, or contact the MangoScan team.")
    current_app.logger.warning("Supabase auth error: %s", exc)
    return t("Something went wrong on our side. Try again in a moment.")


# ---------- Sign up, log in, log out ----------

@bp.route("/signup", methods=["GET", "POST"])
def signup():
    _require_enabled()
    if g.user and not g.user.get("anon"):
        return redirect(_safe_next())
    form = {"name": "", "email": ""}
    errors = {}
    is_guest = bool(g.user and g.user.get("anon"))
    if request.method == "POST":
        _check_csrf()
        if _too_many():
            errors["form"] = t("Too many tries. Wait a few minutes, then try again.")
            return render_template("signup.html", form=form, errors=errors), 429
        form["name"] = request.form.get("name", "").strip()
        form["email"] = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        if not form["name"]:
            errors["name"] = t("Enter your name.")
        if not EMAIL_RE.match(form["email"]):
            errors["email"] = t("Enter an email address like name@example.com.")
        if not is_guest and len(password) < MIN_PASSWORD:
            errors["password"] = t("Use at least {n} characters.", n=MIN_PASSWORD)
        if not errors and is_guest:
            try:
                # Same user id, so every guest scan stays with the new account.
                # Supabase sets the password only after the email is confirmed.
                _session_client().auth.update_user(
                    {"email": form["email"], "data": {"full_name": form["name"]}},
                    {"email_redirect_to": url_for("accounts.confirm", _external=True)},
                )
            except Exception as exc:
                errors["form"] = _auth_message(exc)
            else:
                session["upgrade_pending"] = True
                session["pending_email"] = form["email"]
                return redirect(url_for("accounts.check_email"))
        elif not errors:
            try:
                res = client().auth.sign_up({
                    "email": form["email"],
                    "password": password,
                    "options": {
                        "data": {"full_name": form["name"]},
                        "email_redirect_to": url_for("accounts.confirm", _external=True),
                    },
                })
            except Exception as exc:
                errors["form"] = _auth_message(exc)
            else:
                if res.session:
                    _store_session(res.session, res.user)
                    flash(t("Welcome, {name}. Your scans will now be saved.", name=form["name"]))
                    return redirect(_safe_next())
                # Redirect, so reloading the page does not send the form (and another email) again
                session["pending_email"] = form["email"]
                return redirect(url_for("accounts.check_email"))
    return render_template("signup.html", form=form, errors=errors)


@bp.route("/login", methods=["GET", "POST"])
def login():
    _require_enabled()
    if g.user and not g.user.get("anon"):
        return redirect(_safe_next())
    form = {"email": ""}
    errors = {}
    if request.method == "POST":
        _check_csrf()
        form["email"] = request.form.get("email", "").strip().lower()
        if _too_many():
            errors["form"] = t("Too many tries. Wait a few minutes, then try again.")
            return render_template("login.html", form=form, errors=errors), 429
        password = request.form.get("password", "")
        if not EMAIL_RE.match(form["email"]):
            errors["email"] = t("Enter the email you signed up with.")
        if not password:
            errors["password"] = t("Enter your password.")
        if not errors:
            try:
                res = client().auth.sign_in_with_password({"email": form["email"], "password": password})
            except Exception as exc:
                errors["form"] = _auth_message(exc)
                # The account exists but was never confirmed: offer a fresh link
                if "email not confirmed" in str(getattr(exc, "message", "") or exc).lower():
                    return render_template("login.html", form=form, errors=errors, resend_email=form["email"])
            else:
                _store_session(res.session, res.user)
                session.pop("upgrade_pending", None)
                return redirect(_safe_next())
    return render_template("login.html", form=form, errors=errors)


@bp.route("/logout", methods=["POST"])
def logout():
    _check_csrf()
    auth = session.get("auth")
    if auth and enabled():
        try:
            client().auth.admin.sign_out(auth["at"], "local")
        except Exception:
            pass  # the cookie is cleared either way
    _clear_session()
    flash(t("You are logged out."))
    return redirect(url_for("index"))


def _same_site_referrer():
    """The page the visitor came from, only when it is on this site."""
    ref = urlsplit(request.referrer or "")
    return ref.path if ref.netloc == request.host and ref.path.startswith("/") else url_for("index")


@bp.route("/guest", methods=["POST"])
def guest():
    """Start guest mode: an anonymous Supabase user whose scans are saved like an account's."""
    _require_enabled()
    _check_csrf()
    if g.user:
        return redirect(_safe_next())
    if _too_many():
        flash(t("Too many tries. Wait a few minutes, then try again."), "error")
        return redirect(_same_site_referrer())
    try:
        res = client().auth.sign_in_anonymously()
    except Exception as exc:
        # Anonymous sign-ins switched off in Supabase, or its per-IP limit reached
        current_app.logger.warning("Guest sign-in failed: %s", exc)
        flash(t("Guest mode is not available right now. You can still scan without saving, or create an account."), "error")
        return redirect(_same_site_referrer())
    _store_session(res.session, res.user)
    flash(t("You are now a guest. Your scans are saved on this phone's MangoScan."))
    return redirect(_safe_next())


# ---------- Email links and password reset ----------

@bp.route("/forgot", methods=["GET", "POST"])
def forgot():
    _require_enabled()
    form = {"email": request.values.get("email", "").strip().lower()}
    errors = {}
    if request.method == "POST":
        _check_csrf()
        if _too_many():
            errors["form"] = t("Too many tries. Wait a few minutes, then try again.")
            return render_template("forgot.html", form=form, errors=errors), 429
        if not EMAIL_RE.match(form["email"]):
            errors["email"] = t("Enter the email you signed up with.")
        else:
            try:
                client().auth.reset_password_for_email(
                    form["email"], {"redirect_to": url_for("accounts.confirm", _external=True)})
            except Exception as exc:
                current_app.logger.warning("Password reset request failed: %s", exc)
            # Same answer either way, so the page does not reveal which emails have accounts
            return render_template("auth_message.html",
                                   title=t("Check your email"),
                                   heading=t("Check your email."),
                                   body=t("If {email} has an account, we sent a link to set a new password.", email=form["email"]))
    return render_template("forgot.html", form=form, errors=errors)


@bp.route("/auth/resend", methods=["POST"])
def resend():
    """Send the sign-up confirmation link again, for an account that was never confirmed.

    Supabase creates the account at sign-up and keeps it unconfirmed until the link is opened,
    so a lost email is fixed with a new link, not a new account.
    """
    _require_enabled()
    _check_csrf()
    email = request.form.get("email", "").strip().lower()
    if not EMAIL_RE.match(email):
        return redirect(url_for("accounts.signup"))
    session["pending_email"] = email
    if _too_many():
        flash(t("Too many tries. Wait a few minutes, then try again."), "error")
    else:
        try:
            client().auth.resend({
                # A guest adding an email is an email change, not a new sign-up
                "type": "email_change" if session.get("upgrade_pending") else "signup",
                "email": email,
                "options": {"email_redirect_to": url_for("accounts.confirm", _external=True)},
            })
        except Exception as exc:
            flash(_auth_message(exc), "error")
        else:
            flash(t("We sent a new link to {email}. Open the newest email to confirm your account, then log in.", email=email))
    # Redirect, so reloading the page does not ask for another email
    return redirect(url_for("accounts.check_email"))


@bp.route("/auth/check-email")
def check_email():
    """Where sign-up and "send it again" land: tells the user to open the link, with a button to resend."""
    _require_enabled()
    email = session.get("pending_email")
    if not email:
        return redirect(url_for("accounts.signup"))
    return render_template("auth_message.html",
                           title=t("Check your email"),
                           heading=t("Check your email."),
                           body=t("We sent a link to {email}. Open it to confirm your email, then choose a password.", email=email)
                           if session.get("upgrade_pending") else
                           t("We sent a link to {email}. Open it to confirm your account, then log in.", email=email),
                           resend_email=email)


def _store_tokens(access_token, refresh_token, expires_at):
    """Store tokens that arrived through an email link, after Supabase confirms they are real."""
    res = client().auth.get_user(access_token)
    if not res or not res.user:
        raise ValueError("token rejected")
    meta = res.user.user_metadata or {}
    session["auth"] = {
        "at": access_token,
        "rt": refresh_token,
        "exp": expires_at,
        "uid": res.user.id,
        "email": res.user.email,
        "name": (meta.get("full_name") or "").strip(),
        "anon": bool(getattr(res.user, "is_anonymous", False)),
    }
    session.permanent = True


@bp.route("/auth/confirm", methods=["GET", "POST"])
def confirm():
    """Landing page for the links in Supabase's emails (sign-up confirmation and password reset).

    Two link styles arrive here. The recommended email templates send ?token_hash=...&type=...,
    which the server verifies. Supabase's default templates instead put the tokens after '#',
    which only the browser can read, so the page posts them back to this route.
    """
    _require_enabled()
    if request.method == "POST":
        _check_csrf()
        kind = request.form.get("type", "")
        try:
            exp = int(request.form.get("expires_at") or 0) or int(time.time() + 3600)
            _store_tokens(request.form.get("access_token", ""), request.form.get("refresh_token", ""), exp)
        except Exception as exc:
            current_app.logger.warning("Email link tokens rejected: %s", exc)
            return render_template("auth_message.html", title=t("Link not valid"), heading=t("This link does not work."),
                                   body=t("Open the newest email from MangoScan, or ask for a new link.")), 400
        return _after_confirm(kind)

    token_hash = request.args.get("token_hash", "")
    kind = request.args.get("type", "")
    if not token_hash:
        # Default-template links: read the tokens from the address fragment in the browser
        return render_template("auth_fragment.html")
    if kind not in {"signup", "email", "recovery", "invite", "magiclink", "email_change"}:
        return render_template("auth_message.html", title=t("Link not valid"), heading=t("This link does not work."),
                               body=t("Open the newest email from MangoScan, or ask for a new link.")), 400
    try:
        res = client().auth.verify_otp({"token_hash": token_hash, "type": kind})
    except Exception as exc:
        return render_template("auth_message.html", title=t("Link not valid"), heading=t("This link does not work."),
                               body=_auth_message(exc)), 400
    if res.session:
        _store_session(res.session, res.user)
    return _after_confirm(kind)


def _after_confirm(kind):
    """Where an email link leads once its session is stored."""
    if kind == "recovery":
        return redirect(url_for("accounts.reset_password"))
    if session.pop("upgrade_pending", False):
        flash(t("Your email is confirmed. Now choose a password to finish your account."))
        return redirect(url_for("accounts.reset_password"))
    flash(t("Your email is confirmed. Your scans will now be saved."))
    return redirect(url_for("scan"))


@bp.route("/reset-password", methods=["GET", "POST"])
@login_required
def reset_password():
    errors = {}
    if request.method == "POST":
        _check_csrf()
        password = request.form.get("password", "")
        if len(password) < MIN_PASSWORD:
            errors["password"] = t("Use at least {n} characters.", n=MIN_PASSWORD)
        else:
            try:
                _session_client().auth.update_user({"password": password})
            except Exception as exc:
                errors["form"] = _auth_message(exc)
            else:
                flash(t("Your new password is saved."))
                return redirect(url_for("scan"))
    return render_template("reset_password.html", errors=errors)


def _session_client():
    """A client holding the signed-in user's session, for calls that update the user.

    set_session may refresh the tokens, and Supabase rotates refresh tokens, so
    the cookie is updated with whatever session the client ends up holding.
    """
    sb = client()
    res = sb.auth.set_session(g.user["at"], g.user["rt"])
    if res and res.session:
        _store_session(res.session, res.user or res.session.user)
        g.user = session["auth"]
    return sb


# ---------- Settings ----------

def _settings_page(errors=None, name=None, status=200):
    return render_template(
        "settings.html",
        errors=errors or {},
        form={"name": name if name is not None else (g.user or {}).get("name", "")},
    ), status


@bp.route("/settings")
def settings():
    return _settings_page()


@bp.route("/settings/profile", methods=["POST"])
@login_required
def settings_profile():
    _check_csrf()
    name = request.form.get("name", "").strip()
    errors = {}
    if not name:
        errors["name"] = t("Enter your name.")
    elif len(name) > 100:
        errors["name"] = t("Use 100 characters or fewer.")
    if not errors:
        try:
            sb = _session_client()
            res = sb.auth.update_user({"data": {"full_name": name}})
            current = sb.auth.get_session()
            if current:
                _store_session(current, res.user if res else None)
            else:
                session["auth"]["name"] = name
                session.modified = True
        except Exception as exc:
            errors["form_profile"] = _auth_message(exc)
        else:
            flash(t("Your name is saved."))
            return redirect(url_for("accounts.settings"))
    return _settings_page(errors, name, 400)


@bp.route("/settings/password", methods=["POST"])
@login_required
def settings_password():
    _check_csrf()
    errors = {}
    if _too_many():
        errors["form_password"] = t("Too many tries. Wait a few minutes, then try again.")
        return _settings_page(errors, status=429)
    current = request.form.get("current_password", "")
    new = request.form.get("new_password", "")
    if not current:
        errors["current_password"] = t("Enter your current password.")
    if len(new) < MIN_PASSWORD:
        errors["new_password"] = t("Use at least {n} characters.", n=MIN_PASSWORD)
    if not errors:
        try:
            # Proving the current password first stops someone at an unlocked phone from changing it
            sb = client()
            res = sb.auth.sign_in_with_password({"email": g.user["email"], "password": current})
        except Exception:
            errors["current_password"] = t("That password is not right.")
        else:
            try:
                sb.auth.update_user({"password": new})
                _store_session(sb.auth.get_session() or res.session, res.user)
            except Exception as exc:
                errors["form_password"] = _auth_message(exc)
            else:
                flash(t("Your new password is saved."))
                return redirect(url_for("accounts.settings"))
    return _settings_page(errors, status=400)


# ---------- Saved scans ----------

def save_scan(user, token, record, raw_bytes, raw_type, ann_bytes, ann_type):
    """Upload both photos and the reading for a signed-in user. Returns the new scan id, or None."""
    sb = client(user["at"])
    raw_ext = os.path.splitext(record["raw_filename"])[1].lower() or ".jpg"
    ann_ext = os.path.splitext(record["ann_filename"])[1].lower() or ".jpg"
    raw_path = f"{user['uid']}/{token}/original{raw_ext}"
    ann_path = f"{user['uid']}/{token}/marked{ann_ext}"
    try:
        bucket = sb.storage.from_(BUCKET)
        bucket.upload(raw_path, raw_bytes, {"content-type": raw_type})
        bucket.upload(ann_path, ann_bytes, {"content-type": ann_type})
        res = sb.table("scans").insert({
            "user_id": user["uid"],
            "filename": record["filename"],
            "label": record["label"],
            "confidence": record["confidence"],
            "telemetry": record["telemetry"],
            "metrics": record["metrics"],
            "raw_path": raw_path,
            "ann_path": ann_path,
        }).execute()
        return res.data[0]["id"] if res.data else None
    except Exception:
        current_app.logger.exception("Could not save scan to Supabase")
        return None


def _signed_urls(sb, paths):
    paths = [p for p in paths if p]
    if not paths:
        return {}
    try:
        items = sb.storage.from_(BUCKET).create_signed_urls(paths, SIGNED_URL_TTL)
    except Exception:
        current_app.logger.exception("Could not sign photo links")
        return {}
    return {item["path"]: item["signedURL"] for item in items if not item.get("error")}


def _nice_date(value):
    try:
        dt = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return ""
    return dt.astimezone(timezone.utc).strftime("%d %b %Y")


@bp.route("/scans")
@login_required
def scans():
    sb = client(g.user["at"])
    try:
        rows = (sb.table("scans")
                  .select("id, created_at, label, telemetry, ann_path")
                  .order("created_at", desc=True)
                  .limit(100)
                  .execute().data) or []
    except Exception:
        current_app.logger.exception("Could not load scans")
        rows, load_failed = [], True
    else:
        load_failed = False
    urls = _signed_urls(sb, [r.get("ann_path") for r in rows])
    for r in rows:
        r["thumb"] = urls.get(r.get("ann_path"))
        r["date"] = _nice_date(r.get("created_at"))
        r["word"] = (r.get("label") or "").replace("_", " ")
    return render_template("scans.html", rows=rows, load_failed=load_failed)


@bp.route("/scans/<scan_id>")
@login_required
def scan_detail(scan_id):
    if not UUID_RE.match(scan_id):
        abort(404)
    sb = client(g.user["at"])
    try:
        rows = sb.table("scans").select("*").eq("id", scan_id).limit(1).execute().data
    except Exception:
        current_app.logger.exception("Could not load scan")
        rows = []
    if not rows:
        abort(404)
    row = rows[0]
    urls = _signed_urls(sb, [row["raw_path"], row["ann_path"]])
    return render_template(
        "result.html",
        image_url=urls.get(row["raw_path"], ""),
        annotated_url=urls.get(row["ann_path"], ""),
        filename=row.get("filename") or "",
        prediction=row["label"],
        confidence=row.get("confidence"),
        telemetry=row.get("telemetry") or {},
        metrics=row.get("metrics") or {},
        saved_id=row["id"],
        saved_date=_nice_date(row.get("created_at")),
    )


@bp.route("/scans/<scan_id>/delete", methods=["POST"])
@login_required
def scan_delete(scan_id):
    _check_csrf()
    if not UUID_RE.match(scan_id):
        abort(404)
    sb = client(g.user["at"])
    try:
        rows = sb.table("scans").delete().eq("id", scan_id).execute().data or []
        paths = [p for r in rows for p in (r.get("raw_path"), r.get("ann_path")) if p]
        if paths:
            sb.storage.from_(BUCKET).remove(paths)
    except Exception:
        current_app.logger.exception("Could not delete scan")
        flash(t("That scan could not be deleted. Try again."), "error")
        return redirect(url_for("accounts.scan_detail", scan_id=scan_id))
    flash(t("Scan deleted."))
    return redirect(url_for("accounts.scans"))


# ---------- Delete account ----------

def _normalise(text):
    """Spaces trimmed and collapsed, capital letters ignored."""
    return " ".join(text.split()).casefold()


@bp.route("/account/delete", methods=["POST"])
@login_required
def account_delete():
    """Remove the user's account (their scan rows go with it), then their photos."""
    _check_csrf()
    # The user must type their name (or email, when no name is set), like deleting a GitHub repository
    if g.user.get("anon"):
        # The dialog shows the word in the visitor's language; accept either language
        expected = {GUEST_CONFIRM_WORD, FIL[GUEST_CONFIRM_WORD]}
        # The email may have been confirmed on another phone since this cookie was written;
        # then "guest" must not delete what is now a permanent account
        try:
            res = client().auth.get_user(g.user["at"])
            still_guest = bool(res and res.user and res.user.is_anonymous)
        except Exception:
            still_guest = False
        if not still_guest:
            expected = set()
    else:
        expected = {g.user.get("name") or g.user.get("email") or ""}
    if _normalise(request.form.get("confirm", "")) not in {_normalise(w) for w in expected if w}:
        flash(t("What you typed does not match. Your account was not deleted."), "error")
        return redirect(url_for("accounts.settings"))
    sb = client(g.user["at"])
    try:
        # Read the photo paths first: the scan rows are gone once the account is
        rows = sb.table("scans").select("raw_path, ann_path").execute().data or []
        paths = [p for r in rows for p in (r.get("raw_path"), r.get("ann_path")) if p]
        sb.rpc("delete_own_account").execute()
    except Exception:
        current_app.logger.exception("Account deletion failed")
        flash(t("Your account could not be deleted. Try again, or contact the MangoScan team."), "error")
        return redirect(url_for("accounts.settings"))
    # The account is gone, so a photo that fails to delete is only logged; nobody can open it now
    try:
        for i in range(0, len(paths), 100):
            sb.storage.from_(BUCKET).remove(paths[i:i + 100])
    except Exception:
        current_app.logger.exception("Photos left behind after account deletion")
    _clear_session()
    flash(t("Your account and all your saved scans were deleted."))
    return redirect(url_for("index"))


# ---------- Friendly error pages ----------

@bp.app_errorhandler(400)
@bp.app_errorhandler(404)
@bp.app_errorhandler(503)
def _error_page(err):
    headings = {400: "Something was not right.", 404: "Page not found.", 503: "Not available yet."}
    code = getattr(err, "code", 500)
    body = getattr(err, "description", "") if code != 404 else t("The page or scan you asked for does not exist.")
    return render_template("auth_message.html", title=t(headings.get(code, "Something went wrong.")),
                           heading=t(headings.get(code, "Something went wrong.")), body=t(body) if body else ""), code
