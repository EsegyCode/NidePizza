# NidePizza — Wood-Fired Pizza & Artisan Sushi

Modern Flask e-commerce platform for **NidePizza**, featuring a modular Application Factory architecture, custom editorial design, Dutch GEO/SEO landing pages, dynamic Open Graph PNG generation, Schema.org JSON-LD, `llms.txt`, `sitemap.xml`, `robots.txt`, and legal/compliance pages.

## Tech stack

| Area | Technology | Notes |
| --- | --- | --- |
| Framework | Flask + SQLAlchemy + Jinja2 | application factory in `app/__init__.py` |
| Language | Python >= 3.11 | `pyproject.toml` |
| Database | SQLite by default; MySQL optional | `DATABASE_URL` |
| Payments | Mollie API with local fallback | `app/services/payment.py` |
| Notifications | Telegram Bot API | `app/services/telegram.py` |
| Images | Pillow dynamic OG generator | `app/services/og_image.py` |
| SEO | JSON-LD, sitemap, robots, llms files | `app/routes/seo.py` |
| Tests | pytest | `tests/test_routes.py` |

Status: production e-commerce site configuration; localized for Netherlands delivery. License: TODO (owner).

## Quick Start

```powershell
# 1. Create virtual environment & install dependencies
uv venv .venv
uv pip install --python .venv\Scripts\python.exe -r requirements.txt

# 2. Configure environment variables
copy .env.example .env

# 3. Run the development server
.venv\Scripts\python.exe run.py
```

Open `http://localhost:8000` in your browser.

## Project Structure

- `app/` — Flask application factory, config, SQLAlchemy models, seeding, GEO data, services, and Blueprints
  - `app/services/og_image.py` — Dynamic `1200x630` PNG Open Graph image generator (Pillow)
  - `app/services/seo_schema.py` — JSON-LD builders (`Restaurant`, `Product`, `BreadcrumbList`, `FAQPage`)
  - `app/services/payment.py` — Mollie payment integration with safe local fallback
  - `app/services/telegram.py` — Telegram order notifications
- `templates/` — Jinja2 templates with SEO meta tags, Open Graph, and JSON-LD
- `static/` — Custom editorial CSS design system, vanilla JS cart/toast interactions, fonts, and product imagery
- `tests/` — `pytest` suite covering routes, SEO/GEO, JSON-LD, OG images, and checkout

## Key Endpoints

| Purpose | URL |
| --- | --- |
| Home & Featured | `/` |
| Menu & Categories | `/menu`, `/menu/pizza`, `/menu/sushi`, `/menu/sushi-sets` |
| Legacy Routes | `/sushi`, `/sushiset`, `/about`, `/orders`, `/admin/orders` |
| Product SEO Pages | `/product/<slug>` |
| GEO City Pages | `/locations`, `/delivery/amsterdam`, `/delivery/rotterdam`, `/delivery/utrecht`, `/delivery/den-haag`, `/delivery/haarlem`, `/delivery/eindhoven` |
| Legal Pages | `/privacy`, `/terms`, `/cookies`, `/allergens-delivery` |
| Dynamic OG Images | `/og-image/default.png`, `/og-image/product/<slug>.png`, `/og-image/city/<city>.png` |
| Crawlers & LLMs | `/sitemap.xml`, `/robots.txt`, `/llms.txt`, `/llms-full.txt` |

## Environment variables

Names from `.env.example` (values are set locally in `.env`, never committed):

- `FLASK_ENV`, `SECRET_KEY`, `SITE_URL`, `BRAND_NAME`
- `DATABASE_URL`
- `MOLLIE_API_KEY`
- `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`
- `BUSINESS_PHONE`, `BUSINESS_EMAIL`, `BUSINESS_ADDRESS`, `OPENING_HOURS`, `CURRENCY`, `CURRENCY_SYMBOL` may be overridden through config where supported; defaults are defined in `app/config.py`.

## Documentation

- [Features](docs/FEATURES.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Deployment](docs/DEPLOYMENT.md)
- [Maintainer FAQ](docs/FAQ.md)
- [Content guide](docs/CONTENT-GUIDE.md)
- [SEO and AI readiness](docs/SEO.md)
- [Changelog](docs/CHANGELOG.md)
- [Ukrainian summary](README.uk.md)

## Testing

```powershell
.venv\Scripts\pytest.exe -v
```
