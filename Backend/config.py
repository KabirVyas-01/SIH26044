import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

DB_PATH = os.environ.get("DATABASE_PATH", str(BASE_DIR / "portal.db"))

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-cse-2026")
    DATABASE_PATH = DB_PATH
    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
    SESSION_COOKIE_HTTPONLY = True
    PERMANENT_SESSION_LIFETIME = 86400