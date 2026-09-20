"""
App-side wrapper around the trained classifier.

`predict.py` and the three `.joblib` files beside it are copied straight out of
the training notebook's export folder (CELL 18). Nothing in this file
re-implements segmentation or feature extraction: it imports them, so the app
and the training run cannot drift apart. After a retrain, copying the export
folder over `models/` is the whole update.

What this file adds on top of the export:
  * `predict()` takes an already-decoded BGR array from the upload instead of a
    path, and reports a confidence when the saved model can produce one.
  * `overlay_mask()` and `generate_detection_overlay()` draw the diagnostic
    annotations shown on the result page.
"""

import os
import cv2
import numpy as np

MODELS_DIR = os.path.dirname(os.path.abspath(__file__))

# Everything the training notebook exports, and the app needs present
REQUIRED_FILES = (
    "predict.py",
    "svm_model.pkl",
    "scaler.pkl",
    "label_encoder.pkl",
)

_classifier = None

# The overlay works at photo resolution, so it keeps its own copy of the
# training size rather than importing one at module load
IMG_SIZE = (128, 128)


def load_artifacts():
    """
    Import the exported predictor, with an explicit error if any file is missing.

    `predict.py` loads its `.joblib` files at import time, so the files are
    checked first: a missing artifact should name itself rather than surface as
    an import traceback.
    """
    global _classifier

    if _classifier is not None:
        return _classifier

    missing = [n for n in REQUIRED_FILES if not os.path.exists(os.path.join(MODELS_DIR, n))]
    if missing:
        raise FileNotFoundError(
            f"Missing required model artifact(s) in {MODELS_DIR}: {', '.join(missing)}. "
            f"Copy the contents of the training export folder into the models/ folder."
        )

    from . import predict as classifier
    _classifier = classifier

    return _classifier


# ============================================================
# PREDICTION
# ============================================================

def predict(image_bgr):
    """
    Classify a BGR image decoded by OpenCV from a user upload.

    Mirrors `predict.predict_disease()` exactly, differing only in taking a
    decoded array rather than a file path.

    Returns:
        (label: str, confidence: float or None)
    """
    clf = load_artifacts()

    img_rgb = cv2.resize(cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB), clf.IMG_SIZE)
    features = clf.extract_features(img_rgb, clf.fruit_mask(img_rgb))
    scaled = clf.scaler.transform(features.reshape(1, -1))

    pred_idx = clf.svm_model.predict(scaled)[0]

    try:
        label = clf.le.inverse_transform([pred_idx])[0]
    except Exception:
        label = str(pred_idx)

    # The current SVC is fitted without probability estimates, so this stays
    # None and the result page hides the confidence row. A model retrained with
    # probability=True fills it in with no further change here.
    confidence = None
    if hasattr(clf.svm_model, "predict_proba"):
        try:
            confidence = float(np.max(clf.svm_model.predict_proba(scaled)[0]))
        except Exception:
            confidence = None

    return str(label), confidence


# ============================================================
# DETECTION OVERLAY
# ============================================================

def overlay_mask(image_bgr, max_side=512):
    """
    Fruit silhouette at the photo's own resolution, for the detection overlay.

    The classifier segments the 128x128 training-sized image, which is far too
    coarse to draw lesion boxes on a phone photo. GrabCut cost scales with pixel
    count, so this runs on a copy no larger than `max_side` and scales the mask
    back up.
    """
    clf = load_artifacts()

    h, w = image_bgr.shape[:2]
    scale = min(1.0, max_side / max(h, w))
    small = (
        cv2.resize(image_bgr, (max(1, int(w * scale)), max(1, int(h * scale))),
                   interpolation=cv2.INTER_AREA)
        if scale < 1.0 else image_bgr
    )

    mask = clf.fruit_mask(cv2.cvtColor(small, cv2.COLOR_BGR2RGB))

    if mask.shape[:2] != (h, w):
        mask = cv2.resize(mask, (w, h), interpolation=cv2.INTER_LINEAR)
        mask = np.where(mask > 127, 255, 0).astype(np.uint8)

    return mask


