import re
from scipy.sparse import hstack
from .loader import model, tfidf, ohe, label_encoder


def clean_text(text: str) -> str:
    if not text:
        return ""
    text = text.lower()
    text = re.sub(r"http\S+|www\S+|https\S+", "", text)
    text = re.sub(r"[^a-zA-Z0-9\s\U0001F600-\U0001F64F]", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def predict_sentiment(text: str, brand: str = "unknown") -> str:
    clean = clean_text(text)

    X_text = tfidf.transform([clean])
    X_brand = ohe.transform([[brand]])

    X = hstack([X_text, X_brand])

    pred = model.predict(X)
    label = label_encoder.inverse_transform(pred)[0]

    return label
