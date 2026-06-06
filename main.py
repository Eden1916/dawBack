"""
PillSafe / Dawa Info — FastAPI Backend
Run with:  uvicorn main:app --reload
"""
import os
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes.search import router as search_router
from routes.ocr import router as ocr_router
import cache as cache_module

load_dotenv()

app = FastAPI(
    title="Dawa Info API",
    description="Medicine safety information for Ethiopia — English, Amharic, Afaan Oromo",
    version="1.0.0",
)

# CORS — allow the React dev server and any deployed frontend
allowed_origins = [
    os.getenv("FRONTEND_ORIGIN", "http://localhost:5173"),
    "http://localhost:3000","https://daw-delta.vercel.app/",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(search_router, tags=["Search"])
app.include_router(ocr_router, tags=["OCR"])


@app.get("/health", tags=["Health"])
async def health():
    return {"status": "ok"}


@app.post("/cache/clear", tags=["Health"])
async def clear_cache():
    cache_module.clear()
    return {"status": "cache cleared"}
