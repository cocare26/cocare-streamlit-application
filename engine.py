from datetime import datetime, timedelta
import os
import sys
import types
import importlib
import pandas as pd

# =========================
# Project Paths
# =========================
PROJECT_PATH = os.path.dirname(os.path.abspath(__file__))
UTILS_PATH = os.path.join(PROJECT_PATH, "utils")

sys.path.insert(0, PROJECT_PATH)
sys.path.insert(0, UTILS_PATH)

utils_pkg = types.ModuleType("utils")
utils_pkg.__path__ = [UTILS_PATH]
sys.modules["utils"] = utils_pkg
importlib.invalidate_caches()

# =========================
# Safe Imports
# =========================
try:
    from utils.language_utils import detect_language
except:
    def detect_language(text):
        text = str(text)
        arabic_chars = any("\u0600" <= ch <= "\u06FF" for ch in text)
        return "ar" if arabic_chars else "en"

try:
    from utils.intent_utils import predict_intent
except:
    predict_intent = None

try:
    from utils.sentiment_utils import predict_sentiment
except:
    predict_sentiment = None

# =========================
# Files Paths
# =========================
CHAT_LOG_PATH = os.path.join(PROJECT_PATH, "data", "chat_logs.csv")
NOTI_PATH = os.path.join(PROJECT_PATH, "utils", "Notifications")


# =========================
# Helpers
# =========================
def safe_int(value, default=0):
    try:
        if value == "" or pd.isna(value):
            return default
        return int(float(value))
    except:
        return default


def normalize_model_output(result, default="neutral"):
    try:
        if isinstance(result, tuple):
            if len(result) == 2:
                return result[0], result[1]
            return result[0], 1.0

        if isinstance(result, list):
            if len(result) > 0 and isinstance(result[0], dict):
                return result[0].get("label", default), result[0].get("score", 1.0)
            if len(result) > 0:
                return result[0], 1.0
            return default, 1.0

        if isinstance(result, dict):
            return result.get("label", default), result.get("score", 1.0)

        return result, 1.0
    except:
        return default, 1.0


def normalize_sentiment(s):
    s = str(s).strip().lower()

    if s in ["negative", "label_0", "0", "neg"]:
        return "negative"
    if s in ["positive", "label_2", "2", "pos"]:
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
        "other": "unknown",
        "others": "unknown",
        "general": "unknown",
    }

    return mapping.get(intent, intent)


