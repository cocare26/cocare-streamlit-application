from datetime import datetime
import importlib
import os
import sys
import types

import pandas as pd

from database.db_helper import save_chat_log, fetch_all


# ============================================================
# Project Paths
# ============================================================

PROJECT_PATH = os.path.dirname(os.path.abspath(__file__))

UTILS_PATH = os.path.join(PROJECT_PATH, "utils")
DATA_PATH = os.path.join(PROJECT_PATH, "data")
NOTI_PATH = os.path.join(UTILS_PATH, "Notifications")

sys.path.insert(0, PROJECT_PATH)
sys.path.insert(0, UTILS_PATH)

utils_pkg = types.ModuleType("utils")
utils_pkg.__path__ = [UTILS_PATH]
sys.modules["utils"] = utils_pkg

importlib.invalidate_caches()


# ============================================================
# AI Utilities
# ============================================================

from utils.language_utils import detect_language
from utils.intent_utils import predict_intent
from utils.sentiment_utils import predict_sentiment
from utils.prediction_utils import predict_network_issue


# ============================================================
# General Helpers
# ============================================================

def safe_int(value, default=0):
    try:
        if value == "" or pd.isna(value):
            return default

        return int(float(value))

    except (TypeError, ValueError):
        return default


def normalize_model_output(result, default="neutral"):
    """
    Normalize different model output formats into:
    (label, confidence_score)
    """

    try:
        if isinstance(result, tuple):
            if len(result) >= 2:
                return result[0], result[1]

            if len(result) == 1:
                return result[0], 1.0

        if isinstance(result, list):
            if not result:
                return default, 1.0

            if isinstance(result[0], dict):
                return (
                    result[0].get("label", default),
                    result[0].get("score", 1.0),
                )

            return result[0], 1.0

        if isinstance(result, dict):
            return (
                result.get("label", default),
                result.get("score", 1.0),
            )

        return result, 1.0

    except Exception:
        return default, 1.0


def normalize_sentiment(sentiment):
    sentiment = str(sentiment).strip().lower()

    if sentiment in ["negative", "label_0", "0", "neg"]:
        return "negative"

    if sentiment in ["positive", "label_2", "2", "pos"]:
        return "positive"

    return "neutral"


def normalize_intent(intent):
    intent = str(intent).strip().lower()

    mapping = {
        "slow internet": "slow_internet",
        "slow-internet": "slow_internet",

        "no signal": "no_signal",
        "no-signal": "no_signal",

        "network complaint": "network_complaint",

        "network status": "network_status",
        "network-status": "network_status",

        "check data usage": "check_data_usage",
        "data usage": "check_data_usage",

        "renew package": "renew_package",
        "package renewal": "renew_package",

        "offer inquiry": "offer_inquiry",

        "technical support": "technical_support",
    }

    return mapping.get(intent, intent)


def is_network_intent(intent):
    intent = normalize_intent(intent)

    return intent in [
        "slow_internet",
        "no_signal",
        "network_status",
        "network_complaint",
        "complaint",
    ]


def map_intent_to_issue_type(intent, sentiment=None):
    intent = normalize_intent(intent)

    if intent == "slow_internet":
        return "high_latency"

    if intent == "no_signal":
        return "weak_signal"

    if intent == "network_status":
        return "service_degradation"

    if intent in ["network_complaint", "complaint"]:
        return "unstable_connection"

    return "prediction_alert"


# ============================================================
# Notification Data
# ============================================================

def load_notifications():

    def read_csv_safe(path):
        try:
            if not os.path.exists(path):
                print(f"Notification file not found: {path}")
                return pd.DataFrame()

            return pd.read_csv(
                path,
                encoding="utf-8-sig"
            )

        except Exception as exc:
            print(f"Notification CSV error: {path}")
            print(exc)

            return pd.DataFrame()

    internal_ar = read_csv_safe(
        os.path.join(
            NOTI_PATH,
            "internal_notifications.csv",
        )
    )

    internal_en = read_csv_safe(
        os.path.join(
            NOTI_PATH,
            "internal_notifications_en.csv",
        )
    )

    external_ar = read_csv_safe(
        os.path.join(
            NOTI_PATH,
            "external_notifications.csv",
        )
    )

    external_en = read_csv_safe(
        os.path.join(
            NOTI_PATH,
            "external_notifications_en.csv",
        )
    )

    return (
        internal_ar,
        internal_en,
        external_ar,
        external_en,
    )


