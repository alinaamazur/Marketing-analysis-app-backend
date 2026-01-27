import os
import joblib

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MODEL_PATH = os.path.join(BASE_DIR, "models")

model = joblib.load(os.path.join(MODEL_PATH, "sentiment_model.joblib"))
tfidf = joblib.load(os.path.join(MODEL_PATH, "tfidf_vectorizer.joblib"))
ohe = joblib.load(os.path.join(MODEL_PATH, "brand_encoder.joblib"))
label_encoder = joblib.load(os.path.join(MODEL_PATH, "label_encoder.joblib"))