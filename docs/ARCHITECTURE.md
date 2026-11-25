# Architecture (NidePizza)

Purpose: explain how the application is structured and how requests are served.

## Application model

`app/__init__.py` uses a Flask application factory:

1. Builds Flask app with `templates` and `static` at repository root.
2. Loads configuration from environment variables.
3. Initialises SQLAlchemy and Flask-Admin unless testing.
4. Registers blueprints: `main`, `geo`, `legal`, `seo`, `admin`.
5. Creates database tables and seed data.
6. Safely adds columns to an existing SQLite database.

## Request flow

- Browser requests route to a blueprint.
- Route reads products/cities and cart/order session.
- Templates render HTML with SEO metadata and JSON-LD.
- Dynamic OG endpoints use Pillow.
- SEO endpoints serve text or XML.

```text
browser -> Flask blueprint route -> SQLAlchemy
  -> Jinja template with metadata/JSON-LD -> HTML
  or -> Pillow/Telegram/Mollie integrations
```

## Modules

- `app/models.py`: Product, Order, OrderItem.
- `app/seed.py`: seed products.
- `app/geo_data.py`: cities, neighborhoods, delivery details and FAQs.
- `app/services/payment.py`: Mollie payment and webhook handling.
- `app/services/telegram.py`: Telegram Bot API notifications.
- `app/services/seo_schema.py`: Schema.org builders.
- `app/services/og_image.py`: dynamic OG PNG generation.
- `app/routes/`: main, geo/locations, legal pages and SEO endpoints.

## Cart and checkout

- Cart is stored in Flask session as `{product_id: quantity}`.
- `/checkout` creates an Order and OrderItem records, then attempts Mollie checkout.
- If Mollie is unconfigured or fails, the request falls back to local confirmation and Telegram notification.
- `/mollie_webhook` marks paid orders when Mollie reports payment.

## Database notes

- Default SQLite file is `shop.db`.
- TestConfig uses in-memory SQLite.
- Column migrations run only for SQLite and only add columns if absent.