(
    INTERNAL_AR,
    INTERNAL_EN,
    EXTERNAL_AR,
    EXTERNAL_EN,
) = load_notifications()


# ============================================================
# Intent Classification
# ============================================================

def predict_intent_safe(user_message, lang):
    """
    Use the trained Intent Classification model first.

    Fallback rules are used only if the trained model fails
    or returns an unclear intent.
    """

    text = str(user_message).lower().strip()

    try:
        raw = predict_intent(
            user_message,
            lang,
        )

        intent, confidence = normalize_model_output(
            raw,
            default="unknown",
        )

        intent = normalize_intent(intent)

        try:
            confidence = float(confidence)

        except (TypeError, ValueError):
            confidence = 0.0

        if intent not in [
            "other",
            "unknown",
            "none",
            "neutral",
            "",
        ]:
            return intent, confidence

    except Exception as exc:
        print("Intent model error:", exc)

    if any(
        word in text
        for word in [
            "هاي",
            "هلا",
            "مرحبا",
            "hello",
            "hi",
            "hey",
            "كيفك",
            "كيفو",
        ]
    ):
        return "greeting", 0.80

    if any(
        word in text
        for word in [
            "slow",
            "slow internet",
            "internet is slow",
            "my internet is slow",
            "بطيء",
            "بطئ",
            "النت بطيء",
            "نت بطيء",
            "ضعيف",
            "ضعيفة",
            "تقطيع",
            "سرعة",
            "السرعة",
        ]
    ):
        return "slow_internet", 0.90

    if any(
        word in text
        for word in [
            "signal",
            "no signal",
            "ضعف اشارة",
            "اشارة",
            "إشارة",
            "ما في اشارة",
            "مافي اشارة",
            "فاصل",
        ]
    ):
        return "no_signal", 0.90

    if any(
        word in text
        for word in [
            "network status",
            "حالة الشبكة",
            "الشبكة",
        ]
    ):
        return "network_status", 0.80

    if any(
        word in text
        for word in [
            "complaint",
            "مشكلة",
            "شكوى",
            "سيء",
            "ضعيف",
            "غير مستقر",
        ]
    ):
        return "network_complaint", 0.80

    return "unknown", 0.50


# ============================================================
# Sentiment Analysis
# ============================================================

def predict_sentiment_safe(user_message, lang):
    """
    Use the trained sentiment model while normalizing
    different possible output formats.
    """

    try:
        raw = predict_sentiment(
            user_message,
            lang,
        )

        sentiment, score = normalize_model_output(
            raw,
            default="neutral",
        )

        sentiment = normalize_sentiment(
            sentiment
        )

        try:
            score = float(score)

        except (TypeError, ValueError):
            score = 0.0

        return sentiment, score

    except Exception as exc:
        print("Sentiment model error:", exc)

        return "neutral", 0.0


# ============================================================
# Dynamic Network Metrics - SQLite
# ============================================================

def update_dynamic_metrics(
    user_id,
    region,
    intent,
    issue_type="normal",
    metrics=None,
):

    metrics = metrics or {}

    intent = normalize_intent(intent)

    current_is_network = (
        is_network_intent(intent)
        and issue_type != "normal"
    )

    if not current_is_network:
        metrics.update(
            {
                "user_id": user_id,
                "region": region,
                "repeat_count": 0,
                "area_issue_count": 0,
                "current_is_network": False,
            }
        )

        return metrics

    try:
        rows = fetch_all(
            """
            SELECT
                user_id,
                region,
                intent,
                issue_type,
                network_problem
            FROM chat_logs
            WHERE network_problem = 1
            """
        )

        repeat_count = 1
        area_issue_count = 1

        for row in rows:

            row_user_id = str(
                row["user_id"]
            )

            row_region = str(
                row["region"]
            )

            row_intent = normalize_intent(
                row["intent"]
            )

            row_issue_type = str(
                row["issue_type"]
            )

            if (
                is_network_intent(row_intent)
                and row_issue_type != "normal"
            ):

                if row_user_id == str(user_id):
                    repeat_count += 1

                if row_region == str(region):
                    area_issue_count += 1

    except Exception as exc:
        print(
            "Dynamic metrics database error:",
            exc,
        )

        repeat_count = 1
        area_issue_count = 1

    metrics.update(
        {
            "user_id": user_id,
            "region": region,
            "repeat_count": repeat_count,
            "area_issue_count": area_issue_count,
            "current_is_network": True,
        }
    )

    return metrics


