# Phishing Detection Extension

A phishing-website detector made of three parts:

- **FastAPI backend** (`app.py`) that exposes a `/predict` endpoint.
- **Feature extractor** (`data/features.py`) that turns a URL into 30 numeric features.
- **Chrome extension** (`Extension/`) that sends the current tab's URL to the backend and shows the result.

Two machine-learning models vote on each prediction: a Random Forest (`model.pkl`) and a Multi-layer Perceptron (`modelANN.pkl`). A site is reported as **safe** only when both models agree it is safe.

## Project structure

```
.
├── app.py                  # FastAPI server
├── data/
│   └── features.py         # URL -> 30 feature values
├── models/
│   ├── RFC_Trainer.ipynb   # trains and saves model.pkl
│   ├── MLP_Trainer.ipynb   # trains and saves modelANN.pkl
│   ├── model.pkl           # (included) Random Forest
│   └── modelANN.pkl        # (included) MLP classifier
├── Extension/              # Chrome (Manifest V3) extension
│   ├── manifest.json
│   ├── popup.html
│   └── popup.js
└── requirements.txt
```

## Setup

1. Create and activate a virtual environment:

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

## (Optional) Retrain the models

Pre-trained models (`models/model.pkl` and `models/modelANN.pkl`) are included, so
the API works out of the box. To retrain them you need the phishing dataset
(`phishing.csv`, 30 feature columns + a `class` label of `1`/`-1`) placed in the
`models/` directory, then run both notebooks:

```bash
jupyter notebook models/RFC_Trainer.ipynb   # produces models/model.pkl
jupyter notebook models/MLP_Trainer.ipynb   # produces models/modelANN.pkl
```

A widely used compatible dataset is the
[Phishing Website Detector dataset on Kaggle](https://www.kaggle.com/datasets/eswarchandt/phishing-website-detector).

## Run the API

```bash
uvicorn app:app --reload --host 127.0.0.1 --port 8000
```

- `GET /` &rarr; health check
- `POST /predict` with body `{ "url": "https://example.com" }` &rarr;
  `{ "url": "...", "Prediction": "Website is safe", "is_phishing": false }`

If `model.pkl` / `modelANN.pkl` are missing, the server will raise a clear error
on startup telling you to train the models first.

## Load the Chrome extension

1. Make sure the API is running on `http://127.0.0.1:8000`.
2. Open `chrome://extensions`, enable **Developer mode**.
3. Click **Load unpacked** and select the `Extension/` folder.
4. Open the popup, confirm/enter a URL, and click **Check URL**.

## Notes

- CORS is open (`*`) for local development. Tighten `allow_origins` before any public deployment.
- Some features (WHOIS age, page rank, search-index lookups) depend on third-party
  network services and degrade gracefully to a neutral/unsafe value when unavailable.
