"""
Translates drug info fields into Amharic (am) and Afaan Oromo (om)
using deep-translator (Google Translate, no API key needed).

Handles long OpenFDA texts by splitting into chunks under the 5000-char limit.
"""
import cache
from deep_translator import GoogleTranslator

TRANSLATABLE_FIELDS = ["purpose", "sideEffects", "stopWarnings", "dosage", "interactions", "disclaimer"]

# deep-translator language codes
LANG_CODE_MAP = {
    "am": "am",  # Amharic
    "or": "om",  # Afaan Oromo
}

MAX_CHARS = 4500  # stay safely under Google Translate's 5000-char limit


def _chunk_text(text: str) -> list[str]:
    """
    Split long text into chunks under MAX_CHARS.
    Tries to split on sentence boundaries to preserve readability.
    """
    if len(text) <= MAX_CHARS:
        return [text]

    chunks = []
    # Split on sentence endings first
    sentences = text.replace("\n", " ").split(". ")
    current = ""

    for sentence in sentences:
        piece = sentence.strip()
        if not piece:
            continue
        # Add period back if it was stripped
        if not piece.endswith("."):
            piece += "."

        if len(current) + len(piece) + 1 <= MAX_CHARS:
            current += (" " if current else "") + piece
        else:
            if current:
                chunks.append(current)
            # If a single sentence is still too long, hard-cut it
            if len(piece) > MAX_CHARS:
                for i in range(0, len(piece), MAX_CHARS):
                    chunks.append(piece[i:i + MAX_CHARS])
            else:
                current = piece

    if current:
        chunks.append(current)

    return chunks if chunks else [text[:MAX_CHARS]]


def _translate_text(text: str, target_lang_code: str) -> str:
    """
    Translate a text string, splitting into chunks if it exceeds the limit.
    Returns the original English text on any failure.
    """
    if not text or text == "Not available.":
        return text

    cache_key = f"translate:{target_lang_code}:{hash(text)}"
    cached = cache.get(cache_key)
    if cached:
        return cached

    try:
        chunks = _chunk_text(text)
        translated_parts = []

        for chunk in chunks:
            result = GoogleTranslator(source="en", target=target_lang_code).translate(chunk)
            if result:
                translated_parts.append(result)
            else:
                translated_parts.append(chunk)  # keep original if chunk fails

        translated = " ".join(translated_parts)
        cache.set(cache_key, translated)
        return translated

    except Exception:
        pass  # fall back to English on any error

    return text


def translate_drug(drug: dict) -> dict:
    """
    Returns a new drug dict where each translatable field becomes:
      { "en": "...", "am": "...", "or": "..." }
    """
    result = dict(drug)

    for field in TRANSLATABLE_FIELDS:
        en_text = drug.get(field, "")
        translations = {"en": en_text}

        for app_lang, google_code in LANG_CODE_MAP.items():
            translations[app_lang] = _translate_text(en_text, google_code)

        result[field] = translations

    return result
