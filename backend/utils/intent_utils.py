import os
import re

import torch
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    pipeline,
)


# ============================================================
# Project Paths
# ============================================================

UTILS_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

BACKEND_DIR = os.path.dirname(
    UTILS_DIR
)

PROJECT_ROOT = os.path.dirname(
    BACKEND_DIR
)


def first_existing_path(*paths):
    """
    Return the first existing model path.

    This keeps backward compatibility with older
    project folder structures.
    """

    for path in paths:
        if os.path.exists(path):
            return path

    # Return the preferred path even if it does not exist,
    # so the error message remains clear.
    return paths[0]


AR_MODEL_PATH = first_existing_path(

    # Preferred company-facing structure
    os.path.join(
        PROJECT_ROOT,
        "intent_arabic",
        "xlmr_intent_model_13_balanced",
    ),

    os.path.join(
        PROJECT_ROOT,
        "intent_arabic",
    ),

    # Legacy project structure
    os.path.join(
        BACKEND_DIR,
        "Intent_Ara",
        "xlmr_intent_model_13_balanced",
    ),
)


EN_MODEL_PATH = first_existing_path(

    # Preferred company-facing structure
    os.path.join(
        PROJECT_ROOT,
        "intent_eng",
    ),

    # Legacy project structure
    os.path.join(
        BACKEND_DIR,
        "intent_Eng",
    ),
)


# ============================================================
# Text Normalization
# ============================================================

def normalize_text(text):
    """
    Basic normalization for Arabic and English telecom messages.
    """

    text = str(text).strip().lower()

    # Remove Arabic elongation
    text = re.sub(
        r"ـ+",
        "",
        text,
    )

    # Normalize Arabic letters
    text = re.sub(
        r"[أإآٱ]",
        "ا",
        text,
    )

    text = re.sub(
        r"ى",
        "ي",
        text,
    )

    text = re.sub(
        r"ؤ",
        "و",
        text,
    )

    text = re.sub(
        r"ئ",
        "ي",
        text,
    )

    text = re.sub(
        r"ة",
        "ه",
        text,
    )

    # Remove Arabic diacritics
    text = re.sub(
        r"[\u0617-\u061A\u064B-\u0652]",
        "",
        text,
    )

    # Keep Arabic, English, digits, spaces and underscores
    text = re.sub(
        r"[^\u0600-\u06FFa-zA-Z0-9\s_]",
        " ",
        text,
    )

    # Normalize spaces
    text = re.sub(
        r"\s+",
        " ",
        text,
    ).strip()

    return text


def normalize_intent(intent):
    """
    Normalize intent names returned by different models.
    """

    intent = str(
        intent
    ).strip().lower()

    mapping = {
        "slow internet": "slow_internet",
        "slow-internet": "slow_internet",

        "no signal": "no_signal",
        "no-signal": "no_signal",

        "network complaint": "network_complaint",

        "network status": "network_status",
        "network-status": "network_status",

        "renew package": "renew_package",
        "package renewal": "renew_package",

        "check data usage": "check_data_usage",
        "data usage": "check_data_usage",

        "offer inquiry": "offer_inquiry",

        "technical support": "technical_support",

        "payment issue": "payment_issue",
    }

    return mapping.get(
        intent,
        intent,
    )


# ============================================================
# High-Confidence Rule-Based Backup
# ============================================================