# ============================================================
# Network Prediction
# ============================================================

def safe_prediction(
    metrics,
    intent=None,
    sentiment=None,
):
    """
    Use the trained XGBoost model when compatible telecom KPI data
    is available.

    If KPI data is unavailable, fall back to the prototype
    rule-based network detection logic.
    """

    if not metrics.get(
        "current_is_network",
        False,
    ):
        return 0

    try:
        model_prediction = predict_network_issue(
            metrics
        )

        if model_prediction is not None:
            return int(model_prediction)

    except Exception as exc:
        print(
            "XGBoost prediction error:",
            exc,
        )

    if is_network_intent(intent):
        return 1

    return 0


# ============================================================
# Notification Selection
# ============================================================

def get_notification_message(
    issue_type,
    severity="medium",
):

    def filter_df(df):

        if (
            df.empty
            or "issue_type" not in df.columns
        ):
            return pd.DataFrame()

        temp = df[
            df["issue_type"].astype(str)
            == str(issue_type)
        ]

        if (
            not temp.empty
            and "severity" in temp.columns
        ):

            severity_rows = temp[
                temp["severity"].astype(str)
                == str(severity)
            ]

            if not severity_rows.empty:
                return severity_rows

        return temp

    def safe_get(df, columns):

        if df.empty:
            return None

        for column in columns:

            if column not in df.columns:
                continue

            value = df.iloc[0].get(
                column
            )

            if not pd.isna(value):
                return value

        return None

    internal_ar = filter_df(
        INTERNAL_AR
    )

    internal_en = filter_df(
        INTERNAL_EN
    )

    external_ar = filter_df(
        EXTERNAL_AR
    )

    external_en = filter_df(
        EXTERNAL_EN
    )

    return {
        "internal_message_ar": safe_get(
            internal_ar,
            [
                "employee_notification_ar",
                "internal_message_ar",
            ],
        ),

        "internal_message_en": safe_get(
            internal_en,
            [
                "employee_notification_en",
                "internal_message_en",
            ],
        ),

        "external_message_ar": safe_get(
            external_ar,
            [
                "customer_notification_ar",
                "external_message_ar",
            ],
        ),

        "external_message_en": safe_get(
            external_en,
            [
                "customer_notification_en",
                "external_message_en",
            ],
        ),

        "customer_message_ar": safe_get(
            external_ar,
            [
                "customer_notification_ar",
            ],
        ),

        "customer_message_en": safe_get(
            external_en,
            [
                "customer_notification_en",
            ],
        ),

        "suggested_action": safe_get(
            internal_ar,
            [
                "suggested_action",
            ],
        ),

        "priority": safe_get(
            internal_ar,
            [
                "priority",
            ],
        ),

        "escalate_after_attempts": safe_int(
            safe_get(
                internal_ar,
                ["escalate_after_attempts"],
            ),
            default=3,
        ),

        "show_to_customer": safe_int(
            safe_get(
                external_ar,
                ["show_to_customer"],
            ),
            default=0,
        ),
    }


# ============================================================
# Notification & Escalation Engine
# ============================================================

