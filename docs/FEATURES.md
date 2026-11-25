# Features (NidePizza)

Purpose: user-facing and technical features evidenced by the repository.

## Storefront

- Home page with featured products, category counts and city list.
- Menu filtering by `all`, `pizza`, `sushi`, `sushi-sets`.
- Legacy `/sushi` and `/sushiset` redirects to menu categories.
- Product detail pages with related products and JSON-LD.
- Cart with add/update/remove and cart count.
- Checkout form with phone validation, city/address capture and order creation.
- Local order confirmation and optional Mollie payment redirect/webhook.

## Products and data

- `Product` model with slug, category, price, weight, image, badge and featured flag.
- `Order` and `OrderItem` models.
- Seed data created in `app/seed.py`; `_ensure_sqlite_columns` updates legacy SQLite columns.

## GEO and delivery

- Locations index and per-city landing pages.
- City data from `app/geo_data.py`, including neighborhoods and FAQs.
- City-specific JSON-LD with coordinates and aggregate delivery info.
- Netherlands delivery cities: Amsterdam, Rotterdam, Utrecht, Den Haag, Haarlem, Eindhoven.
- OG images for default, product and city variants.

## SEO and AI readiness

- `/robots.txt`, `/sitemap.xml`, `/llms.txt`, `/llms-full.txt`.
- Sitemap includes static pages, city pages and product pages when slugs exist.
- JSON-LD types: `Restaurant`, `Product`, `BreadcrumbList`, `FAQPage`.
- Dynamic OG PNG generation with Pillow at 1200 x 630.
- Meta title/description/canonical/OG properties in templates and route handlers.

## Administration and operations

- Flask-Admin over products, orders and order items.
- Telegram notifications for new and paid orders.
- Mollie payments with webhook paid-status updates.
- Error handlers for 404 and 500.

## Configuration touchpoints

- Config: `app/config.py`.
- Models: `app/models.py`.
- Blueprints: `app/routes/`.
- Seed and migration: `app/seed.py`, `_ensure_sqlite_columns()` in `app/__init__.py`.