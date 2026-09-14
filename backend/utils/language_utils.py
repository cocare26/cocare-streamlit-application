def detect_language(text: str) -> str:
    """
    Detect whether the input text is primarily Arabic or English.

    Returns:
        "ar" for Arabic
        "en" for English
    """

    if not text or not str(text).strip():
        return "ar"

    text = str(text)

    arabic_count = sum(
        1 for char in text
        if "\u0600" <= char <= "\u06FF"
    )

    english_count = sum(
        1 for char in text
        if char.isascii() and char.isalpha()
    )

    if arabic_count == 0 and english_count == 0:
        return "ar"

    return "ar" if arabic_count >= english_count else "en"