def notification_engine(
    prediction,
    sentiment,
    metrics=None,
    intent=None,
):

    metrics = metrics or {}

    repeat_count = safe_int(
        metrics.get("repeat_count")
    )

    area_issue_count = safe_int(
        metrics.get(
            "area_issue_count"
        )
    )

    if (
        prediction == 0
        or not metrics.get(
            "current_is_network",
            False,
        )
    ):

        return {
            "issue_type": "normal",
            "network_problem": False,
            "notification_type": "none",
            "display_channel": "none",
            "escalation": False,
            "reason": None,
            "repeat_count": 0,
            "area_issue_count": 0,
            "external_message_ar": None,
            "external_message_en": None,
            "internal_message_ar": None,
            "internal_message_en": None,
            "priority": None,
            "suggested_action": None,
            "show_to_customer": 0,
        }

    issue_type = map_intent_to_issue_type(
        intent,
        sentiment,
    )

    severity = "medium"

    if sentiment == "negative":
        severity = "high"

    notification = get_notification_message(
        issue_type,
        severity,
    )

    escalate_after = safe_int(
        notification.get(
            "escalate_after_attempts"
        ),
        default=3,
    )

    show_to_customer = safe_int(
        notification.get(
            "show_to_customer"
        ),
        default=0,
    )

    escalation = False

    notification_type = "internal_noti"

    display_channel = (
        "employee_dashboard"
    )

    reason = (
        "Network issue detected"
    )

    if (
        area_issue_count >= 5
        and show_to_customer == 1
    ):

        escalation = True

        notification_type = (
            "external_noti"
        )

        display_channel = (
            "customer_app"
        )

        reason = "Area-wide issue"

    elif repeat_count >= escalate_after:

        escalation = True

        notification_type = (
            "internal_noti"
        )

        display_channel = (
            "employee_dashboard"
        )

        reason = (
            "Repeated user issue"
        )

    internal_ar = notification.get(
        "internal_message_ar"
    )

    internal_en = notification.get(
        "internal_message_en"
    )

    external_ar = (
        notification.get(
            "external_message_ar"
        )
        or notification.get(
            "customer_message_ar"
        )
    )

    external_en = (
        notification.get(
            "external_message_en"
        )
        or notification.get(
            "customer_message_en"
        )
    )

    return {
        "issue_type": issue_type,
        "network_problem": True,
        "notification_type": notification_type,
        "display_channel": display_channel,
        "escalation": escalation,
        "reason": reason,
        "repeat_count": repeat_count,
        "area_issue_count": area_issue_count,
        "external_message_ar": external_ar,
        "external_message_en": external_en,
        "internal_message_ar": internal_ar,
        "internal_message_en": internal_en,
        "priority": notification.get(
            "priority"
        ),
        "suggested_action": notification.get(
            "suggested_action"
        ),
        "show_to_customer": show_to_customer,
    }


# ============================================================
# Chatbot Responses
# ============================================================

def get_intent_response(
    lang,
    intent,
    sentiment="neutral",
):

    intent = normalize_intent(intent)

    if lang == "en":

        negative_prefix = ""

        if sentiment == "negative":
            negative_prefix = (
                "Sorry for the inconvenience. "
            )

        responses = {

            "greeting": (
                "Hello! How can I help you today?",
                "What would you like to know?",
            ),

            "slow_internet": (
                negative_prefix
                + "It looks like your internet connection may be slow.",
                "Would you like us to troubleshoot it together?",
            ),

            "no_signal": (
                negative_prefix
                + "It looks like there may be a signal issue.",
                "Can you confirm your selected area?",
            ),

            "network_status": (
                "Let me check the network status for your area.",
                "Which service are you having trouble with?",
            ),

            "network_complaint": (
                negative_prefix
                + "Your network complaint has been registered.",
                "Has this issue happened more than once?",
            ),

            "complaint": (
                negative_prefix
                + "Your complaint has been registered.",
                "Has this issue happened more than once?",
            ),

            "renew_package": (
                "You can easily renew your package through the application.",
                "Would you like to renew your current package?",
            ),

            "check_data_usage": (
                "You can check your internet usage from the customer dashboard.",
                "Would you like to check your remaining data?",
            ),

            "offer_inquiry": (
                "Several telecom offers and packages are currently available.",
                "Are you looking for internet or call offers?",
            ),

            "technical_support": (
                "Your request has been referred to technical support.",
                "Could you provide more details about the issue?",
            ),

            "payment_issue": (
                "It looks like there may be an issue with your payment.",
                "Please verify your payment information and try again.",
            ),
        }

        return responses.get(
            intent,
            (
                "Could you please explain your request in more detail?",
                "Tell me more about how I can help.",
            ),
        )

    negative_prefix = ""

    if sentiment == "negative":
        negative_prefix = (
            "آسفين على الإزعاج. "
        )

    responses = {

        "greeting": (
            "هلا وغلا، كيف فيني أساعدك؟",
            "شو حاب تعرف؟",
        ),

        "slow_internet": (
            negative_prefix
            + "واضح إن سرعة الإنترنت عندك فيها مشكلة.",
            "بدك نتابع المشكلة مع بعض؟",
        ),

        "no_signal": (
            negative_prefix
            + "واضح إن في مشكلة بالإشارة.",
            "تأكد إن المنطقة المختارة صحيحة.",
        ),

        "network_status": (
            "خليني أشيك حالة الشبكة عندك.",
            "أي خدمة عندك فيها مشكلة؟",
        ),

        "network_complaint": (
            negative_prefix
            + "تم تسجيل شكوى الشبكة وسنتابع المشكلة.",
            "صار معك هالشي أكثر من مرة؟",
        ),

        "complaint": (
            negative_prefix
            + "تم تسجيل ملاحظتك وسنتابع المشكلة.",
            "صار معك هالشي أكثر من مرة؟",
        ),

        "renew_package": (
            "يمكنك تجديد الباقة بسهولة من التطبيق.",
            "هل تريد تجديد نفس الباقة الحالية؟",
        ),

        "check_data_usage": (
            "يمكنك معرفة استهلاك الإنترنت من لوحة التحكم.",
            "هل تريد معرفة المتبقي من الباقة؟",
        ),

        "offer_inquiry": (
            "توجد عروض وباقات متنوعة متاحة حالياً.",
            "هل تبحث عن عروض إنترنت أم مكالمات؟",
        ),

        "technical_support": (
            "تم تحويل طلبك إلى الدعم الفني.",
            "هل يمكنك توضيح المشكلة بشكل أكبر؟",
        ),

        "payment_issue": (
            "يبدو أن هناك مشكلة في عملية الدفع.",
            "تأكد من معلومات الدفع وحاول مرة أخرى.",
        ),
    }

    return responses.get(
        intent,
        (
            "ممكن توضح طلبك أكثر؟",
            "احكيلي تفاصيل أكثر حتى أقدر أساعدك.",
        ),
    )


