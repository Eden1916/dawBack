"""
Extracts text from a medicine photo using Tesseract OCR,
then picks the most likely drug name from the result.

Tesseract must be installed separately:
  Windows: https://github.com/UB-Mannheim/tesseract/wiki
  Linux:   sudo apt install tesseract-ocr
  macOS:   brew install tesseract
"""
import os
import re
import pytesseract
from PIL import Image, ImageFilter, ImageEnhance
import io

# Allow overriding the Tesseract binary path via .env
_tesseract_cmd = os.getenv("TESSERACT_CMD")
if _tesseract_cmd:
    pytesseract.pytesseract.tesseract_cmd = _tesseract_cmd

# Common words on medicine packaging that are NOT drug names — skip these
_NOISE_WORDS = {
    "tablets", "capsules", "syrup", "injection", "mg", "ml", "g", "mcg",
    "film", "coated", "oral", "solution", "suspension", "batch", "lot",
    "exp", "mfg", "manufactured", "by", "for", "use", "only", "keep",
    "out", "of", "reach", "children", "store", "below", "warning",
    "dosage", "each", "contains", "active", "ingredient", "ingredients",
}


def _preprocess(image_bytes: bytes) -> Image.Image:
    """Enhance the image to improve OCR accuracy."""
    img = Image.open(io.BytesIO(image_bytes)).convert("L")  # grayscale
    img = img.filter(ImageFilter.SHARPEN)
    img = ImageEnhance.Contrast(img).enhance(2.0)
    return img


def _extract_drug_name(raw_text: str) -> str | None:
    """
    Heuristic: the drug name is usually the largest / first prominent word.
    We look for the first capitalised word that is not a noise word and
    is at least 4 characters long.
    """
    lines = raw_text.strip().splitlines()
    for line in lines:
        line = line.strip()
        if not line:
            continue
        # Take the first token that looks like a drug name
        tokens = re.findall(r"[A-Za-z]{4,}", line)
        for token in tokens:
            if token.lower() not in _NOISE_WORDS:
                return token
    return None


def extract_text_from_image(image_bytes: bytes) -> dict:
    """
    Run OCR on the provided image bytes.
    Returns:
      { "raw_text": str, "drug_name": str | None }
    """
    img = _preprocess(image_bytes)
    raw_text = pytesseract.image_to_string(img, lang="eng")
    drug_name = _extract_drug_name(raw_text)
    return {"raw_text": raw_text.strip(), "drug_name": drug_name}
