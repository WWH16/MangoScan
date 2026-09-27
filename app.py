import os
import uuid
import mimetypes
import base64
import socket
import binascii
from datetime import timedelta
from flask import Flask, render_template, request, url_for, redirect, g, send_from_directory
from werkzeug.utils import secure_filename

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
mimetypes.add_type("application/manifest+json", ".webmanifest")

# Local settings (Supabase keys, secret key) live in .env; on Vercel they come from the project settings
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(BASE_DIR, ".env"))
except ImportError:
    pass

import accounts
import i18n
import ratelimit
from i18n import t

# Vercel serverless has a read-only filesystem; writable scratch is in /tmp
IS_VERCEL = bool(os.environ.get("VERCEL"))

app = Flask(__name__)
if IS_VERCEL:
    # Vercel terminates HTTPS at its proxy; trust its forwarded headers so
    # external links (email confirmation redirects) are built as https://<domain>
    from werkzeug.middleware.proxy_fix import ProxyFix
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)

# The session cookie carries the user's login, so the signing key must be secret and stable
secret_key = os.environ.get("MANGOSCAN_SECRET_KEY", "").strip()
if not secret_key:
    if IS_VERCEL:
        raise RuntimeError("Set MANGOSCAN_SECRET_KEY in the Vercel project's environment variables.")
    secret_key = "dev-only-insecure-key-set-MANGOSCAN_SECRET_KEY"
app.secret_key = secret_key
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=IS_VERCEL,
    PERMANENT_SESSION_LIFETIME=timedelta(days=30),
)
app.register_blueprint(accounts.bp)
app.register_blueprint(i18n.bp)

# 10 MB maximum upload limit (phones shrink photos before upload, so real uploads are far smaller)
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}
SCAN_LIMIT = (20, 10 * 60)      # scans per client per 10 minutes
DISPLAY_MAX_SIDE = 1280         # result photos are shown at most this large

PHOTO_PROBLEMS = {
    "no_fruit": "We could not find a mango in this photo. Take a closer photo of one fruit on a plain background.",
    "blurry": "This photo is too blurry. Hold the phone still and tap the mango to focus, then try again.",
    "dark": "This photo is too dark. Move to brighter light and try again.",
    "bright": "This photo is too bright. Move out of direct glare and try again.",
}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def error_response(message, status):
    """Show the scan page again with the message, in the visitor's language."""
    return render_template("upload.html", error=t(message)), status


def _data_url(image_bgr):
    """Encode an image as a JPEG data URL, shrunk to the display size."""
    import base64 as b64
    import cv2

    h, w = image_bgr.shape[:2]
    scale = min(1.0, DISPLAY_MAX_SIDE / max(h, w))
    if scale < 1.0:
        image_bgr = cv2.resize(image_bgr, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_AREA)
    ok, buf = cv2.imencode(".jpg", image_bgr, [cv2.IMWRITE_JPEG_QUALITY, 85])
    return "data:image/jpeg;base64," + b64.b64encode(buf.tobytes()).decode("ascii") if ok else ""


@app.route("/")
def index():
    # Supabase falls back to the site root when an email link's redirect is not allowed
    if request.args.get("token_hash"):
        return redirect(url_for("accounts.confirm", **request.args))
    return render_template("upload.html")


