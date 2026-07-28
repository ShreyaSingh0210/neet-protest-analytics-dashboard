# config/config.py
# Central configuration for NEET Protest Analytics Platform
# - Uses environment variables (via python-dotenv) for secrets and endpoints
# - Provides helpful defaults for a local dev environment
# - Lightweight helper factories for external services (Supabase / Gemini / OpenAI)
# Do NOT store secrets in this file; put them in a .env file or in your deployment env.

import os
import logging
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

# Load .env from project root (if present)
BASE_DIR = Path(__file__).resolve().parents[1]
ENV_PATH = BASE_DIR / ".env"
if ENV_PATH.exists():
    load_dotenv(ENV_PATH)
else:
    load_dotenv()  # safe: will fall back to environment variables

# ----- Paths and files -----
DATA_DIR = Path(os.getenv("DATA_DIR", BASE_DIR / "data")).resolve()
DATA_FILE = Path(os.getenv("DATA_FILE", DATA_DIR / "neet_protest_dataset.csv")).resolve()

DASHBOARD_DIR = Path(os.getenv("DASHBOARD_DIR", BASE_DIR / "dashboards")).resolve()
DOCS_DIR = Path(os.getenv("DOCS_DIR", BASE_DIR / "docs")).resolve()
STATIC_DIR = Path(os.getenv("STATIC_DIR", BASE_DIR / "static")).resolve()
TEMPLATES_DIR = Path(os.getenv("TEMPLATES_DIR", BASE_DIR / "templates")).resolve()

# Ensure directories exist in dev (the app will create them on startup if needed)
for p in (DATA_DIR, DASHBOARD_DIR, DOCS_DIR, STATIC_DIR, TEMPLATES_DIR):
    try:
        p.mkdir(parents=True, exist_ok=True)
    except Exception:
        # If environment is read-only, ignore; existence checks will handle later
        pass

# ----- App / security -----
SECRET_KEY = os.getenv("SECRET_KEY", "change-me-to-a-secure-random-value")
FLASK_DEBUG = os.getenv("FLASK_DEBUG", "False").lower() in ("1", "true", "yes")

# ----- External services (set these in .env / deployment) -----
# Supabase (optional) - used if you push the cleaned dataset to a managed DB
SUPABASE_URL = os.getenv("SUPABASE_URL", "") or None
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "") or None

# Gemini / LLM provider keys. Configure per your deployment and provider.
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "") or None
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "") or None

# Optional analytics / telemetry
SENTRY_DSN = os.getenv("SENTRY_DSN", "") or None

# ----- Feature flags / limits -----
MAX_AI_RESPONSE_TOKENS = int(os.getenv("MAX_AI_RESPONSE_TOKENS", "800"))
AI_MODEL = os.getenv("AI_MODEL", "gemini-pro")  # descriptive default

# ----- Logging -----
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
)
logger = logging.getLogger("neet_protest_analytics_config")

# ----- Helper factories (safe imports) -----
def get_supabase_client():
    """
    Returns a Supabase client if SUPABASE_URL and SUPABASE_KEY are present.
    The function lazily imports the client library so the codebase can run
    even if supabase is not installed in development environments.
    """
    if not SUPABASE_URL or not SUPABASE_KEY:
        logger.debug("Supabase credentials not configured; skipping client creation.")
        return None
    try:
        from supabase import create_client  # type: ignore
        client = create_client(SUPABASE_URL, SUPABASE_KEY)
        logger.debug("Supabase client created.")
        return client
    except Exception as e:
        logger.exception("Failed to create Supabase client: %s", e)
        return None


def get_ai_client():
    """
    Returns a callable/object that your app can use to call the configured LLM.
    This is a minimal abstraction — implement provider specific logic in the main app.
    If GEMINI_API_KEY is set, the app will prefer Gemini; otherwise OpenAI if available.
    """
    # Prefer Gemini if configured
    if GEMINI_API_KEY:
        # Integrate with your Gemini client / SDK here.
        # We avoid importing vendor SDKs at config time to keep dev simple.
        logger.debug("Gemini API key present; configure Gemini client in application code.")
        return {"provider": "gemini", "api_key": GEMINI_API_KEY, "model": AI_MODEL}
    if OPENAI_API_KEY:
        logger.debug("OpenAI API key present; configure OpenAI client in application code.")
        return {"provider": "openai", "api_key": OPENAI_API_KEY, "model": AI_MODEL}
    logger.warning("No AI provider configured (GEMINI_API_KEY or OPENAI_API_KEY missing).")
    return None

# ----- Runtime checks (useful during startup) -----
def verify_required_paths():
    """
    Check for the dataset and dashboard directory; logs warnings if not present.
    The app should still start even if data is missing so preview/placeholder screens can be shown.
    """
    if not DATA_FILE.exists():
        logger.warning("Dataset file not found at %s", DATA_FILE)
    else:
        logger.info("Dataset file located: %s", DATA_FILE)
    if not DASHBOARD_DIR.exists():
        logger.warning("Dashboard directory not found at %s", DASHBOARD_DIR)
    else:
        logger.info("Dashboard directory located: %s", DASHBOARD_DIR)

# Expose simple utility values for templates and app logic
CONFIG = {
    "BASE_DIR": str(BASE_DIR),
    "DATA_DIR": str(DATA_DIR),
    "DATA_FILE": str(DATA_FILE),
    "DASHBOARD_DIR": str(DASHBOARD_DIR),
    "DOCS_DIR": str(DOCS_DIR),
    "STATIC_DIR": str(STATIC_DIR),
    "TEMPLATES_DIR": str(TEMPLATES_DIR),
    "AI_PROVIDER": get_ai_client(),
    "SUPABASE": bool(SUPABASE_URL and SUPABASE_KEY),
}

if __name__ == "__main__":
    # Quick local check
    verify_required_paths()
    logger.info("Config loaded. Debug=%s", FLASK_DEBUG)
