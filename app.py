import os
import uuid
import base64
from flask import Flask, render_template, request, url_for, jsonify, redirect
from werkzeug.utils import secure_filename
import cv2
import numpy as np

app = Flask(__name__)
app.secret_key = "mangoscan-thesis-secret-key"

# 10 MB maximum upload limit
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024

UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

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
    if request.is_json and "image_base64" in request.json:
        try:
            b64_data = request.json["image_base64"]
            if "," in b64_data:
                b64_data = b64_data.split(",", 1)[1]
            file_bytes = base64.b64decode(b64_data)
            original_filename = "camera_scan.jpg"
        except Exception as e:
            return jsonify({"error": f"Camera capture decoding failed: {str(e)}"}), 400

    # Support standard file upload or direct camera capture
    elif "image" in request.files or "image_camera" in request.files:
        file = None
        for key in ("image", "image_camera"):
            candidate = request.files.get(key)
            if candidate and candidate.filename:
                file = candidate
                break

        if not file or file.filename == "":
            return render_template("upload.html", error="No file selected. Please choose or capture a mango photo."), 400

        if not allowed_file(file.filename):
            return render_template(
                "upload.html",
                error="Unsupported format. Please upload a JPG, PNG, or WEBP image."
            ), 400

        file_bytes = file.read()
        original_filename = secure_filename(file.filename)

    else:
        return render_template("upload.html", error="Please choose an image file to upload."), 400

    # Decode image with OpenCV
    try:
        np_arr = np.frombuffer(file_bytes, np.uint8)
        image_bgr = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        if image_bgr is None:
            return render_template(
                "upload.html",
                error="Could not read this file as an image. Please choose a valid photo."
            ), 400

    except Exception as e:
        return render_template("upload.html", error=f"Image processing error: {str(e)}"), 400

    # Save original raw image
    token = uuid.uuid4().hex[:8]
    raw_filename = f"{token}_{original_filename}"
    raw_path = os.path.join(app.config["UPLOAD_FOLDER"], raw_filename)
    with open(raw_path, "wb") as f:
        f.write(file_bytes)

    # Run ML inference and generate computer vision detection overlay
    try:
        from models import inference
        label, confidence = inference.predict(image_bgr)
        annotated_bgr, telemetry, metrics = inference.generate_detection_overlay(image_bgr, label)

        # Save annotated detection image
        ann_filename = f"detection_{token}_{original_filename}"
        ann_path = os.path.join(app.config["UPLOAD_FOLDER"], ann_filename)
        cv2.imwrite(ann_path, annotated_bgr)

    except FileNotFoundError as e:
        return render_template(
            "upload.html",
            error=f"Model files not found in models/: {str(e)}"
        ), 500
    except Exception as e:
        return render_template(
            "upload.html",
            error=f"Diagnosis error: {str(e)}"
        ), 500

    image_url = url_for("static", filename=f"uploads/{raw_filename}")
    annotated_url = url_for("static", filename=f"uploads/{ann_filename}")

    # If requested via camera JSON, return redirect URL
    if request.is_json:
        return jsonify({
            "success": True,
            "redirect_url": url_for("result_view", token=token, filename=original_filename, label=label)
        })

    return redirect(url_for("result_view", token=token, filename=original_filename, label=label))

@app.route("/result/<token>")
def result_view(token):
    # Lookup generated files for this token
    filename = request.args.get("filename", "specimen.jpg")
    label = request.args.get("label", "Healthy")
    raw_filename = f"{token}_{filename}"
    ann_filename = f"detection_{token}_{filename}"

    image_url = url_for("static", filename=f"uploads/{raw_filename}")
    annotated_url = url_for("static", filename=f"uploads/{ann_filename}")

    raw_path = os.path.join(app.config["UPLOAD_FOLDER"], raw_filename)
    if not os.path.exists(raw_path):
        return render_template("upload.html", error="Scan session expired. Please start a new scan."), 404

    image_bgr = cv2.imread(raw_path)
    from models import inference
    _, telemetry, metrics = inference.generate_detection_overlay(image_bgr, label)

    return render_template(
        "result.html",
        image_url=image_url,
        annotated_url=annotated_url,
        filename=filename,
        prediction=label,
        confidence=None,
        telemetry=telemetry,
        metrics=metrics
    )

@app.errorhandler(405)
def method_not_allowed(error):
    return redirect(url_for("index"))

@app.errorhandler(413)
def request_entity_too_large(error):
    return render_template("upload.html", error="File is too large (exceeds 10 MB limit). Please choose a smaller photo."), 413

if __name__ == "__main__":
    import sys
    use_ssl = "--ssl" in sys.argv
    if use_ssl:
        print("\n" + "=" * 60)
        print("  MangoScan running in HTTPS Mode (for Mobile Live Camera)")
        print("  On PC:    https://127.0.0.1:5000")
        print("  On Phone: https://192.168.254.103:5000")
        print("=" * 60 + "\n")
        app.run(debug=True, host="0.0.0.0", port=5000, ssl_context="adhoc")
    else:
        print("\n" + "=" * 60)
        print("  MangoScan running in HTTP Mode")
        print("  On PC:    http://127.0.0.1:5000")
        print("  On Phone: http://192.168.254.103:5000")
        print("  Tip: Add --ssl to enable the live phone camera viewfinder")
        print("=" * 60 + "\n")
        app.run(debug=True, host="0.0.0.0", port=5000)