def merge_boxes(boxes):
    """Merge overlapping or nested (x, y, w, h) boxes until none overlap; largest first."""
    boxes = [list(b) for b in boxes]
    merged = True
    while merged:
        merged = False
        for i in range(len(boxes)):
            for j in range(i + 1, len(boxes)):
                ax, ay, aw, ah = boxes[i]
                bx, by, bw, bh = boxes[j]
                if ax <= bx + bw and bx <= ax + aw and ay <= by + bh and by <= ay + ah:
                    x0, y0 = min(ax, bx), min(ay, by)
                    x1, y1 = max(ax + aw, bx + bw), max(ay + ah, by + bh)
                    boxes[i] = [x0, y0, x1 - x0, y1 - y0]
                    del boxes[j]
                    merged = True
                    break
            if merged:
                break
    return sorted((tuple(b) for b in boxes), key=lambda b: b[2] * b[3], reverse=True)


def _fruit_region(image_bgr, mask):
    """
    Boolean fruit silhouette plus its pixel count.

    Prefers the GrabCut mask. Without one, falls back to an Otsu threshold,
    eroded so the stem, the twig and the dark peel edge are not counted as fruit
    body. If neither yields anything, the whole frame is used, so the caller
    always has a region to measure against.
    """
    h, w = image_bgr.shape[:2]

    if mask is not None:
        fruit = mask > 127
    else:
        gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        _, thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        erode_k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (max(3, w // 40),) * 2)
        fruit = cv2.erode(thresh, erode_k) > 0

    fruit_pixels = int(np.count_nonzero(fruit))
    if fruit_pixels == 0:
        fruit = np.ones((h, w), dtype=bool)
        fruit_pixels = h * w

    return fruit, fruit_pixels


def _fruit_core(fruit, segmented):
    """
    The fruit interior, pulled back from its outline.

    Segmentation error lives at the boundary: a finger, a leaf or a shadow that
    GrabCut clipped in appears there as a dark strip and reads as one huge
    lesion. The Otsu fallback already erodes its own mask, so this applies to
    the GrabCut mask only.
    """
    if not segmented:
        return fruit

    h, w = fruit.shape[:2]
    k = max(3, int(min(h, w) * 0.03)) | 1  # odd size, so the kernel has a centre
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k, k))
    core = cv2.erode(fruit.astype(np.uint8), kernel) > 0

    return core if np.count_nonzero(core) else fruit


def _lesion_mask(image_bgr, fruit):
    """
    Peel that is much darker than the fruit's own median brightness.

    The cutoff is relative to the fruit, not to a fixed value, so a photo taken
    in shade is judged against its own exposure rather than against a studio one.
    """
    value = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2HSV)[:, :, 2]
    fruit_v = value[fruit]
    if fruit_v.size == 0:
        return np.zeros(value.shape, np.uint8)

    cutoff = 0.6 * float(np.median(fruit_v))
    lesion = ((value < cutoff) & fruit).astype(np.uint8) * 255

    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    return cv2.morphologyEx(lesion, cv2.MORPH_OPEN, kernel)


