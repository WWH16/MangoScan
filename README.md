# MangoScan

AI / Computer Vision Mango Quality & Classification System (Flask Web Application).

## Project Setup

### 1. Activate Virtual Environment
```bash
# Windows PowerShell:
.\venv\Scripts\Activate.ps1

# Windows Command Prompt:
.\venv\Scripts\activate.bat
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run Application
```bash
python app.py
```
Access the application at `http://127.0.0.1:5000`.

Options:
- `python app.py --ssl`: HTTPS (needed for live phone camera; requires `pyOpenSSL`).
- `python app.py --debug`: Flask debug mode, bound to `127.0.0.1` only.
- Set `MANGOSCAN_SECRET_KEY` to use a fixed secret key.

Model artifacts live in `models/`: `svm_model.pkl`, `scaler.pkl`, `label_encoder.pkl` and
`predict.py`, copied straight from the training notebook's export folder. `models/inference.py`
imports `predict.py` rather than reimplementing it, so a retrain only needs the export folder copied
over `models/` again.
