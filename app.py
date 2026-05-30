from pathlib import Path
import pickle

import numpy as np
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from data.features import getfeatures

app = FastAPI(title="Phishing Detection API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows requests from any domain
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods
    allow_headers=["*"],  # Allows all HTTP headers
)


class URLInput(BaseModel):
    url: str


MODELS_DIR = Path(__file__).resolve().parent / "models"


def _load_model(filename: str):
    path = MODELS_DIR / filename
    if not path.exists():
        raise FileNotFoundError(
            f"Model file '{path}' not found. Train the models first by running "
            f"the notebooks in the models/ directory (see README.md)."
        )
    with open(path, "rb") as file:
        return pickle.load(file)


model = _load_model("model.pkl")
modelANN = _load_model("modelANN.pkl")

@app.get("/")
async def root():
    return {"message": "Hello, this is the phishing detection API"}

@app.post("/predict")
async def predict(input_data: URLInput):
    try:
        # Extract features from the URL
        features = getfeatures(input_data.url)
        features_array = np.array(features).reshape(1, -1)  # Ensure 2D shape for model input

        prediction = int(model.predict(features_array)[0])
        predictionANN = int(modelANN.predict(features_array)[0])

        # Interpret prediction (1 == safe, -1 == phishing)
        if prediction == 1 and predictionANN == 1:
            result = "Website is safe"
            is_phishing = False
        elif prediction == -1 and predictionANN == -1:
            result = "Website is not safe"
            is_phishing = True
        else:
            result = "Prediction mismatch - unable to determine"
            is_phishing = None

        return {
            "url": input_data.url,
            "Prediction": result,
            "is_phishing": is_phishing,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
