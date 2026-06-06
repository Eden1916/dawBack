"""
GET /search?q=amoxicillin&lang=en

Returns full translated drug info for a given drug name.
"""
from fastapi import APIRouter, HTTPException, Query
from services.openfda import fetch_drug
from services.translate import translate_drug

router = APIRouter()


@router.get("/search")
async def search_drug(
    q: str = Query(..., min_length=2, description="Drug name to search"),
    lang: str = Query("en", description="Preferred language: en | am | om"),
):
    drug = await fetch_drug(q)
    if not drug:
        raise HTTPException(status_code=404, detail=f"Drug '{q}' not found in OpenFDA database.")

    translated = translate_drug(drug)

    # Flatten to the requested language for convenience
    # (frontend can also handle the full multilingual object)
    return {"drug": translated, "lang": lang}
