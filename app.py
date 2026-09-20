import os
import re
import json
import uuid
import base64
import socket
import binascii
from flask import Flask, render_template, request, url_for, jsonify, redirect, send_from_directory, session
from werkzeug.utils import secure_filename
import cv2
import numpy as np

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__)
app.secret_key = os.environ.get("MANGOSCAN_SECRET_KEY") or "mangoscan-production-secret-key-salt"

# 10 MB maximum upload limit
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024

# Vercel serverless has a read-only filesystem; writable scratch is in /tmp
IS_VERCEL = bool(os.environ.get("VERCEL"))
if IS_VERCEL:
    UPLOAD_FOLDER = os.path.join("/tmp", "mangoscan_uploads")
    SCAN_FOLDER = os.path.join("/tmp", "mangoscan_scans")
else:
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads")
    SCAN_FOLDER = os.path.join(BASE_DIR, "uploads")

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(SCAN_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}
TOKEN_RE = re.compile(r"^[0-9a-f]{8}$")


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def wants_json():
    return request.is_json


def error_response(message, status):
    """Return the error in the format the client expects (JSON for camera captures)."""
    if wants_json():
        return jsonify({"error": message}), status
    return render_template("upload.html", error=message), status


def scan_record_path(token):
    return os.path.join(SCAN_FOLDER, f"{token}.json")


@app.route("/")
def index():
    return render_template("upload.html")


@app.route("/predict", methods=["GET", "POST"])
def predict():
    if request.method == "GET":
        return redirect(url_for("index"))
    file_bytes = None
    original_filename = "camera_capture.jpg"

    # Support JSON base64 capture from live camera
    if request.is_json:
        payload = request.get_json(silent=True) or {}
        b64_data = payload.get("image_base64")
        if not isinstance(b64_data, str) or not b64_data:
            return error_response("No camera image received.", 400)
        if "," in b64_data:
            b64_data = b64_data.split(",", 1)[1]
        try:
            file_bytes = base64.b64decode(b64_data, validate=True)
        except (binascii.Error, ValueError) as e:
            return error_response(f"Camera capture decoding failed: {e}", 400)
        original_filename = "camera_scan.jpg"

    # Support standard file upload or direct camera capture
    elif "image" in request.files or "image_camera" in request.files:
        file = None
        for key in ("image", "image_camera"):
            candidate = request.files.get(key)
            if candidate and candidate.filename:
                file = candidate
                break

        if not file:
            return error_response("No file selected. Please choose or capture a mango photo.", 400)

        if not allowed_file(file.filename):
            return error_response("Unsupported format. Please upload a JPG, PNG, or WEBP image.", 400)

        file_bytes = file.read()
        # secure_filename can strip everything (e.g. non-ASCII names); keep the extension
        ext = file.filename.rsplit(".", 1)[1].lower()
        original_filename = secure_filename(file.filename) or f"upload.{ext}"

    else:
        return error_response("Please choose an image file to upload.", 400)

    # Decode image with OpenCV
    np_arr = np.frombuffer(file_bytes, np.uint8)
    image_bgr = cv2.imdecode(np_arr, cv2.IMREAD_COLOR) if np_arr.size else None
    if image_bgr is None:
        return error_response("Could not read this file as an image. Please choose a valid photo.", 400)

    token = uuid.uuid4().hex[:8]
    raw_filename = f"{token}_{original_filename}"
    ann_filename = f"detection_{token}_{original_filename}"

    # Run ML inference and generate computer vision detection overlay
    try:
        from models import inference
        label, confidence = inference.predict(image_bgr)
        # Segment again at display resolution so the boxes and percentages are
        # measured against the fruit rather than against the whole photo
        mask = inference.overlay_mask(image_bgr)
        annotated_bgr, telemetry, metrics = inference.generate_detection_overlay(
            image_bgr, label, mask=mask
        )
    except FileNotFoundError as e:
        return error_response(f"Model files not found in models/: {e}", 500)
    except Exception as e:
        app.logger.exception("Diagnosis failed")
        return error_response(f"Diagnosis error: {e}", 500)

    # Save original, annotated image, and the scan result
    with open(os.path.join(UPLOAD_FOLDER, raw_filename), "wb") as f:
        f.write(file_bytes)
    ext = os.path.splitext(ann_filename)[1] or ".jpg"
    ok, encoded = cv2.imencode(ext, annotated_bgr)
    if not ok:
        return error_response("Could not save the detection overlay.", 500)
    with open(os.path.join(UPLOAD_FOLDER, ann_filename), "wb") as f:
        f.write(encoded.tobytes())

    record = {
        "filename": original_filename,
        "raw_filename": raw_filename,
        "ann_filename": ann_filename,
        "label": str(label),
        "confidence": confidence,
        "telemetry": telemetry,
        "metrics": metrics,
    }
    try:
        with open(scan_record_path(token), "w", encoding="utf-8") as f:
            json.dump(record, f, ensure_ascii=False)
    except OSError:
        pass

    session[f"scan_{token}"] = record

    redirect_url = url_for("result_view", token=token)
    if request.is_json:
        return jsonify({"success": True, "redirect_url": redirect_url})
    return redirect(redirect_url)


@app.route("/scan_uploads/<path:filename>")
def serve_upload(filename):
    """Serve uploaded and annotated scan images from the active upload folder."""
    return send_from_directory(UPLOAD_FOLDER, filename)


@app.route("/result/<token>")
def result_view(token):
    expired = "Scan session expired. Please start a new scan."
    if not TOKEN_RE.match(token):
        return render_template("upload.html", error=expired), 404

    record = None
    try:
        with open(scan_record_path(token), encoding="utf-8") as f:
            record = json.load(f)
    except (OSError, ValueError):
        pass

    if not record:
        record = session.get(f"scan_{token}")

    if not record:
        return render_template("upload.html", error=expired), 404

    raw_file = record.get("raw_filename", "")
    if not raw_file or not os.path.exists(os.path.join(UPLOAD_FOLDER, raw_file)):
        return render_template("upload.html", error=expired), 404

    return render_template(
        "result.html",
        image_url=url_for("serve_upload", filename=record["raw_filename"]),
        annotated_url=url_for("serve_upload", filename=record["ann_filename"]),
        filename=record["filename"],
        prediction=record["label"],
        confidence=record.get("confidence"),
        telemetry=record["telemetry"],
        metrics=record["metrics"],
    )


@app.errorhandler(405)
def method_not_allowed(error):
    return redirect(url_for("index"))


@app.errorhandler(413)
def request_entity_too_large(error):
    return error_response("File is too large (exceeds 10 MB limit). Please choose a smaller photo.", 413)


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
