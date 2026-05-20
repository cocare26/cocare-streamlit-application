import os
import re
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline

# =========================
# Paths
# =========================
try:
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
except:
    BASE_DIR = os.getcwd()

AR_MODEL_PATH = os.path.join(BASE_DIR, "Intent_Ara", "xlmr_intent_model_13_balanced")
EN_MODEL_PATH = os.path.join(BASE_DIR, "intent_Eng")

# =========================
# Text Cleaning
# =========================
def normalize_text(text):
    text = str(text).strip().lower()
    text = re.sub(r"ـ+", "", text)
    text = re.sub(r"[أإآٱ]", "ا", text)
    text = re.sub(r"ى", "ي", text)
    text = re.sub(r"ؤ", "و", text)
    text = re.sub(r"ئ", "ي", text)
    text = re.sub(r"ة", "ه", text)
    text = re.sub(r"[\u0617-\u061A\u064B-\u0652]", "", text)
    text = re.sub(r"[^\u0600-\u06FFa-zA-Z0-9\s_]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def normalize_intent(intent):
    return str(intent).strip().lower()


# =========================
# Rule-based Arabic Override
# =========================
def rule_based_override(text):
    t = normalize_text(text)

    greetings = {
        "مرحبا", "مرحباا", "هلا", "هلااا", "هلا والله", "هلا فيك",
        "ياهلا", "يا هلا وغلا", "اهلا", "اهلين", "اهلين فيك",
        "حي الله", "السلام عليكم", "كيفك", "كيف الحال", "شو الاخبار",
        "hello", "hi", "hey", "كيفو"
    }

    goodbyes = {
        "مع السلامه", "مع السلامة", "باي", "bye", "goodbye", "سلام"
    }

    feedback_words = {
        "شكرا", "شكراً", "مشكور", "يسلمو", "يعطيك العافيه",
        "يعطيك العافية", "thank you", "thanks", "كفو", "ما قصرت"
    }
        # =========================

    # Renew Package

    # =========================

    if re.search(r"(جدد|تجديد|الباقه|الباقة|اشترك|اشتراك)", t):

        return "renew_package"
 
    # =========================

    # Check Data Usage

    # =========================

    if re.search(r"(استهلاك|استهلك|المتبقي|المتبقي لدي|النت المتبقي|البيانات)", t):

        return "check_data_usage"
 
    # =========================

    # Offers Inquiry

    # =========================

    if re.search(r"(العروض|العرض|الالعاب|الألعاب|games|offers)", t):

        return "offer_inquiry"
 
    # =========================

    # International Calls

    # =========================

    if re.search(r"(المكالمات الدوليه|المكالمات الدولية|دوليه|دولية|international)", t):

        return "offer_inquiry"
 
    # =========================

    # Technical Support

    # =========================

    if re.search(r"(الدعم الفني|دعم فني|التواصل مع الدعم|support)", t):

        return "technical_support"

    
    if t in greetings:
        return "greeting"

    if t in goodbyes:
        return "goodbye"

    if t in feedback_words:
        return "feedback"

    if re.search(r"(النت|الانترنت|التصفح|الصفحات).*(بطي|تعبان|بخزي|بعلق|بتعلق|ضعيف|ضعيفة|خرا|زفت|تقطيع|سرعة)", t):
        return "slow_internet"

    if re.search(r"(بطي|تعبان|بخزي|بعلق|بتعلق|ضعيف|ضعيفة|خرا|زفت|تقطيع|سرعة)", t):
        return "slow_internet"

    if re.search(r"(ما في|مافي|لا يوجد|معدومه|معدومة|خارج الخدمه|خارج الخدمة).*(اشاره|اشارة|شبكه|شبكة|تغطيه|تغطية)", t):
        return "no_signal"

    if re.search(r"(حاله|حالة|وضع|شو وضع|افحص|تفحص|تحقق).*(الشبكه|الشبكة|النت|الخدمه|الخدمة)", t):
        return "network_status"

    if re.search(r"(دفعت|دفع|شحن|شحنت|خصم|انخصم|الرصيد|فاتوره|فاتورة).*(ما صار|ما وصل|فشل|مشكله|مشكلة|اختفى|اختفي|ما زبط)", t):
        return "payment_issue"

    if re.search(r"(دعم|تقني|فني|مساعده|مساعدة|اصلح|حل).*(مشكله|مشكلة|خطوه|خطوة)", t):
        return "technical_support"

    return None


# =========================
# Load Models Safely
# =========================
device = 0 if torch.cuda.is_available() else -1

arabic_clf = None
english_clf = None


def load_arabic_model():
    global arabic_clf

    if arabic_clf is None:
        if not os.path.exists(AR_MODEL_PATH):
            raise FileNotFoundError(
                f"Arabic intent model not found at: {AR_MODEL_PATH}. "
                "Make sure the folder Intent_Ara/xlmr_intent_model_13_balanced exists on GitHub."
            )

        tokenizer = AutoTokenizer.from_pretrained(AR_MODEL_PATH)
        model = AutoModelForSequenceClassification.from_pretrained(AR_MODEL_PATH)

        arabic_clf = pipeline(
            "text-classification",
            model=model,
            tokenizer=tokenizer,
            device=device
        )

    return arabic_clf


def load_english_model():
    global english_clf

    if english_clf is None:
        if not os.path.exists(EN_MODEL_PATH):
            return None

        tokenizer = AutoTokenizer.from_pretrained(EN_MODEL_PATH)
        model = AutoModelForSequenceClassification.from_pretrained(EN_MODEL_PATH)

        english_clf = pipeline(
            "text-classification",
            model=model,
            tokenizer=tokenizer,
            device=device
        )

    return english_clf


# =========================
# Main Predict Function
# =========================
def predict_intent(text, lang="ar"):
    text = str(text)
    clean_text = normalize_text(text)

    forced_intent = rule_based_override(text)
    if forced_intent is not None:
        return forced_intent, 0.99

    try:
        if lang == "ar":
            clf = load_arabic_model()
        else:
            clf = load_english_model()

        if clf is None:
            return "other", 0.5

        pred = clf(clean_text, truncation=True)[0]
        intent = normalize_intent(pred.get("label", "other"))
        confidence = float(pred.get("score", 0.5))

        if confidence < 0.40:
            intent = "other"

        return intent, confidence

    except Exception as e:
        print("[INTENT WARNING]", e)

        # fallback بسيط عشان التطبيق ما يوقف
        if any(w in clean_text for w in ["هاي", "هلا", "مرحبا", "hello", "hi", "كيفك", "كيفو"]):
            return "greeting", 0.8

        if any(w in clean_text for w in ["بطي", "ضعيف", "ضعيفة", "خرا", "زفت", "تقطيع", "سرعة"]):
            return "slow_internet", 0.8

        return "other", 0.5