def rule_based_override(text):
    """
    High-confidence rules for common telecom requests.

    These rules are intentionally limited so they do not
    unnecessarily override the trained AI model.
    """

    text = normalize_text(
        text
    )


    # --------------------------------------------------------
    # Greetings
    # --------------------------------------------------------

    greetings = {
        "مرحبا",
        "مرحباا",
        "هلا",
        "هلااا",
        "هلا والله",
        "هلا فيك",
        "ياهلا",
        "يا هلا وغلا",
        "اهلا",
        "اهلين",
        "اهلين فيك",
        "السلام عليكم",
        "كيفك",
        "كيف الحال",
        "شو الاخبار",
        "hello",
        "hi",
        "hey",
    }

    if text in greetings:
        return "greeting"


    # --------------------------------------------------------
    # Goodbye
    # --------------------------------------------------------

    goodbyes = {
        "مع السلامه",
        "باي",
        "bye",
        "goodbye",
        "سلام",
    }

    if text in goodbyes:
        return "goodbye"


    # --------------------------------------------------------
    # Feedback / Thanks
    # --------------------------------------------------------

    feedback_words = {
        "شكرا",
        "مشكور",
        "يسلمو",
        "يعطيك العافيه",
        "thank you",
        "thanks",
        "كفو",
        "ما قصرت",
    }

    if text in feedback_words:
        return "feedback"


    # --------------------------------------------------------
    # Package Renewal
    # --------------------------------------------------------

    if re.search(
        r"\b("
        r"جدد|"
        r"تجديد|"
        r"اجدد|"
        r"تجدد|"
        r"renew|"
        r"renewal"
        r")\b",
        text,
    ):
        return "renew_package"


    # --------------------------------------------------------
    # Data Usage
    # --------------------------------------------------------

    if re.search(
        r"("
        r"استهلاك|"
        r"استهلكت|"
        r"المتبقي|"
        r"كم باقي|"
        r"قديش باقي|"
        r"البيانات المتبقيه|"
        r"remaining data|"
        r"data usage|"
        r"usage"
        r")",
        text,
    ):
        return "check_data_usage"


    # --------------------------------------------------------
    # Offers
    # --------------------------------------------------------

    if re.search(
        r"("
        r"العروض|"
        r"عرض جديد|"
        r"عروض الانترنت|"
        r"عروض المكالمات|"
        r"offers|"
        r"available offers"
        r")",
        text,
    ):
        return "offer_inquiry"


    # --------------------------------------------------------
    # International Calls
    # --------------------------------------------------------

    if re.search(
        r"("
        r"المكالمات الدوليه|"
        r"اتصال دولي|"
        r"مكالمات دوليه|"
        r"international calls"
        r")",
        text,
    ):
        return "offer_inquiry"


    # --------------------------------------------------------
    # Technical Support
    # --------------------------------------------------------

    if re.search(
        r"("
        r"الدعم الفني|"
        r"دعم فني|"
        r"التواصل مع الدعم|"
        r"technical support|"
        r"customer support"
        r")",
        text,
    ):
        return "technical_support"


    # --------------------------------------------------------
    # Slow Internet
    # --------------------------------------------------------

    if re.search(
        r"("
        r"النت|"
        r"الانترنت|"
        r"internet"
        r").*("
        r"بطي|"
        r"ضعيف|"
        r"تقطيع|"
        r"يعلق|"
        r"slow|"
        r"weak"
        r")",
        text,
    ):
        return "slow_internet"


    if re.search(
        r"("
        r"السرعه بطي|"
        r"سرعه ضعيفه|"
        r"slow internet"
        r")",
        text,
    ):
        return "slow_internet"


    # --------------------------------------------------------
    # No Signal
    # --------------------------------------------------------

    if re.search(
        r"("
        r"ما في|"
        r"مافي|"
        r"لا يوجد|"
        r"معدومه|"
        r"خارج الخدمه|"
        r"no"
        r").*("
        r"اشاره|"
        r"شبكه|"
        r"تغطيه|"
        r"signal|"
        r"coverage"
        r")",
        text,
    ):
        return "no_signal"


    if re.search(
        r"("
        r"no signal|"
        r"no coverage"
        r")",
        text,
    ):
        return "no_signal"


    # --------------------------------------------------------
    # Network Status
    # --------------------------------------------------------

    if re.search(
        r"("
        r"حاله|"
        r"وضع|"
        r"شو وضع|"
        r"افحص|"
        r"تفحص|"
        r"تحقق|"
        r"status"
        r").*("
        r"الشبكه|"
        r"النت|"
        r"الخدمه|"
        r"network|"
        r"internet"
        r")",
        text,
    ):
        return "network_status"


    # --------------------------------------------------------
    # Payment Issue
    # --------------------------------------------------------

    if re.search(
        r"("
        r"دفعت|"
        r"دفع|"
        r"شحن|"
        r"شحنت|"
        r"خصم|"
        r"انخصم|"
        r"الرصيد|"
        r"فاتوره|"
        r"payment"
        r").*("
        r"ما صار|"
        r"ما وصل|"
        r"فشل|"
        r"مشكله|"
        r"اختفى|"
        r"ما زبط|"
        r"failed|"
        r"problem"
        r")",
        text,
    ):
        return "payment_issue"


    return None