def is_network_intent(intent):
    intent = normalize_intent(intent)
    return intent in [
        "slow_internet",
        "no_signal",
        "network_status",
        "network_complaint",
        "complaint"
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


# =========================
# Load Notifications
# =========================
def load_notifications():
    def read_csv_safe(path):
        try:
            if os.path.exists(path):
                return pd.read_csv(path, encoding="utf-8-sig")
            print(f"CSV not found: {path}")
            return pd.DataFrame()
        except Exception as e:
            print(f"CSV load error: {path}")
            print(e)
            return pd.DataFrame()

    internal_ar = read_csv_safe(os.path.join(NOTI_PATH, "internal_notifications.csv"))
    internal_en = read_csv_safe(os.path.join(NOTI_PATH, "internal_notifications_en.csv"))
    external_ar = read_csv_safe(os.path.join(NOTI_PATH, "external_notifications.csv"))
    external_en = read_csv_safe(os.path.join(NOTI_PATH, "external_notifications_en.csv"))

    return internal_ar, internal_en, external_ar, external_en


INTERNAL_AR, INTERNAL_EN, EXTERNAL_AR, EXTERNAL_EN = load_notifications()


# =========================
# Safe Models
# =========================
def predict_intent_safe(user_message, lang="en"):
    try:
        if predict_intent is not None:
            raw = predict_intent(user_message, lang)
            intent, confidence = normalize_model_output(raw, default="unknown")
            return normalize_intent(intent), confidence
    except Exception as e:
        print("Intent model error:", e)

    text = str(user_message).lower()

    if any(w in text for w in ["هاي", "هلا", "مرحبا", "hello", "hi", "كيفك"]):
        return "greeting", 0.8

    if any(w in text for w in ["بطيء", "ضعيف", "ضعيفة", "slow", "تقطيع", "سرعة]):
        return "slow_internet", 0.8

    if any(w in text for w in ["اشارة", "إشارة", "signal", "فاصل", "no signal"]):
        return "no_signal", 0.8

    if any(w in text for w in ["network", "complaint", "مشكلة", "شكوى"]):
        return "network_complaint", 0.7

    return "unknown", 0.5


def predict_sentiment_safe(user_message, lang="en"):
    try:
        if predict_sentiment is not None:
            raw = predict_sentiment(user_message, lang)
            label, score = normalize_model_output(raw)
            return normalize_sentiment(label), score
    except Exception as e:
        print("Sentiment model error:", e)

    text = str(user_message).lower()

    if any(w in text for w in ["سيء", "بطيء", "ضعيف", "ضعيفة", "تخزي", "مشكلة", "bad", "slow", "angry"]):
        return "negative", 0.9

    if any(w in text for w in ["ممتاز", "تمام", "شكرا", "يسلمو", "good", "great", "thanks"]):
        return "positive", 0.8

    return "neutral", 0.5


# =========================
# Chat Log Cleanup 48 Hours
# =========================
def cleanup_old_logs():
    try:
        if not os.path.exists(CHAT_LOG_PATH):
            return

        logs = pd.read_csv(CHAT_LOG_PATH, encoding="utf-8-sig")

        if logs.empty or "timestamp" not in logs.columns:
            return

        logs["timestamp_dt"] = pd.to_datetime(logs["timestamp"], errors="coerce")
        cutoff = datetime.now() - timedelta(hours=48)

        logs = logs[logs["timestamp_dt"] >= cutoff]
        logs = logs.drop(columns=["timestamp_dt"], errors="ignore")

        logs.to_csv(CHAT_LOG_PATH, index=False, encoding="utf-8-sig")
    except Exception as e:
        print("Cleanup logs error:", e)


# =========================
# Dynamic Metrics
# =========================
def update_dynamic_metrics(user_id, region, intent, issue_type="normal", metrics=None):
    metrics = metrics or {}
    intent = normalize_intent(intent)

    current_is_network = is_network_intent(intent) and issue_type != "normal"

    if not current_is_network:
        metrics.update({
            "user_id": user_id,
            "region": region,
            "repeat_count": 0,
            "area_issue_count": 0,
            "current_is_network": False
        })
        return metrics

    cleanup_old_logs()

    try:
        logs = pd.read_csv(CHAT_LOG_PATH, encoding="utf-8-sig")
    except:
        logs = pd.DataFrame()

    if logs.empty:
        repeat = 1
        area = 1
    else:
        for col in ["user_id", "region", "intent", "issue_type", "network_problem"]:
            if col not in logs.columns:
                logs[col] = None

        logs["intent"] = logs["intent"].astype(str).apply(normalize_intent)
        logs["issue_type"] = logs["issue_type"].astype(str)
        logs["network_problem"] = logs["network_problem"].astype(str).str.lower()

        network_logs = logs[
            (logs["intent"].apply(is_network_intent)) &
            (logs["issue_type"] != "normal") &
            (logs["network_problem"].isin(["true", "1", "yes"]))
        ]

        repeat = len(network_logs[network_logs["user_id"].astype(str) == str(user_id)]) + 1
        area = len(network_logs[network_logs["region"].astype(str) == str(region)]) + 1

    metrics.update({
        "user_id": user_id,
        "region": region,
        "repeat_count": repeat,
        "area_issue_count": area,
        "current_is_network": True
    })

    return metrics


def safe_prediction(metrics, intent=None, sentiment=None):
    if not metrics.get("current_is_network", False):
        return 0

    if is_network_intent(intent):
        return 1

    return 0


# =========================
# Notification Picker
# =========================
def get_notification_message(issue_type, severity="medium"):
    def filter_df(df):
        if df.empty or "issue_type" not in df.columns:
            return pd.DataFrame()

        temp = df[df["issue_type"].astype(str) == str(issue_type)]

        if not temp.empty and "severity" in temp.columns:
            sev_temp = temp[temp["severity"].astype(str) == str(severity)]
            if not sev_temp.empty:
                return sev_temp

        return temp

    def safe_get(df, cols):
        if df.empty:
            return None

        for col in cols:
            if col in df.columns:
                value = df.iloc[0].get(col)
                if not pd.isna(value):
                    return value

        return None

    internal_ar = filter_df(INTERNAL_AR)
    internal_en = filter_df(INTERNAL_EN)
    external_ar = filter_df(EXTERNAL_AR)
    external_en = filter_df(EXTERNAL_EN)

    return {
        "internal_message_ar": safe_get(internal_ar, ["employee_notification_ar", "internal_message_ar"]),
        "internal_message_en": safe_get(internal_en, ["employee_notification_en", "internal_message_en"]),
        "external_message_ar": safe_get(external_ar, ["customer_notification_ar", "external_message_ar"]),
        "external_message_en": safe_get(external_en, ["customer_notification_en", "external_message_en"]),
        "customer_message_ar": safe_get(external_ar, ["customer_notification_ar"]),
        "customer_message_en": safe_get(external_en, ["customer_notification_en"]),
        "suggested_action": safe_get(internal_ar, ["suggested_action"]),
        "priority": safe_get(internal_ar, ["priority"]),
        "escalate_after_attempts": safe_int(safe_get(internal_ar, ["escalate_after_attempts"]), default=3),
        "show_to_customer": safe_int(safe_get(external_ar, ["show_to_customer"]), default=0),
    }


# =========================
# Notification Engine
# =========================
def notification_engine(prediction, sentiment, metrics=None, intent=None):
    metrics = metrics or {}

    repeat = safe_int(metrics.get("repeat_count"))
    area = safe_int(metrics.get("area_issue_count"))

    if prediction == 0 or not metrics.get("current_is_network", False):
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
            "show_to_customer": 0
        }

    issue_type = map_intent_to_issue_type(intent, sentiment)
    severity = "medium"

    noti = get_notification_message(issue_type, severity)

    escalate_after = safe_int(noti.get("escalate_after_attempts"), default=3)
    show_to_customer = safe_int(noti.get("show_to_customer"), default=0)

    escalation = False
    notification_type = "external_noti"
    display_channel = "customer_app"
    reason = "Network problem detected"

    if repeat >= escalate_after:
        escalation = True
        notification_type = "internal_noti"
        display_channel = "employee_dashboard"
        reason = "Repeated user issue"

    if area >= 5 and show_to_customer == 1:
        escalation = True
        notification_type = "external_noti"
        display_channel = "customer_app"
        reason = "Area-wide issue"

    return {
        "issue_type": issue_type,
        "network_problem": True,
        "notification_type": notification_type,
        "display_channel": display_channel,
        "escalation": escalation,
        "reason": reason,
        "repeat_count": repeat,
        "area_issue_count": area,
        "external_message_ar": noti.get("external_message_ar") or noti.get("customer_message_ar"),
        "external_message_en": noti.get("external_message_en") or noti.get("customer_message_en"),
        "internal_message_ar": noti.get("internal_message_ar"),
        "internal_message_en": noti.get("internal_message_en"),
        "priority": noti.get("priority"),
        "suggested_action": noti.get("suggested_action"),
        "show_to_customer": show_to_customer
    }


# =========================
# Responses
# =========================
def get_intent_response(lang, intent, sentiment="neutral"):
    intent = normalize_intent(intent)

    if lang == "ar":
        if sentiment == "negative":
            prefix = "آسفين جداً على الإزعاج، "
        else:
            prefix = ""

        responses = {
            "greeting": ("هلا وغلا، كيف فيني أساعدك؟", "شو حاب تعرف؟"),
            "slow_internet": (prefix + "واضح إن النت عندك بطيء.", "خلينا نتابعها مع بعض، هل المشكلة مستمرة الآن؟"),
            "no_signal": (prefix + "فهمت عليك، واضح في مشكلة بالإشارة.", "هل الإشارة ضعيفة بكل الأماكن ولا بمكان معين؟"),
            "network_status": ("خليني أشيك حالة الشبكة عندك.", "أي منطقة موجود فيها؟"),
            "network_complaint": (prefix + "تم تسجيل ملاحظتك وسنتابع المشكلة.", "صار معك هالشي أكثر من مرة؟"),
            "complaint": (prefix + "تم تسجيل ملاحظتك وسنتابع المشكلة.", "صار معك هالشي أكثر من مرة؟"),
            "payment_issue": ("واضح عندك مشكلة بالدفع.", "تأكد من بيانات الدفع وجرب مرة ثانية."),
            "check_data_usage": ("بتقدر تشيك استهلاك الإنترنت من لوحة التحكم.", "حاب أساعدك بخطوة ثانية؟"),
            "renew_package": ("بتقدر تجدد الباقة من قسم الباقات.", "حاب أشرحلك الخطوات؟"),
            "offer_inquiry": ("أكيد، بتقدر تشوف العروض المتاحة من قسم العروض.", "بدك عروض إنترنت ولا مكالمات؟"),
        }

        return responses.get(intent, ("ممكن توضح أكثر؟", "احكيلي تفاصيل أكثر"))

    else:
        if sentiment == "negative":
            prefix = "Sorry for the inconvenience. "
        else:
            prefix = ""

        responses = {
            "greeting": ("Hello, how can I help you?", "What would you like to know?"),
            "slow_internet": (prefix + "It looks like your internet is slow.", "Is the issue still happening now?"),
            "no_signal": (prefix + "It seems there may be a signal issue.", "Is the signal weak everywhere or only in one place?"),
            "network_status": ("I’ll check the current network status for you.", "Which area are you in?"),
            "network_complaint": (prefix + "Your network complaint has been noted.", "Has this happened more than once?"),
            "complaint": (prefix + "Your complaint has been noted.", "Has this happened more than once?"),
            "payment_issue": ("It looks like there is a payment issue.", "Please check your payment details and try again."),
            "check_data_usage": ("You can check your data usage from your dashboard.", "Would you like help with anything else?"),
            "renew_package": ("You can renew your package from the packages section.", "Would you like the steps?"),
            "offer_inquiry": ("Sure, you can check available offers from the offers section.", "Are you looking for internet or call offers?"),
        }

        return "Could you please explain more?", "Tell me more details."


# =========================
# Logging
# =========================
def log_chat(user_message, result):
    cleanup_old_logs()
    os.makedirs(os.path.dirname(CHAT_LOG_PATH), exist_ok=True)

    row = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "user_id": result.get("user_id"),
        "region": result.get("region"),
        "message": user_message,
        "language": result.get("language"),
        "intent": result.get("intent"),
        "intent_confidence": result.get("intent_confidence"),
        "sentiment": result.get("sentiment"),
        "sentiment_score": result.get("sentiment_score"),
        "prediction": result.get("prediction"),
        "issue_type": result.get("issue_type"),
        "network_problem": result.get("network_problem"),
        "notification_type": result.get("notification_type"),
        "display_channel": result.get("display_channel"),
        "escalation": result.get("escalation"),
        "reason": result.get("reason"),
        "repeat_count": result.get("repeat_count"),
        "area_issue_count": result.get("area_issue_count"),
        "priority": result.get("priority"),
        "suggested_action": result.get("suggested_action"),
        "show_to_customer": result.get("show_to_customer"),
    }

    try:
        old = pd.read_csv(CHAT_LOG_PATH, encoding="utf-8-sig")
        logs = pd.concat([old, pd.DataFrame([row])], ignore_index=True)
    except:
        logs = pd.DataFrame([row])

    logs.to_csv(CHAT_LOG_PATH, index=False, encoding="utf-8-sig")


# =========================
# Main Function
# =========================
def process_message(user_message, metrics=None, user_id="customer_1", region="Unknown"):
    try:
        lang = detect_language(user_message)
    except:
        lang = "ar"

    intent, intent_confidence = predict_intent_safe(user_message, lang)
    sentiment, sentiment_score = predict_sentiment_safe(user_message, lang)

    preliminary_issue_type = map_intent_to_issue_type(intent, sentiment) if is_network_intent(intent) else "normal"

    metrics = update_dynamic_metrics(
        user_id=user_id,
        region=region,
        intent=intent,
        issue_type=preliminary_issue_type,
        metrics=metrics
    )

    prediction = safe_prediction(metrics, intent, sentiment)

    response, followup = get_intent_response(
        lang=lang,
        intent=intent,
        sentiment=sentiment
    )

    notification = notification_engine(
        prediction=prediction,
        sentiment=sentiment,
        metrics=metrics,
        intent=intent
    )

    result = {
        "language": lang,
        "intent": intent,
        "intent_confidence": float(intent_confidence),
        "sentiment": sentiment,
        "sentiment_score": float(sentiment_score),
        "prediction": int(prediction),
        "response": response,
        "followup_response": followup,
        **notification,
        "user_id": user_id,
        "region": region
    }

    log_chat(user_message, result)

    return result