def generate_detection_overlay(image_bgr, label, mask=None):
    """
    Generates computer-vision bounding boxes and diagnostic annotations for the
    detected condition, plus the telemetry shown on the result page.

    `mask` is the GrabCut silhouette from `overlay_mask()`. When it is given,
    every box and every percentage is measured against the real fruit instead of
    against the whole photo, so the table, the hand and the background no longer
    count as peel.
    """
    annotated = image_bgr.copy()
    h, w = image_bgr.shape[:2]

    # Color telemetry
    img_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
    img_resized = cv2.resize(img_rgb, IMG_SIZE)
    hsv = cv2.cvtColor(img_resized, cv2.COLOR_RGB2HSV)
    mean_hue = float(np.mean(hsv[:, :, 0]))
    mean_sat = float(np.mean(hsv[:, :, 1]))

    segmented = mask is not None
    fruit, fruit_pixels = _fruit_region(image_bgr, mask)
    fx, fy, fw, fh = cv2.boundingRect(fruit.astype(np.uint8))

    # Boxes and the bounding box follow the full silhouette; every measurement
    # follows the interior, where the mask is trustworthy
    core = _fruit_core(fruit, segmented)
    core_pixels = max(1, int(np.count_nonzero(core)))

    lesion = _lesion_mask(image_bgr, core)
    area_pct = round(cv2.countNonZero(lesion) / core_pixels * 100, 1)

    line_w = max(2, w // 300)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    label_lower = (label or "").lower()

    if "healthy" in label_lower:
        # Green bounding box around the fruit, with corner crosshairs
        pad = int(max(fw, fh) * 0.04)
        x1, y1 = max(0, fx - pad), max(0, fy - pad)
        x2, y2 = min(w - 1, fx + fw + pad), min(h - 1, fy + fh + pad)
        cv2.rectangle(annotated, (x1, y1), (x2, y2), (72, 161, 36), 3)

        corner_len = int(min(x2 - x1, y2 - y1) * 0.12)
        cv2.line(annotated, (x1, y1), (x1 + corner_len, y1), (72, 161, 36), 5)
        cv2.line(annotated, (x1, y1), (x1, y1 + corner_len), (72, 161, 36), 5)
        cv2.line(annotated, (x2, y2), (x2 - corner_len, y2), (72, 161, 36), 5)
        cv2.line(annotated, (x2, y2), (x2, y2 - corner_len), (72, 161, 36), 5)

        telemetry = {
            "defect_coverage": "0.0% (clear surface)",
            "grade": "Export quality",
            "grade_letter": "A",
            "imperative": "Ship it.",
            "action": "Fruit approved for commercial distribution, packaging, and long-term storage."
        }
    elif "anthracnose" in label_lower:
        # Red boxes around the dark necrotic spots on the peel
        spots = cv2.dilate(lesion, kernel, iterations=2)
        contours, _ = cv2.findContours(spots, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        min_area = core_pixels * 0.0008
        boxes = []
        for c in contours:
            if cv2.contourArea(c) <= min_area:
                continue
            x, y, cw, ch = cv2.boundingRect(c)
            # Without a segmentation mask, spots touching the photo border are
            # background shadow rather than lesion, so drop them
            if not segmented:
                margin = 3
                if x <= margin or y <= margin or x + cw >= w - margin or y + ch >= h - margin:
                    continue
            boxes.append((x, y, cw, ch))

        for x, y, cw, ch in merge_boxes(boxes)[:8]:
            cv2.rectangle(annotated, (x, y), (x + cw, y + ch), (40, 30, 218), line_w)

        telemetry = {
            "defect_coverage": f"{min(95.0, area_pct)}% of surface",
            "grade": "Infected specimen (cull)",
            "grade_letter": "C",
            "imperative": "Quarantine.",
            "action": "Quarantine fruit. Apply postharvest hot water treatment (48 °C for 20 min) or prochloraz dip."
        }
    else:  # Stem_Rot
        # Amber frame on the stem shoulder: the top 45% of the fruit itself
        shoulder_h = max(1, int(fh * 0.45))
        cv2.rectangle(annotated, (fx, fy), (fx + fw, fy + shoulder_h), (0, 180, 240), 3)

        shoulder = np.zeros((h, w), dtype=bool)
        shoulder[fy:fy + shoulder_h, fx:fx + fw] = True
        shoulder &= core
        shoulder_pixels = max(1, int(np.count_nonzero(shoulder)))
        shoulder_pct = round(
            int(np.count_nonzero((lesion > 0) & shoulder)) / shoulder_pixels * 100, 1
        )

        telemetry = {
            "defect_coverage": f"{min(85.0, shoulder_pct)}% of stem shoulder",
            "grade": "Vascular tissue decay",
            "grade_letter": "C",
            "imperative": "Trim the stem.",
            "action": "Trim stem flush with fruit shoulder. Separate from export crates and store in dry ventilation (below 13 °C)."
        }

    metrics = {
        "mean_hue": f"{mean_hue:.1f} / 180",
        "saturation": f"{mean_sat:.1f} / 255",
        "resolution": f"{w} × {h} px"
    }

    return annotated, telemetry, metrics
