from datetime import datetime
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
DATA_PATH = os.path.join(PROJECT_PATH, "data")
NOTI_PATH = os.path.join(UTILS_PATH, "Notifications")

sys.path.insert(0, PROJECT_PATH)
sys.path.insert(0, UTILS_PATH)

utils_pkg = types.ModuleType("utils")
utils_pkg.__path__ = [UTILS_PATH]
sys.modules["utils"] = utils_pkg

importlib.invalidate_caches()

from utils.language_utils import detect_language
from utils.intent_utils import predict_intent
from utils.sentiment_utils import predict_sentiment

from database.db_helper import save_chat_log, fetch_all


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
            return result[0], 1.0

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
            return pd.read_csv(path, encoding="utf-8-sig")
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
def predict_intent_safe(user_message, lang):
    """
    Uses the trained intent model first.
    If the model fails or returns unclear intent like other/unknown,
    fallback rules are used only as backup.
    """

    text = str(user_message).lower().strip()

    try:
        raw = predict_intent(user_message, lang)
        intent, confidence = normalize_model_output(raw, default="unknown")

        intent = normalize_intent(intent)
        confidence = float(confidence)

        print("INTENT MODEL RAW:", raw)
        print("INTENT MODEL OUTPUT:", intent, confidence)

        # إذا المودل رجع intent واضح نستخدمه
        if intent not in ["other", "unknown", "none", "neutral", ""]:
            return intent, confidence

    except Exception as e:
        print("Intent model error:", e)

    # Backup فقط إذا المودل فشل أو رجع other
    if any(w in text for w in ["هاي", "هلا", "مرحبا", "hello", "hi", "hey", "كيفك", "كيفو"]):
        return "greeting", 0.8

    if any(w in text for w in [
        "slow", "slow internet", "internet is slow", "my internet is slow",
        "بطيء", "بطئ", "النت بطيء", "نت بطيء",
        "ضعيف", "ضعيفة", "تقطيع", "سرعة", "السرعة"
    ]):
        return "slow_internet", 0.9

    if any(w in text for w in [
        "signal", "no signal", "ضعف اشارة", "اشارة", "إشارة",
        "ما في اشارة", "مافي اشارة", "فاصل"
    ]):
        return "no_signal", 0.9

    if any(w in text for w in [
        "network status", "status", "حالة الشبكة", "الشبكة"
    ]):
        return "network_status", 0.8

    if any(w in text for w in [
        "complaint", "مشكلة", "شكوى", "سيء", "زفت", "خرا"
    ]):
        return "network_complaint", 0.8

    return "unknown", 0.5
# =========================
# Dynamic Metrics - SQLite
# =========================
def update_dynamic_metrics(user_id, region, intent, issue_type="normal", metrics=None):
    metrics = metrics or {}
    intent = normalize_intent(intent)

    current_is_network = is_network_intent(intent) and issue_type != "normal"

    if not current_is_network:
        metrics["user_id"] = user_id
        metrics["region"] = region
        metrics["repeat_count"] = 0
        metrics["area_issue_count"] = 0
        metrics["current_is_network"] = False
        return metrics

    try:
        rows = fetch_all("""
            SELECT user_id, region, intent, issue_type, network_problem
            FROM chat_logs
            WHERE network_problem = 1
        """)

        repeat = 1
        area = 1

        for row in rows:
            row_user_id = str(row["user_id"])
            row_region = str(row["region"])
            row_intent = normalize_intent(row["intent"])
            row_issue_type = str(row["issue_type"])

            if is_network_intent(row_intent) and row_issue_type != "normal":
                if row_user_id == str(user_id):
                    repeat += 1

                if row_region == str(region):
                    area += 1

    except Exception:
        repeat = 1
        area = 1

    metrics["user_id"] = user_id
    metrics["region"] = region
    metrics["repeat_count"] = repeat
    metrics["area_issue_count"] = area
    metrics["current_is_network"] = True

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
        "customer_message_ar": safe_get(internal_ar, ["customer_notification_ar"]),
        "customer_message_en": safe_get(internal_ar, ["customer_notification_en"]),
        "suggested_action": safe_get(internal_ar, ["suggested_action"]),
        "priority": safe_get(internal_ar, ["priority"]),
        "escalate_after_attempts": safe_int(safe_get(internal_ar, ["escalate_after_attempts"]), default=3),
        "show_to_customer": safe_int(safe_get(internal_ar, ["show_to_customer"]), default=0),
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
    notification_type = "internal_noti"
    display_channel = "employee_dashboard"
    reason = None

    if area >= 5 and show_to_customer == 1:
        escalation = True
        notification_type = "external_noti"
        display_channel = "customer_app"
        reason = "Area-wide issue"

    elif repeat >= escalate_after:
        escalation = True
        notification_type = "internal_noti"
        display_channel = "employee_dashboard"
        reason = "Repeated user issue"

    internal_ar = noti.get("internal_message_ar")
    internal_en = noti.get("internal_message_en")

    if internal_en is None and internal_ar is not None:
        try:
            from deep_translator import GoogleTranslator
            internal_en = GoogleTranslator(source="ar", target="en").translate(internal_ar)
        except Exception:
            internal_en = internal_ar

    external_ar = noti.get("external_message_ar") or noti.get("customer_message_ar")
    external_en = noti.get("external_message_en") or noti.get("customer_message_en")

    return {
        "issue_type": issue_type,
        "network_problem": True,
        "notification_type": notification_type,
        "display_channel": display_channel,
        "escalation": escalation,
        "reason": reason,
        "repeat_count": repeat,
        "area_issue_count": area,
        "external_message_ar": external_ar,
        "external_message_en": external_en,
        "internal_message_ar": internal_ar,
        "internal_message_en": internal_en,
        "priority": noti.get("priority"),
        "suggested_action": noti.get("suggested_action"),
        "show_to_customer": show_to_customer
    }


