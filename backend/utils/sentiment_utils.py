from pathlib import Path

import joblib
import torch
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    pipeline,
)

from utils.text_preprocessing import clean_text


# ============================================================
# Project Paths
# ============================================================

UTILS_DIR = Path(__file__).resolve().parent
BACKEND_DIR = UTILS_DIR.parent
PROJECT_ROOT = BACKEND_DIR.parent


# ============================================================
# Candidate Model Paths
# ============================================================

AR_MODEL_CANDIDATES = [
    PROJECT_ROOT / "sentiment_arabic",
    PROJECT_ROOT / "Sentiment_Ara",
    BACKEND_DIR / "Sentiment_Ara",
]

EN_MODEL_CANDIDATES = [
    PROJECT_ROOT / "sentiment_eng",
    PROJECT_ROOT / "Sentiment_Eng",
    BACKEND_DIR / "Sentiment_Eng",
]


# ============================================================
# Runtime Device
# ============================================================

DEVICE = 0 if torch.cuda.is_available() else -1


# ============================================================
# Cached Models
# ============================================================

sentiment_model_ar = None
sentiment_model_en = None

sentiment_type_ar = None
sentiment_type_en = None


# ============================================================
# Helpers
# ============================================================

def normalize_sentiment(label):
    """
    Normalize different model labels into:
    positive / negative / neutral
    """

    label = str(label).lower().strip()

    positive_labels = {
        "positive",
        "pos",
        "label_2",
        "2",
        "ايجابي",
        "إيجابي",
    }

    negative_labels = {
        "negative",
        "neg",
        "label_0",
        "0",
        "سلبي",
    }

    neutral_labels = {
        "neutral",
        "neu",
        "label_1",
        "1",
        "محايد",
    }

    if label in positive_labels:
        return "positive"

    if label in negative_labels:
        return "negative"

    if label in neutral_labels:
        return "neutral"

    return "neutral"


def find_joblib_model(model_dir):
    """
    Look for common sklearn/joblib model filenames.
    """

    if model_dir is None:
        return None

    model_dir = Path(model_dir)

    possible_files = [
        model_dir / "model.pkl",
        model_dir / "sentiment_model.pkl",
        model_dir / "classifier.pkl",
        model_dir / "model.joblib",
    ]

    for file_path in possible_files:
        if file_path.exists():
            return file_path

    return None


def is_transformer_model(model_dir):
    """
    Detect whether a folder contains
    a usable Hugging Face model.
    """

    if model_dir is None:
        return False

    model_dir = Path(model_dir)

    config_file = model_dir / "config.json"

    weight_files = [
        model_dir / "model.safetensors",
        model_dir / "pytorch_model.bin",
    ]

    return (
        config_file.exists()
        and any(
            path.exists()
            for path in weight_files
        )
    )


def find_existing_model(candidates):
    """
    Find the first usable sentiment model.

    A usable model can be:
    1. Hugging Face Transformer model
    2. Joblib / pickle classifier

    Also checks one folder level inside
    each candidate directory.
    """

    for candidate in candidates:

        candidate = Path(candidate)

        if not candidate.exists():
            continue

        # Check candidate directory itself
        if (
            is_transformer_model(candidate)
            or find_joblib_model(candidate) is not None
        ):
            return candidate

        # Check one folder level inside
        if candidate.is_dir():

            for child in candidate.iterdir():

                if not child.is_dir():
                    continue

                if (
                    is_transformer_model(child)
                    or find_joblib_model(child) is not None
                ):
                    return child

    return None


# ============================================================
# Model Loading
# ============================================================

