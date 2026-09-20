from pathlib import Path
import pickle
import cv2
import numpy as np
from skimage.feature import graycomatrix, graycoprops

HERE = Path(__file__).resolve().parent
IMG_SIZE = (128, 128)


def _load(name):
    with open(HERE / name, "rb") as f:
        return pickle.load(f)


svm_model = _load("svm_model.pkl")
le = _load("label_encoder.pkl")
scaler = _load("scaler.pkl")


def fruit_mask(img):
    cv2.setRNGSeed(0)
    h, w = img.shape[:2]
    full = np.full((h, w), 255, np.uint8)
    m = np.zeros((h, w), np.uint8)
    rect = (int(w * 0.08), int(h * 0.08), int(w * 0.84), int(h * 0.84))
    bgd = np.zeros((1, 65), np.float64)
    fgd = np.zeros((1, 65), np.float64)

    try:
        cv2.grabCut(cv2.cvtColor(img, cv2.COLOR_RGB2BGR), m, rect, bgd, fgd, 3, cv2.GC_INIT_WITH_RECT)
    except cv2.error:
        return full

    mask = np.where((m == cv2.GC_FGD) | (m == cv2.GC_PR_FGD), 255, 0).astype(np.uint8)
    n, lab, stats, _ = cv2.connectedComponentsWithStats(mask)
    if n <= 1:
        return full

    largest = 1 + np.argmax(stats[1:, cv2.CC_STAT_AREA])
    mask = np.where(lab == largest, 255, 0).astype(np.uint8)
    return mask if (mask > 0).mean() > 0.15 else full


def color_hist(img, mask, bins=8):
    hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)
    hist = cv2.calcHist([hsv], [0, 1, 2], mask, [bins] * 3, [0, 180, 0, 256, 0, 256])
    return cv2.normalize(hist, hist).flatten()


def glcm_features(img, mask):
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    ys, xs = np.where(mask > 0)
    gray = cv2.resize(gray[ys.min():ys.max() + 1, xs.min():xs.max() + 1], (64, 64))

    glcm = graycomatrix(
        gray, [1],
        [0, np.pi / 4, np.pi / 2, 3 * np.pi / 4],
        levels=256, symmetric=True, normed=True
    )
    props = ["contrast", "dissimilarity", "homogeneity", "energy", "correlation"]
    return np.hstack([graycoprops(glcm, p).flatten() for p in props])


def hu_features(mask):
    hu = cv2.HuMoments(cv2.moments(mask, binaryImage=True)).flatten()
    return -np.sign(hu) * np.log10(np.abs(hu) + 1e-10)


def extract_features(img, mask):
    return np.hstack([color_hist(img, mask), glcm_features(img, mask), hu_features(mask)])


def predict_disease(path):
    bgr = cv2.imread(str(path))
    if bgr is None:
        raise ValueError(f"Could not read image: {path}")
    img = cv2.resize(cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB), IMG_SIZE)
    x = scaler.transform(extract_features(img, fruit_mask(img)).reshape(1, -1))
    return le.inverse_transform(svm_model.predict(x))[0]


if __name__ == "__main__":
    import sys
    print(predict_disease(sys.argv[1]))
