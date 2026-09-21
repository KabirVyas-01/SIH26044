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
    SMTP_SERVER = os.environ.get("SMTP_SERVER", "smtp.gmail.com")
    SMTP_PORT = int(os.environ.get("SMTP_PORT", 587))
    SMTP_EMAIL = os.environ.get("SMTP_EMAIL", "")
    SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD", "")