# =========================
# Responses
# =========================
def get_intent_response(lang, intent):
    intent = normalize_intent(intent)

    if lang == "en":
        if intent == "greeting":
            return "Hello! How can I help you today?", "What would you like to know?"
        if intent == "slow_internet":
            return "I understand, your internet seems slow.", "Would you like us to troubleshoot it together?"
        if intent == "no_signal":
            return "I understand, it looks like there may be a signal issue.", "Can you confirm your selected area?"
        if intent == "network_status":
            return "Let me check the network status for your area.", "Which service are you having trouble with?"
        if intent == "renew_package":

            return "يمكنك تجديد الباقة من التطبيق بسهولة.", "هل تريد تجديد نفس الباقة الحالية؟"
 
        if intent == "check_data_usage":

            return "يمكنك معرفة استهلاك الإنترنت من لوحة التحكم.", "هل تريد معرفة المتبقي من الباقة؟"
 
        if intent == "offer_inquiry":

            return "توجد عروض وباقات متنوعة متاحة حالياً.", "هل تبحث عن عروض إنترنت أم مكالمات؟"
 
        if intent == "technical_support":

            return "تم تحويل طلبك إلى الدعم الفني.", "هل يمكنك شرح المشكلة بشكل أكبر؟"
     
        if intent in ["network_complaint", "complaint"]:
            return "Sorry for the inconvenience. We will follow up on this issue.", "Has this happened more than once?"
        return "Can you explain a little more?", "Tell me more details."

    if intent == "greeting":
        return "هلا وغلا، كيف فيني أساعدك؟", "شو حاب تعرف؟"

    if intent == "slow_internet":
        return "واضح إن النت عندك بطيء.", "بدك نحلها مع بعض؟"

    if intent == "no_signal":
        return "فهمت عليك، واضح في مشكلة بالإشارة.", "تأكد إن المنطقة المختارة صحيحة."

    if intent == "network_status":
        return "خليني أشيك حالة الشبكة عندك.", "أي خدمة عندك فيها مشكلة؟"

    if intent in ["network_complaint", "complaint"]:
        return "آسفين على الإزعاج، رح نتابع المشكلة فوراً.", "صار معك هالشي أكثر من مرة؟"

    return "ممكن توضح أكثر؟", "احكيلي تفاصيل أكثر."


# =========================
# Logging - SQLite
# =========================
def log_chat(user_message, result):
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
    }

    try:
        save_chat_log(row)
    except Exception as e:
        print("SQLite save error:", e)


# =========================
# Main Function
# =========================
def process_message(user_message, metrics=None, user_id="customer_1", region="Amman"):
    lang = detect_language(user_message)

    intent, intent_confidence = predict_intent_safe(user_message, lang)
    sentiment, sentiment_score = predict_sentiment(user_message, lang)

    preliminary_issue_type = map_intent_to_issue_type(intent, sentiment) if is_network_intent(intent) else "normal"

    metrics = update_dynamic_metrics(
        user_id=user_id,
        region=region,
        intent=intent,
        issue_type=preliminary_issue_type,
        metrics=metrics
    )

    prediction = safe_prediction(metrics, intent, sentiment)
    response, followup = get_intent_response(lang, intent)

    notification = notification_engine(
        prediction=prediction,
        sentiment=sentiment,
        metrics=metrics,
        intent=intent
    )

    result = {
        "language": lang,
        "intent": intent,
        "intent_confidence": intent_confidence,
        "sentiment": sentiment,
        "sentiment_score": sentiment_score,
        "prediction": prediction,
        "response": response,
        "followup_response": followup,
        **notification,
        "user_id": user_id,
        "region": region
    }

    log_chat(user_message, result)

    return result
