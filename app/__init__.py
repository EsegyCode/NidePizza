import json
import logging
import os
from flask import Flask, render_template, session
from flask_admin.contrib.sqla import ModelView
from sqlalchemy import text

from app.config import Config
from app.extensions import admin, db
from app.models import Order, OrderItem, Product
from app.routes import register_blueprints
from app.seed import ensure_seed_data


def _ensure_sqlite_columns():
    """Safely add new columns to an existing legacy shop.db without losing data."""
    if not str(db.engine.url).startswith("sqlite"):
        return

    product_cols = {
        row[1] for row in db.session.execute(text("PRAGMA table_info(product)")).fetchall()
    }
    migrations_product = {
        "slug": "ALTER TABLE product ADD COLUMN slug VARCHAR(140)",
        "weight": "ALTER TABLE product ADD COLUMN weight VARCHAR(40) DEFAULT '300g'",
        "badge": "ALTER TABLE product ADD COLUMN badge VARCHAR(40)",
        "is_featured": "ALTER TABLE product ADD COLUMN is_featured BOOLEAN NOT NULL DEFAULT 0",
    }
    for col, sql in migrations_product.items():
        if col not in product_cols:
            db.session.execute(text(sql))

    order_cols = {
        row[1] for row in db.session.execute(text('PRAGMA table_info("order")')).fetchall()
    }
    migrations_order = {
        "customer_name": 'ALTER TABLE "order" ADD COLUMN customer_name VARCHAR(120)',
        "delivery_city": 'ALTER TABLE "order" ADD COLUMN delivery_city VARCHAR(80)',
        "delivery_address": 'ALTER TABLE "order" ADD COLUMN delivery_address VARCHAR(240)',
    }
    for col, sql in migrations_order.items():
        if col not in order_cols:
            db.session.execute(text(sql))

    db.session.commit()


def create_app(config_class=Config) -> Flask:
    root_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    app = Flask(
        __name__,
        template_folder=os.path.join(root_dir, "templates"),
        static_folder=os.path.join(root_dir, "static"),
    )
    app.config.from_object(config_class)

    # Logging
    os.makedirs(app.config["LOG_DIR"], exist_ok=True)
    logging.basicConfig(
        filename=os.path.join(app.config["LOG_DIR"], "orders.log"),
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )

    # Extensions
    db.init_app(app)
    if not app.config.get("TESTING"):
        admin.init_app(app)
        if not admin._views or len(admin._views) <= 1:
            admin.add_view(ModelView(Product, db.session))
            admin.add_view(ModelView(Order, db.session))
            admin.add_view(ModelView(OrderItem, db.session))

    # Jinja helper for JSON-LD
    app.jinja_env.filters["to_jsonld"] = lambda obj: json.dumps(obj, ensure_ascii=False, indent=2)

    @app.context_processor
    def inject_globals():
        cart = session.get("cart", {})
        cart_count = sum(qty for qty in cart.values() if isinstance(qty, int) and qty > 0)
        return {
            "brand_name": app.config["BRAND_NAME"],
            "cart_count": cart_count,
            "business_phone": app.config["BUSINESS_PHONE"],
            "business_email": app.config["BUSINESS_EMAIL"],
            "opening_hours": app.config["OPENING_HOURS"],
        }

    # Blueprints
    register_blueprints(app)

    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return (
            render_template(
                "errors/404.html",
                seo={"title": "Page Not Found (404) | NidePizza", "robots": "noindex, nofollow"},
            ),
            404,
        )

    @app.errorhandler(500)
    def server_error(error):
        return (
            render_template(
                "errors/500.html",
                seo={"title": "Server Error (500) | NidePizza", "robots": "noindex, nofollow"},
            ),
            500,
        )

    with app.app_context():
        db.create_all()
        _ensure_sqlite_columns()
        ensure_seed_data()

    return app
