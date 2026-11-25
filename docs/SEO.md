# SEO and AI Readiness (NidePizza)

Purpose: document search and AI-facing mechanisms implemented in the project.

## Metadata and structured data

- Route handlers supply `seo` dictionaries for title, description, canonical URL, OG image, robots and OG type.
- `app/services/seo_schema.py` builds Restaurant, Product, BreadcrumbList and FAQPage schemas.
- JSON-LD is rendered through Jinja templates.

## Crawler files

- `/robots.txt` disallows admin/order/cart/checkout/payment routes and references `/sitemap.xml`.
- `/sitemap.xml` includes core pages, city pages and product pages.
- `/llms.txt` gives an AI summary with city and legal links.
- `/llms-full.txt` lists products and city FAQs.

## Dynamic assets

- `/og-image/default.png`, `/og-image/product/<slug>.png`, `/og-image/city/<slug>.png` and `/og-image/page/<key>.png` generate 1200 x 630 PNGs via Pillow.
- Responses are cached for one day.

## URLs

Canonical URLs use `SITE_URL` or the current request URL. JSON-LD and sitemap locations depend on the same base.

## Touchpoints

- Change business metadata in `app/config.py`.
- Change routes in `app/routes/`.
- Change schema builders in `app/services/seo_schema.py`.