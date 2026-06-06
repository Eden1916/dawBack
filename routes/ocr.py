"""
POST /ocr
Body: multipart/form-data  { file: <image> }

Extracts a drug name from the uploaded medicine photo,
then returns full translated drug info.
"""
from fastapi import APIRouter, HTTPException, UploadFile, File, Query
from services.ocr import extract_text_from_image
from services.openfda import fetch_drug
from services.translate import translate_drug

router = APIRouter()

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp", "image/heic"}


@router.post("/ocr")
async def ocr_drug(
    file: UploadFile = File(...),
    lang: str = Query("en", description="Preferred language: en | am | om"),
):
    # Validate file type
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {file.content_type}. Use JPEG or PNG.")

    image_bytes = await file.read()

    # Validate file size
    if len(image_bytes) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File too large. Maximum size is 10 MB.")

    # Run OCR
    ocr_result = extract_text_from_image(image_bytes)
    drug_name = ocr_result.get("drug_name")

    if not drug_name:
        raise HTTPException(
            status_code=422,
            detail="Could not identify a drug name from the image. Try a clearer photo or search by name.",
        )

    # Fetch drug data
    drug = await fetch_drug(drug_name)
    if not drug:
        raise HTTPException(
            status_code=404,
            detail=f"Drug '{drug_name}' was read from the image but not found in the database.",
        )

    translated = translate_drug(drug)

    return {
        "drug": translated,
        "lang": lang,
        "ocr": {
            "detected_name": drug_name,
            "raw_text": ocr_result.get("raw_text"),
        },
    }
