"""
Fetches drug information from the OpenFDA API and normalises it
into the shape the frontend expects.

OpenFDA docs: https://open.fda.gov/apis/drug/label/
No API key required for up to 1000 requests/day per IP.
"""
import httpx
import cache

OPENFDA_LABEL_URL = "https://api.fda.gov/drug/label.json"


def _first(lst: list, fallback: str = "") -> str:
    """Return the first element of a list or a fallback string."""
    if lst and isinstance(lst, list):
        return lst[0]
    return fallback


async def fetch_drug(drug_name: str) -> dict | None:
    """
    Query OpenFDA for a drug by name.
    Returns a normalised dict or None if not found.
    """
    cache_key = f"openfda:{drug_name.lower()}"
    cached = cache.get(cache_key)
    if cached:
        return cached

    params = {
        "search": f'openfda.brand_name:"{drug_name}" OR openfda.generic_name:"{drug_name}"',
        "limit": 1,
    }

    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(OPENFDA_LABEL_URL, params=params)

    if resp.status_code != 200:
        return None

    data = resp.json()
    results = data.get("results")
    if not results:
        return None

    label = results[0]
    openfda = label.get("openfda", {})

    drug = {
        "name": _first(openfda.get("brand_name"), drug_name).title(),
        "generic": _first(openfda.get("generic_name"), "").title(),
        "rx": "OTC" not in _first(openfda.get("product_type"), "OTC").upper(),
        "purpose": _first(label.get("purpose") or label.get("indications_and_usage"), "Not available."),
        "sideEffects": _first(label.get("adverse_reactions"), "Not available."),
        "stopWarnings": _first(label.get("warnings") or label.get("warnings_and_cautions"), "Not available."),
        "dosage": _first(label.get("dosage_and_administration"), "Not available."),
        "interactions": _first(label.get("drug_interactions"), "Not available."),
        "disclaimer": (
            "Always consult a licensed pharmacist or doctor before taking this medicine. "
            "This app provides information only and is not medical advice."
        ),
    }

    cache.set(cache_key, drug)
    return drug
