from flask import Blueprint, redirect, render_template, request, url_for
from app.extensions import db
from app.models import Order, Product
from app.seed import ensure_seed_data, slugify

admin_bp = Blueprint("admin_views", __name__)


@admin_bp.route("/orders")
@admin_bp.route("/admin/orders")
def show_orders():
    orders = Order.query.order_by(Order.id.desc()).all()
    return render_template(
        "orders.html",
        orders=orders,
        active_page="orders",
        seo={"title": "Orders Dashboard | NidePizza", "robots": "noindex, nofollow"},
    )


@admin_bp.route("/admin/add-product", methods=["GET", "POST"])
def add_product():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        description = request.form.get("description", "").strip()
        price = request.form.get("price", type=float)
        image = request.form.get("image", "margherita.png").strip() or "margherita.png"
        category = request.form.get("category", "Pizza").strip()
        if name and price is not None:
            base_slug = slugify(name)
            slug = base_slug
            idx = 1
            while Product.query.filter_by(slug=slug).first():
                idx += 1
                slug = f"{base_slug}-{idx}"
            prod = Product(
                slug=slug,
                name=name,
                description=description,
                price=price,
                image=image,
                category=category,
            )
            db.session.add(prod)
            db.session.commit()
            return redirect(url_for("main.product_detail", slug=prod.slug))

    return render_template(
        "add_product.html",
        active_page="orders",
        seo={"title": "Add Dish | NidePizza", "robots": "noindex, nofollow"},
    )


@admin_bp.route("/init_products")
def init_products():
    added = ensure_seed_data()
    return f"Initialized {added} products." if added else "Products already initialized."
