import logging
import re
from flask import (
    Blueprint,
    abort,
    current_app,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from app.extensions import db
from app.geo_data import get_all_cities
from app.models import Order, OrderItem, Product
from app.services.payment import create_mollie_payment, fetch_mollie_payment
from app.services.seo_schema import (
    build_breadcrumb_schema,
    build_product_schema,
    build_restaurant_schema,
)
from app.services.telegram import send_telegram_message

main_bp = Blueprint("main", __name__)
logger = logging.getLogger(__name__)

CATEGORY_META = {
    "all": {
        "db_category": None,
        "title": "Full Menu — Wood-Fired Pizza & Fresh Sushi",
        "eyebrow": "Crafted Fresh Daily",
        "description": "Explore our complete menu of 48-hour sourdough Neapolitan pizzas, hand-rolled maki, and signature sushi sets.",
    },
    "pizza": {
        "db_category": "Pizza",
        "title": "Artisan Wood-Fired Pizza",
        "eyebrow": "48h Sourdough Crust",
        "description": "Stone-baked at 450°C with San Marzano DOP tomatoes, fior di latte mozzarella, and gourmet toppings.",
    },
    "sushi": {
        "db_category": "Sushi",
        "title": "Fresh Hand-Rolled Sushi",
        "eyebrow": "Sashimi-Grade Fish",
        "description": "Daily filleted Norwegian salmon, yellowfin tuna, and tiger shrimp paired with seasoned Japanese rice.",
    },
    "sushi-sets": {
        "db_category": "SushiSet",
        "title": "Signature Sushi Rolls & Sets",
        "eyebrow": "Chef's Selection",
        "description": "Our signature specialty rolls including Philadelphia, Dragon Unagi, Spicy Tuna, and Zen Vegetarian.",
    },
}


def _base_url() -> str:
    return request.url_root.rstrip("/") if request else current_app.config["SITE_URL"]


def _build_cart_summary():
    cart = session.get("cart", {})
    cart_items = []
    total = 0.0
    total_qty = 0
    for product_id, quantity in cart.items():
        product = db.session.get(Product, int(product_id))
        if product and quantity > 0:
            subtotal = round(product.price * quantity, 2)
            total += subtotal
            total_qty += quantity
            cart_items.append({"product": product, "quantity": quantity, "subtotal": subtotal})
    return cart_items, round(total, 2), total_qty


@main_bp.route("/")
def index():
    featured = Product.query.filter_by(is_featured=True).limit(6).all()
    if not featured:
        featured = Product.query.limit(6).all()
    pizzas_count = Product.query.filter_by(category="Pizza").count()
    sushi_count = Product.query.filter_by(category="Sushi").count()
    sets_count = Product.query.filter_by(category="SushiSet").count()
    cities = get_all_cities()
    base_url = _base_url()
    schemas = [build_restaurant_schema(base_url)]
    return render_template(
        "index.html",
        featured=featured,
        counts={"pizza": pizzas_count, "sushi": sushi_count, "sets": sets_count},
        cities=cities,
        active_page="main",
        seo={
            "title": "NidePizza — Wood-Fired Pizza & Fresh Sushi Delivery in the Netherlands",
            "description": "Order 48-hour sourdough Neapolitan pizza and sashimi-grade hand-rolled sushi online. 30-minute delivery across Amsterdam, Rotterdam, Utrecht & more.",
            "canonical": f"{base_url}/",
            "og_image": f"{base_url}/og-image/default.png",
        },
        schemas=schemas,
    )


@main_bp.route("/menu")
@main_bp.route("/menu/<category_slug>")
def menu(category_slug: str = "all"):
    key = category_slug.lower()
    if key not in CATEGORY_META:
        abort(404)
    meta = CATEGORY_META[key]
    query = Product.query
    if meta["db_category"]:
        query = query.filter_by(category=meta["db_category"])
    products = query.order_by(Product.id.asc()).all()
    base_url = _base_url()
    crumbs = [("Home", "/"), ("Menu", "/menu")]
    if key != "all":
        crumbs.append((meta["title"], f"/menu/{key}"))
    return render_template(
        "menu.html",
        products=products,
        category_key=key,
        meta=meta,
        active_page=key if key != "all" else "menu",
        seo={
            "title": f"{meta['title']} | NidePizza",
            "description": meta["description"],
            "canonical": f"{base_url}/menu" if key == "all" else f"{base_url}/menu/{key}",
            "og_image": f"{base_url}/og-image/page/{key}.png",
        },
        schemas=[build_breadcrumb_schema(base_url, crumbs)],
    )


# Legacy route compatibility
@main_bp.route("/sushi")
def sushi_legacy():
    return menu("sushi")


@main_bp.route("/sushiset")
def sushiset_legacy():
    return menu("sushi-sets")


@main_bp.route("/product/<slug>")
def product_detail(slug: str):
    product = Product.query.filter_by(slug=slug).first()
    if not product:
        abort(404)
    related = (
        Product.query.filter(Product.category == product.category, Product.id != product.id)
        .limit(3)
        .all()
    )
    base_url = _base_url()
    cat_slug = "pizza" if product.category == "Pizza" else ("sushi-sets" if product.category == "SushiSet" else "sushi")
    schemas = [
        build_product_schema(base_url, product),
        build_breadcrumb_schema(
            base_url,
            [
                ("Home", "/"),
                ("Menu", "/menu"),
                (product.category, f"/menu/{cat_slug}"),
                (product.name, f"/product/{product.slug}"),
            ],
        ),
    ]
    return render_template(
        "product_detail.html",
        product=product,
        related=related,
        cat_slug=cat_slug,
        active_page="menu",
        seo={
            "title": f"{product.name} — Order Online | NidePizza",
            "description": f"{product.name} (€{product.price:.2f}, {product.weight or '300g'}). {product.description}",
            "canonical": f"{base_url}/product/{product.slug}",
            "og_image": f"{base_url}/og-image/product/{product.slug}.png",
            "og_type": "product",
        },
        schemas=schemas,
    )


@main_bp.route("/cart")
def cart():
    cart_items, total, _ = _build_cart_summary()
    base_url = _base_url()
    return render_template(
        "cart.html",
        cart_items=cart_items,
        total=total,
        cities=get_all_cities(),
        active_page="cart",
        seo={
            "title": "Your Cart | NidePizza",
            "description": "Review your pizza and sushi order and complete checkout with iDEAL or card.",
            "canonical": f"{base_url}/cart",
            "robots": "noindex, follow",
        },
    )


@main_bp.route("/add_to_cart/<int:product_id>", methods=["POST"])
def add_to_cart(product_id: int):
    product = db.session.get(Product, product_id)
    if not product:
        abort(404)
    cart_data = session.get("cart", {})
    cart_data[str(product_id)] = cart_data.get(str(product_id), 0) + 1
    session["cart"] = cart_data
    session.modified = True

    if request.headers.get("X-Requested-With") == "XMLHttpRequest" or request.is_json:
        _, total, total_qty = _build_cart_summary()
        return jsonify({"ok": True, "product_name": product.name, "cart_count": total_qty, "cart_total": total})

    return redirect(request.referrer or url_for("main.menu"))


@main_bp.route("/cart/update/<int:product_id>", methods=["POST"])
def update_cart(product_id: int):
    action = request.form.get("action", "inc")
    cart_data = session.get("cart", {})
    key = str(product_id)
    current_qty = cart_data.get(key, 0)

    if action == "inc":
        cart_data[key] = current_qty + 1
    elif action == "dec":
        if current_qty > 1:
            cart_data[key] = current_qty - 1
        else:
            cart_data.pop(key, None)
    elif action == "remove":
        cart_data.pop(key, None)

    session["cart"] = cart_data
    session.modified = True
    return redirect(url_for("main.cart"))


@main_bp.route("/checkout", methods=["POST"])
def checkout():
    cart_data = session.get("cart", {})
    if not cart_data:
        return redirect(url_for("main.cart"))

    phone = request.form.get("phone", "").strip()
    customer_name = request.form.get("customer_name", "").strip()[:120]
    delivery_city = request.form.get("delivery_city", "Amsterdam").strip()[:80]
    delivery_address = request.form.get("delivery_address", "").strip()[:240]

    if not re.match(r"^\+\d{7,15}$", phone):
        cart_items, total, _ = _build_cart_summary()
        return (
            render_template(
                "cart.html",
                cart_items=cart_items,
                total=total,
                cities=get_all_cities(),
                active_page="cart",
                error="Please enter a valid international phone number (e.g. +31612345678).",
                seo={"title": "Your Cart | NidePizza", "robots": "noindex, follow"},
            ),
            400,
        )

    order = Order(
        phone=phone,
        customer_name=customer_name or None,
        delivery_city=delivery_city or None,
        delivery_address=delivery_address or None,
        total=0.0,
    )
    db.session.add(order)

    total = 0.0
    for product_id, quantity in cart_data.items():
        product = db.session.get(Product, int(product_id))
        if product and quantity > 0:
            subtotal = round(product.price * quantity, 2)
            total += subtotal
            db.session.add(
                OrderItem(
                    order=order,
                    product_id=product.id,
                    name=product.name,
                    quantity=quantity,
                    subtotal=subtotal,
                )
            )

    order.total = round(total, 2)
    db.session.commit()

    # Log order
    log_lines = [f"Order #{order.id} | Phone: {order.phone} | City: {order.delivery_city or '-'} | Total: €{order.total:.2f}"]
    for item in order.items:
        log_lines.append(f"  - {item.name} x{item.quantity} = €{item.subtotal:.2f}")
    logger.info("\n".join(log_lines))

    # Clear cart
    session.pop("cart", None)

    # Attempt Mollie checkout if configured; otherwise go to local confirmation
    try:
        checkout_url = create_mollie_payment(order, phone)
        if checkout_url:
            return redirect(checkout_url)
    except Exception as exc:
        logger.error("Mollie payment creation failed for order #%s: %s", order.id, exc)

    # Local dev / fallback confirmation + Telegram notification
    msg_lines = [f"<b>New Order #{order.id}</b>", f"Phone: {order.phone}"]
    if order.delivery_city:
        msg_lines.append(f"City: {order.delivery_city}")
    for item in order.items:
        msg_lines.append(f"• {item.name} x{item.quantity} = €{item.subtotal:.2f}")
    msg_lines.append(f"<b>Total: €{order.total:.2f}</b>")
    send_telegram_message("\n".join(msg_lines))

    return redirect(url_for("main.payment_success", order_id=order.id))


@main_bp.route("/mollie_webhook", methods=["POST"])
def mollie_webhook():
    payment_id = request.form.get("id")
    if not payment_id:
        return "Missing payment ID", 400

    payment = fetch_mollie_payment(payment_id)
    if payment and payment.is_paid():
        order_id = payment.metadata.get("order_id")
        order = db.session.get(Order, int(order_id)) if order_id else None
        if order and not order.is_paid:
            order.is_paid = True
            order.payment_id = payment_id
            db.session.commit()

            msg_lines = [
                f"<b>Paid Order #{order.id}</b>",
                f"Phone: {order.phone}",
            ]
            for item in order.items:
                msg_lines.append(f"• {item.name} x{item.quantity} = €{item.subtotal:.2f}")
            msg_lines.append(f"<b>Total: €{order.total:.2f}</b>")
            send_telegram_message("\n".join(msg_lines))
    return "", 200


@main_bp.route("/payment_success")
def payment_success():
    order_id = request.args.get("order_id", type=int)
    order = db.session.get(Order, order_id) if order_id else None
    base_url = _base_url()
    return render_template(
        "checkout_success.html",
        order=order,
        active_page="cart",
        seo={
            "title": "Order Confirmed | NidePizza",
            "canonical": f"{base_url}/payment_success",
            "robots": "noindex, follow",
        },
    )


@main_bp.route("/about")
def about():
    base_url = _base_url()
    return render_template(
        "about.html",
        cities=get_all_cities(),
        active_page="about",
        seo={
            "title": "About NidePizza — Our Story, Craft & Kitchens",
            "description": "Founded in Amsterdam in 2024, NidePizza brings together 48-hour sourdough Neapolitan pizza and sashimi-grade Japanese sushi.",
            "canonical": f"{base_url}/about",
            "og_image": f"{base_url}/og-image/page/about.png",
        },
        schemas=[build_breadcrumb_schema(base_url, [("Home", "/"), ("About Us", "/about")])],
    )
