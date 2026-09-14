import os
import joblib
import pandas as pd


# ============================================================
# Paths
# ============================================================

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.dirname(CURRENT_DIR)
PROJECT_ROOT = os.path.dirname(BACKEND_DIR)

PREDICTION_DIR = os.path.join(
    PROJECT_ROOT,
    "prediction"
)

MODEL_PATH = os.path.join(
    PREDICTION_DIR,
    "network_issue_model.pkl"
)

COLUMNS_PATH = os.path.join(
    PREDICTION_DIR,
    "network_issue_columns.pkl"
)


# ============================================================
# Load Model
# ============================================================

prediction_model = None
required_columns = []


try:
    prediction_model = joblib.load(
        MODEL_PATH
    )

    required_columns = joblib.load(
        COLUMNS_PATH
    )

    print(
        "Network prediction model loaded successfully."
    )

except Exception as exc:
    print(
        "Network prediction model could not be loaded:",
        exc,
    )


# ============================================================
# Helpers
# ============================================================

def model_available():
    return (
        prediction_model is not None
        and len(required_columns) > 0
    )


def prepare_network_features(metrics):
    """
    Prepare telecom KPI input so that it matches
    the exact feature structure used during XGBoost training.

    Missing values are filled with 0 only for compatibility.
    In production, real telecom KPI values should be supplied
    by the network monitoring system.
    """

    if not isinstance(metrics, dict):
        return None

    row = {}

    for column in required_columns:
        row[column] = metrics.get(
            column,
            0
        )

    return pd.DataFrame(
        [row],
        columns=required_columns,
    )


def has_meaningful_kpis(metrics):
    """
    Prevent the model from making a prediction when
    no real network KPI information has been supplied.
    """

    if not isinstance(metrics, dict):
        return False

    if not required_columns:
        return False

    values_found = 0

    for column in required_columns:

        if column not in metrics:
            continue

        value = metrics.get(column)

        if value is None:
            continue

        values_found += 1

    return values_found > 0


# ============================================================
# Network Prediction
# ============================================================

def predict_network_issue(
    metrics=None,
    return_probability=False,
):
    """
    Predict whether a network issue is expected.

    Returns:
        int:
            0 = No predicted network issue
            1 = Predicted network issue

    If return_probability=True:
        returns a dictionary containing both
        prediction and probability.

    If the model is unavailable or no meaningful
    KPI data is supplied, None is returned.
    """

    if not model_available():
        return None

    if not has_meaningful_kpis(
        metrics
    ):
        return None

    try:
        X = prepare_network_features(
            metrics
        )

        prediction = int(
            prediction_model.predict(
                X
            )[0]
        )

        probability = None

        if hasattr(
            prediction_model,
            "predict_proba",
        ):
            probability = float(
                prediction_model.predict_proba(
                    X
                )[0][1]
            )

        if return_probability:
            return {
                "prediction": prediction,
                "probability": probability,
            }

        return prediction

    except Exception as exc:
        print(
            "Network prediction error:",
            exc,
        )

        return None