@app.route("/predict", methods=["GET", "POST"])
def predict():
    if request.method == "GET":
        return redirect(url_for("index"))
    if not ratelimit.allow("scan", *SCAN_LIMIT):
        return error_response("You have scanned a lot in a short time. Wait a few minutes, then try again.", 429)

    file_bytes = None
    original_filename = "camera_scan.jpg"

    # Live camera capture arrives as a base64 data URL in a form field
    b64_data = request.form.get("image_base64", "")
    if b64_data:
        if "," in b64_data:
            b64_data = b64_data.split(",", 1)[1]
        try:
            file_bytes = base64.b64decode(b64_data, validate=True)
        except (binascii.Error, ValueError):
            return error_response("The camera photo could not be read. Try again.", 400)

    # Standard file upload or direct camera capture
    elif "image" in request.files or "image_camera" in request.files:
        file = None
        for key in ("image", "image_camera"):
            candidate = request.files.get(key)
            if candidate and candidate.filename:
                file = candidate
                break

        if not file:
            return error_response("No photo selected. Take or choose a photo of one mango.", 400)
        if not allowed_file(file.filename):
            return error_response("That file type is not supported. Use a JPG, PNG or WEBP photo.", 400)

        file_bytes = file.read()
        # secure_filename can strip everything (e.g. non-ASCII names); keep the extension
        ext = file.filename.rsplit(".", 1)[1].lower()
        original_filename = secure_filename(file.filename) or f"upload.{ext}"

    else:
        return error_response("Take or choose a photo of one mango first.", 400)

    import cv2
    import numpy as np

    np_arr = np.frombuffer(file_bytes, np.uint8)
    image_bgr = cv2.imdecode(np_arr, cv2.IMREAD_COLOR) if np_arr.size else None
    if image_bgr is None:
        return error_response("This file could not be opened as a photo. Choose another one.", 400)

    try:
        from models import inference
        # Segment at display resolution first: the photo check needs the fruit
        # outline, and the boxes and percentages are measured against it
        mask = inference.overlay_mask(image_bgr)
        problem = inference.check_photo(image_bgr, mask)
        if problem:
            return error_response(PHOTO_PROBLEMS[problem], 422)
        label, confidence = inference.predict(image_bgr)
        annotated_bgr, telemetry, metrics = inference.generate_detection_overlay(image_bgr, label, mask=mask)
    except FileNotFoundError as e:
        app.logger.error("Model files missing: %s", e)
        return error_response("MangoScan is not set up correctly: the model files are missing.", 500)
    except Exception:
        app.logger.exception("Diagnosis failed")
        return error_response("Something went wrong while checking this photo. Try again.", 500)

    record = {
        "filename": original_filename,
        "raw_filename": original_filename,
        "ann_filename": os.path.splitext(original_filename)[0] + ".jpg",
        "label": str(label),
        "confidence": confidence,
        "telemetry": telemetry,
        "metrics": metrics,
    }

    # Signed-in users get the scan saved to their account and land on the saved copy
    if g.get("user"):
        ok, encoded = cv2.imencode(".jpg", annotated_bgr, [cv2.IMWRITE_JPEG_QUALITY, 90])
        mime = {".png": "image/png", ".webp": "image/webp"}
        raw_type = mime.get(os.path.splitext(original_filename)[1].lower(), "image/jpeg")
        saved_id = accounts.save_scan(g.user, uuid.uuid4().hex[:8], record,
                                      file_bytes, raw_type, encoded.tobytes(), "image/jpeg") if ok else None
        if saved_id:
            return redirect(url_for("accounts.scan_detail", scan_id=saved_id))

    # Everyone else sees the result straight away. Nothing is written to disk,
    # so the page works on Vercel, where the next request may land on a
    # different server with an empty /tmp.
    return render_template(
        "result.html",
        image_url=_data_url(image_bgr),
        annotated_url=_data_url(annotated_bgr),
        filename=original_filename,
        prediction=record["label"],
        confidence=confidence,
        telemetry=telemetry,
        metrics=metrics,
    )


# ---------- Install to home screen (PWA) ----------

@app.route("/sw.js")
def service_worker():
    # Served from the site root so it may control every page
    resp = send_from_directory(os.path.join(BASE_DIR, "static"), "sw.js", mimetype="application/javascript")
    resp.headers["Cache-Control"] = "no-cache"
    return resp


@app.route("/offline")
def offline():
    return render_template("offline.html")


@app.errorhandler(405)
def method_not_allowed(error):
    return redirect(url_for("index"))


@app.errorhandler(413)
def request_entity_too_large(error):
    return error_response("That photo is too large (over 10 MB). Choose a smaller one or take a new photo.", 413)


def lan_ip():
    """Best-effort local network address, for the phone access hint."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("10.255.255.255", 1))  # no packets sent for UDP connect
            return s.getsockname()[0]
    except OSError:
        return "<your-PC-IP>"


if __name__ == "__main__":
    import sys
    use_ssl = "--ssl" in sys.argv
    # Werkzeug debugger allows code execution; never expose it on the LAN by default
    debug = "--debug" in sys.argv or os.environ.get("FLASK_DEBUG") == "1"
    host = "127.0.0.1" if debug else "0.0.0.0"
    scheme = "https" if use_ssl else "http"

    print("\n" + "=" * 60)
    print(f"  MangoScan running in {scheme.upper()} Mode" + (" (for Mobile Live Camera)" if use_ssl else ""))
    print(f"  On PC:    {scheme}://127.0.0.1:5000")
    if debug:
        print("  Debug mode: bound to localhost only")
    else:
        print(f"  On Phone: {scheme}://{lan_ip()}:5000")
    if not use_ssl:
        print("  Tip: Add --ssl to enable the live phone camera viewfinder")
    print("=" * 60 + "\n")

    app.run(debug=debug, host=host, port=5000, ssl_context="adhoc" if use_ssl else None)
