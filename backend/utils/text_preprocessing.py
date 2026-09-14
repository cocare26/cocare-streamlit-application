import re


# ============================================================
# Arabic normalization
# ============================================================

def normalize_arabic(text: str) -> str:
    """
    Normalize common Arabic letter variations while preserving
    the meaning of the original text.
    """

    if not isinstance(text, str):
        return ""

    # Remove Arabic diacritics
    text = re.sub(
        r"[\u0617-\u061A\u064B-\u0652]",
        "",
        text,
    )

    # Remove Tatweel
    text = re.sub(r"ـ+", "", text)

    # Normalize Arabic letters
    text = re.sub(r"[إأآٱ]", "ا", text)
    text = re.sub(r"ى", "ي", text)
    text = re.sub(r"ؤ", "و", text)
    text = re.sub(r"ئ", "ي", text)

    # Keep this because the Arabic training pipeline
    # used the same normalization.
    text = re.sub(r"ة", "ه", text)

    return text


# ============================================================
# Arabic slang normalization
# ============================================================

ARABIC_SLANG_MAP = {
    "بخزي": "سيء",
    "بعلق": "بطيء",
    "معلق": "بطيء",
    "بقطع": "منقطع",
    "خربان": "مشكله",
}


def normalize_slang(text: str) -> str:
    """
    Normalize selected Arabic colloquial expressions.
    """

    if not isinstance(text, str):
        return ""

    for slang, formal in ARABIC_SLANG_MAP.items():
        text = text.replace(slang, formal)

    return text


# ============================================================
# Repeated Arabic letters
# ============================================================

def normalize_arabic_repetition(text: str) -> str:
    """
    Reduce exaggerated Arabic character repetition.

    Example:
        هلاااا -> هلا

    This is limited to Arabic characters so English words such
    as 'good' or 'book' are not modified.
    """

    return re.sub(
        r"([\u0600-\u06FF])\1{2,}",
        r"\1",
        text,
    )


# ============================================================
# Main text cleaning
# ============================================================

def clean_text(text: str, lang: str = None) -> str:
    """
    Clean customer text before NLP processing.

    Args:
        text: Customer message.
        lang: Optional language code ("ar" or "en").

    Returns:
        Cleaned lowercase text.
    """

    if not isinstance(text, str):
        return ""

    text = text.strip()

    if not text:
        return ""

    # Remove URLs
    text = re.sub(
        r"https?://\S+|www\.\S+",
        " ",
        text,
    )

    # Arabic-specific preprocessing
    if lang == "ar" or (
        lang is None
        and re.search(r"[\u0600-\u06FF]", text)
    ):
        text = normalize_arabic(text)
        text = normalize_slang(text)
        text = normalize_arabic_repetition(text)

    # Remove unnecessary punctuation while keeping
    # letters, numbers and whitespace.
    text = re.sub(
        r"[^\w\s]",
        " ",
        text,
        flags=re.UNICODE,
    )

    # Normalize whitespace
    text = re.sub(
        r"\s+",
        " ",
        text,
    )

    return text.lower().strip()