def load_sentiment_model(lang):
    """
    Load Arabic or English sentiment model.

    Supports:
    1. Hugging Face Transformer folders.
    2. Legacy joblib / pickle classifiers.
    """

    global sentiment_model_ar
    global sentiment_model_en
    global sentiment_type_ar
    global sentiment_type_en

    if lang == "ar":
        cached_model = sentiment_model_ar
        candidates = AR_MODEL_CANDIDATES

    else:
        cached_model = sentiment_model_en
        candidates = EN_MODEL_CANDIDATES

    if cached_model is not None:
        return cached_model

    model_dir = find_existing_model(
        candidates
    )

    if model_dir is None:
        print(
            f"[SENTIMENT WARNING] "
            f"No usable sentiment model found for language: {lang}"
        )

        return None

    # --------------------------------------------------------
    # Hugging Face Transformer
    # --------------------------------------------------------

    if is_transformer_model(
        model_dir
    ):
        try:
            tokenizer = AutoTokenizer.from_pretrained(
                model_dir
            )

            model = (
                AutoModelForSequenceClassification
                .from_pretrained(
                    model_dir
                )
            )

            classifier = pipeline(
                "text-classification",
                model=model,
                tokenizer=tokenizer,
                device=DEVICE,
            )

            if lang == "ar":
                sentiment_model_ar = classifier
                sentiment_type_ar = "transformer"

            else:
                sentiment_model_en = classifier
                sentiment_type_en = "transformer"

            print(
                f"[SENTIMENT] "
                f"{lang.upper()} transformer model loaded from: "
                f"{model_dir}"
            )

            return classifier

        except Exception as exc:
            print(
                "[SENTIMENT TRANSFORMER WARNING]",
                exc,
            )

    # --------------------------------------------------------
    # Legacy sklearn / joblib
    # --------------------------------------------------------

    joblib_path = find_joblib_model(
        model_dir
    )

    if joblib_path is not None:
        try:
            classifier = joblib.load(
                joblib_path
            )

            if lang == "ar":
                sentiment_model_ar = classifier
                sentiment_type_ar = "joblib"

            else:
                sentiment_model_en = classifier
                sentiment_type_en = "joblib"

            print(
                f"[SENTIMENT] "
                f"{lang.upper()} joblib model loaded from: "
                f"{joblib_path}"
            )

            return classifier

        except Exception as exc:
            print(
                "[SENTIMENT JOBLIB WARNING]",
                exc,
            )

    print(
        f"[SENTIMENT WARNING] "
        f"No usable sentiment model found inside: {model_dir}"
    )

    return None


# ============================================================
# Prediction Helpers
# ============================================================

def predict_transformer(
    model,
    text,
):
    """
    Predict sentiment using Hugging Face pipeline.
    """

    prediction = model(
        text,
        truncation=True,
    )[0]

    label = prediction.get(
        "label",
        "neutral",
    )

    score = float(
        prediction.get(
            "score",
            0.0,
        )
    )

    return (
        normalize_sentiment(label),
        score,
    )


def predict_joblib(
    model,
    text,
):
    """
    Predict sentiment using sklearn/joblib classifier.
    """

    prediction = model.predict(
        [text]
    )[0]

    sentiment = normalize_sentiment(
        prediction
    )

    if hasattr(
        model,
        "predict_proba",
    ):
        probabilities = model.predict_proba(
            [text]
        )[0]

        score = float(
            max(probabilities)
        )

    else:
        score = 1.0

    return (
        sentiment,
        score,
    )


# ============================================================
# Main Prediction Function
# ============================================================

def predict_sentiment(
    text: str,
    lang: str = "ar",
):
    """
    Predict sentiment for Arabic or English customer messages.

    Returns:
        (sentiment, confidence)

    sentiment:
        positive / neutral / negative
    """

    text = str(
        text
    ).strip()

    if not text:
        return (
            "neutral",
            0.0,
        )

    cleaned_text = clean_text(
        text
    )

    try:
        model = load_sentiment_model(
            lang
        )

        if model is None:
            return (
                "neutral",
                0.0,
            )

        if lang == "ar":
            model_type = sentiment_type_ar

        else:
            model_type = sentiment_type_en

        if model_type == "transformer":
            return predict_transformer(
                model,
                cleaned_text,
            )

        if model_type == "joblib":
            return predict_joblib(
                model,
                cleaned_text,
            )

        return (
            "neutral",
            0.0,
        )

    except Exception as exc:
        print(
            "[SENTIMENT WARNING]",
            exc,
        )

        return (
            "neutral",
            0.0,
        )
