# Maintainer FAQ (NidePizza)

Purpose: practical maintenance answers for the NidePizza platform.

## How do I run it locally?

Create the virtual environment, install requirements, copy `.env.example` to `.env`, then run `.venv\Scripts\python.exe run.py`.

## How are products managed?

Products are stored in the database and seeded in `app/seed.py`. Admin views use Flask-Admin. Seed runs during app startup.

## How do Mollie payments work?

`app/services/payment.py` creates a Mollie payment when credentials are configured. The webhook updates `Order.is_paid`. Without credentials, checkout falls back to local confirmation and Telegram notification.

## How do Telegram notifications work?

`app/services/telegram.py` sends order details using `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID`. If either is empty, notifications are skipped.

## Where do I change delivery cities?

Edit `app/geo_data.py`; city pages and llms output use the same city records.

## Where is SEO/schema content?

Generated in `app/routes/seo.py` and `app/services/seo_schema.py`; business settings are in `app/config.py`.

## How are OG images generated?

`app/services/og_image.py` renders 1200 x 630 PNG images for default, product and city variants.

## How do I test?

Run `.venv\Scripts\pytest.exe -v`. Test config uses an in-memory database and tests some routes, SEO and JSON-LD.

## What should I check after a deploy?

Order placement, cart update, webhook/plain callback as applicable, city pages, sitemap, robots, llms, OG images, and Telegram notifications.

## License and contact

Business contact details are in `app/config.py` defaults. License is not declared in the repository: TODO (owner).