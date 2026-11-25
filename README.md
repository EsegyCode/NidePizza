# NidePizza — Wood-Fired Pizza & Artisan Sushi

Modern Flask e-commerce platform for **NidePizza**, featuring a modular Application Factory architecture, custom editorial design, Dutch GEO/SEO landing pages, dynamic Open Graph PNG generation, Schema.org JSON-LD, `llms.txt`, `sitemap.xml`, `robots.txt`, and legal/compliance pages.

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

## Testing

```powershell
.venv\Scripts\pytest.exe -v
```
