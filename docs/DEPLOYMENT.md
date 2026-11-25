# Deployment (NidePizza)

Purpose: runtime, dependency and post-deploy notes for the Flask application.

## Runtime

- Python >= 3.11.
- Run with `run.py` or `python app.py` / Flask app; server listens on port `PORT` (default `8000`).
- SQLite file is `shop.db`; `DATABASE_URL` may point to another supported database.

## Dependencies

```powershell
uv pip install -r requirements.txt
# or
pip install -r requirements.txt
```

Dependencies are listed in `requirements.txt` and `pyproject.toml`.

## Environment variables

From `.env.example`: `FLASK_ENV`, `SECRET_KEY`, `SITE_URL`, `BRAND_NAME`, `DATABASE_URL`, `MOLLIE_API_KEY`, `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`. Production values should override environment-specific defaults. Site URL is used for canonical/SEO generation; do not commit real values.

## Build and output

There is no frontend build step. Static assets live in `static/`, templates in `templates/`, and media are served directly by Flask. Database seed data is created during app startup.

## Pre-release checklist

- Create `.env` from `.env.example` with safe values.
- Run `.venv\Scripts\pytest.exe -v`.
- Verify home, menu, product, city, cart, checkout, legal and OG image URLs.
- Verify `/robots.txt`, `/sitemap.xml`, `/llms.txt`, `/llms-full.txt`.
- Configure Mollie webhook URL if Mollie is used.
- Back up `shop.db` before deploy if it contains production data.