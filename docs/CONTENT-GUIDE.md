# Content Guide (NidePizza)

Purpose: map editable content and data locations.

## Product data

- `app/seed.py`: initial products, prices, categories, images and badges.
- `Product` model in `app/models.py`: slug, name, description, price, image, category, weight and badge.
- Flask-Admin allows editing products, orders and order items in production.

## City / GEO data

- `app/geo_data.py`: cities, neighborhoods, delivery times, fees and FAQs. Keep city slugs URL-safe because routes use them.
- Add a city only if its FAQ and delivery details are complete; sitemap generation includes all cities.

## Business metadata

- `app/config.py`: brand name, site URL, phone, email, address, opening hours and currency.
- Do not hard-code secrets; use environment variables.

## Templates

- Templates in `templates/` reference product and city fields. Text changes should preserve HTML escaping through Jinja.
- Do not expose internal Mollie webhook or admin URLs in public content.

## Checklist for adding a product

1. Add seed record or admin product with a unique slug.
2. Add corresponding image under `static/img/`.
3. Verify menu, product detail, sitemap and `/og-image/product/<slug>.png`.
4. Run tests.