import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
load_dotenv(os.path.join(basedir, ".env"))


class Config:
    """Application configuration loaded from environment variables."""

    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-nidepizza-secret-change-in-prod")
    BRAND_NAME = os.environ.get("BRAND_NAME", "NidePizza")
    SITE_URL = os.environ.get("SITE_URL", "http://localhost:8000").rstrip("/")

    # Database
    default_db = "sqlite:///" + os.path.join(basedir, "shop.db")
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", default_db)
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # External integrations (never hardcoded in source)
    MOLLIE_API_KEY = os.environ.get("MOLLIE_API_KEY", "")
    TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
    TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")

    # Business metadata for SEO / GEO / Schema.org
    BUSINESS_PHONE = os.environ.get("BUSINESS_PHONE", "+31 20 894 3120")
    BUSINESS_EMAIL = os.environ.get("BUSINESS_EMAIL", "contact@nidepizza.com")
    BUSINESS_ADDRESS = {
        "street": "Keizersgracht 412",
        "city": "Amsterdam",
        "postal_code": "1016 GC",
        "country": "NL",
        "region": "Noord-Holland",
    }
    OPENING_HOURS = "Mo-Su 11:00-23:00"
    CURRENCY = "EUR"
    CURRENCY_SYMBOL = "€"
    LOG_DIR = os.path.join(basedir, "logs")


class TestConfig(Config):
    """Configuration used by pytest."""

    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SITE_URL = "https://nidepizza.nl"
    MOLLIE_API_KEY = ""
    TELEGRAM_BOT_TOKEN = ""