# ============================================================
# Model Loading
# ============================================================

DEVICE = (
    0
    if torch.cuda.is_available()
    else -1
)

arabic_clf = None
english_clf = None


def load_classifier(model_path, language_name):
    """
    Load a Hugging Face text-classification model.
    """

    if not os.path.exists(
        model_path
    ):
        raise FileNotFoundError(
            f"{language_name} intent model was not found at: "
            f"{model_path}"
        )

    tokenizer = AutoTokenizer.from_pretrained(
        model_path
    )

    model = (
        AutoModelForSequenceClassification
        .from_pretrained(
            model_path
        )
    )

    return pipeline(
        "text-classification",
        model=model,
        tokenizer=tokenizer,
        device=DEVICE,
    )


def load_arabic_model():
    global arabic_clf

    if arabic_clf is None:
        arabic_clf = load_classifier(
            AR_MODEL_PATH,
            "Arabic",
        )

    return arabic_clf


def load_english_model():
    global english_clf

    if english_clf is None:
        english_clf = load_classifier(
            EN_MODEL_PATH,
            "English",
        )

    return english_clf


# ============================================================
# Model Prediction
# ============================================================

def predict_with_model(
    clean_text,
    lang,
):

    if lang == "ar":
        classifier = load_arabic_model()

    else:
        classifier = load_english_model()

    prediction = classifier(
        clean_text,
        truncation=True,
    )[0]

    intent = normalize_intent(
        prediction.get(
            "label",
            "other",
        )
    )

    confidence = float(
        prediction.get(
            "score",
            0.0,
        )
    )

    return (
        intent,
        confidence,
    )


# ============================================================
# Main Intent Prediction Function
# ============================================================

def predict_intent(
    text,
    lang="ar",
):
    """
    Predict customer intent using:

    1. High-confidence rules for common requests.
    2. Trained Arabic or English Transformer model.
    3. Minimal fallback logic if the model is unavailable.
    """

    text = str(
        text
    )

    clean_text = normalize_text(
        text
    )

    if not clean_text:
        return (
            "other",
            0.0,
        )


    # --------------------------------------------------------
    # High-confidence rules
    # --------------------------------------------------------

    forced_intent = rule_based_override(
        text
    )

    if forced_intent is not None:
        return (
            forced_intent,
            0.99,
        )


    # --------------------------------------------------------
    # Transformer Model
    # --------------------------------------------------------

    try:
        intent, confidence = predict_with_model(
            clean_text,
            lang,
        )

        # Reject low-confidence model output
        if confidence < 0.40:
            return (
                "other",
                confidence,
            )

        return (
            intent,
            confidence,
        )


    # --------------------------------------------------------
    # Safe Fallback
    # --------------------------------------------------------

    except Exception as exc:

        print(
            "[INTENT MODEL WARNING]",
            exc,
        )

        fallback_rules = {

            "greeting": [
                "هاي",
                "هلا",
                "مرحبا",
                "hello",
                "hi",
                "hey",
            ],

            "slow_internet": [
                "بطي",
                "تقطيع",
                "slow internet",
            ],

            "no_signal": [
                "ما في اشاره",
                "مافي اشاره",
                "no signal",
            ],

            "technical_support": [
                "دعم فني",
                "technical support",
            ],
        }

        for intent, keywords in (
            fallback_rules.items()
        ):

            if any(
                keyword in clean_text
                for keyword in keywords
            ):
                return (
                    intent,
                    0.75,
                )

        return (
            "other",
            0.50,
        )