# ============================================================
# Chat Logging - SQLite
# ============================================================

def log_chat(
    user_message,
    result,
):

    row = {

        "timestamp": datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        ),

        "user_id": result.get(
            "user_id"
        ),

        "region": result.get(
            "region"
        ),

        "message": user_message,

        "language": result.get(
            "language"
        ),

        "intent": result.get(
            "intent"
        ),

        "intent_confidence": result.get(
            "intent_confidence"
        ),

        "sentiment": result.get(
            "sentiment"
        ),

        "sentiment_score": result.get(
            "sentiment_score"
        ),

        "prediction": result.get(
            "prediction"
        ),

        "issue_type": result.get(
            "issue_type"
        ),

        "network_problem": result.get(
            "network_problem"
        ),

        "notification_type": result.get(
            "notification_type"
        ),

        "display_channel": result.get(
            "display_channel"
        ),

        "escalation": result.get(
            "escalation"
        ),

        "reason": result.get(
            "reason"
        ),

        "repeat_count": result.get(
            "repeat_count"
        ),

        "area_issue_count": result.get(
            "area_issue_count"
        ),
    }

    try:
        save_chat_log(row)

    except Exception as exc:
        print(
            "SQLite save error:",
            exc,
        )


# ============================================================
# Main CoCare Processing Pipeline
# ============================================================

def process_message(
    user_message,
    metrics=None,
    user_id="customer_1",
    region="Unknown",
):

    try:
        lang = detect_language(
            user_message
        )

    except Exception as exc:
        print(
            "Language detection error:",
            exc,
        )

        lang = "en"

    (
        intent,
        intent_confidence,
    ) = predict_intent_safe(
        user_message,
        lang,
    )

    (
        sentiment,
        sentiment_score,
    ) = predict_sentiment_safe(
        user_message,
        lang,
    )

    if is_network_intent(intent):

        preliminary_issue_type = (
            map_intent_to_issue_type(
                intent,
                sentiment,
            )
        )

    else:
        preliminary_issue_type = (
            "normal"
        )

    metrics = update_dynamic_metrics(
        user_id=user_id,
        region=region,
        intent=intent,
        issue_type=preliminary_issue_type,
        metrics=metrics,
    )

    prediction = safe_prediction(
        metrics=metrics,
        intent=intent,
        sentiment=sentiment,
    )

    (
        response,
        followup_response,
    ) = get_intent_response(
        lang=lang,
        intent=intent,
        sentiment=sentiment,
    )

    notification = notification_engine(
        prediction=prediction,
        sentiment=sentiment,
        metrics=metrics,
        intent=intent,
    )

    result = {

        "language": lang,

        "intent": intent,

        "intent_confidence": float(
            intent_confidence
        ),

        "sentiment": sentiment,

        "sentiment_score": float(
            sentiment_score
        ),

        "prediction": int(
            prediction
        ),

        "response": response,

        "followup_response": (
            followup_response
        ),

        **notification,

        "user_id": user_id,

        "region": region,
    }

    log_chat(
        user_message,
        result,
    )

    return result
