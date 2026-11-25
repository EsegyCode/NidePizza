from datetime import date
from xml.sax.saxutils import escape
from flask import Blueprint, Response, abort, current_app, request
from app.geo_data import get_all_cities, get_city
from app.models import Product
from app.services.og_image import generate_og_image

seo_bp = Blueprint("seo", __name__)


def _base_url() -> str:
    return request.url_root.rstrip("/") if request else current_app.config["SITE_URL"]


@seo_bp.route("/robots.txt")
def robots_txt():
    base_url = _base_url()
    lines = [
        "User-agent: *",
        "Allow: /",
        "Disallow: /admin",
        "Disallow: /orders",
        "Disallow: /cart",
        "Disallow: /checkout",
        "Disallow: /payment_success",
        "Disallow: /init_products",
        "",
        f"Sitemap: {base_url}/sitemap.xml",
        f"# LLM Context: {base_url}/llms.txt",
    ]
    return Response("\n".join(lines), mimetype="text/plain; charset=utf-8")


@seo_bp.route("/sitemap.xml")
def sitemap_xml():
    base_url = _base_url()
    today = date.today().isoformat()

    urls = [
        ("/", "1.0", "daily"),
        ("/menu", "0.9", "daily"),
        ("/menu/pizza", "0.9", "weekly"),
        ("/menu/sushi", "0.9", "weekly"),
        ("/menu/sushi-sets", "0.9", "weekly"),
        ("/locations", "0.8", "weekly"),
        ("/about", "0.7", "monthly"),
        ("/privacy", "0.3", "yearly"),
        ("/terms", "0.3", "yearly"),
        ("/cookies", "0.3", "yearly"),
        ("/allergens-delivery", "0.5", "monthly"),
    ]

    for city in get_all_cities():
        urls.append((f"/delivery/{city['slug']}", "0.8", "weekly"))

    for product in Product.query.order_by(Product.id.asc()).all():
        if product.slug:
            urls.append((f"/product/{product.slug}", "0.8", "weekly"))

    xml_parts = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]
    for path, priority, changefreq in urls:
        loc = escape(f"{base_url}{path}")
        xml_parts.append(
            f"  <url>\n"
            f"    <loc>{loc}</loc>\n"
            f"    <lastmod>{today}</lastmod>\n"
            f"    <changefreq>{changefreq}</changefreq>\n"
            f"    <priority>{priority}</priority>\n"
            f"  </url>"
        )
    xml_parts.append("</urlset>")
    return Response("\n".join(xml_parts), mimetype="application/xml; charset=utf-8")


@seo_bp.route("/llms.txt")
def llms_txt():
    base_url = _base_url()
    cities = get_all_cities()
    city_links = "\n".join(
        f"- [{c['name']} Delivery]({base_url}/delivery/{c['slug']}): {c['delivery_time']}, min order {c['min_order']}, {c['delivery_fee']}"
        for c in cities
    )
    content = f"""# NidePizza

> Artisan Wood-Fired Neapolitan Pizza & Fresh Hand-Rolled Sushi in the Netherlands. Daily 11:00–23:00 with dual-zone thermal delivery and iDEAL/card checkout via Mollie.

## Core Pages
- [Home]({base_url}/): Overview, featured dishes, and delivery cities
- [Full Menu]({base_url}/menu): All pizzas, sushi rolls, and sushi sets
- [Wood-Fired Pizza]({base_url}/menu/pizza): 48-hour sourdough Neapolitan pizzas
- [Fresh Sushi]({base_url}/menu/sushi): Hand-rolled maki & uramaki
- [Signature Sushi Sets]({base_url}/menu/sushi-sets): Chef specialty rolls
- [About Us]({base_url}/about): Kitchen craft, ingredients, and story
- [Full Catalog for LLMs]({base_url}/llms-full.txt): Complete itemized menu with prices and descriptions

## Delivery Locations (Netherlands)
{city_links}

## Legal & Policies
- [Privacy Policy (GDPR)]({base_url}/privacy)
- [Terms & Conditions]({base_url}/terms)
- [Cookie Policy]({base_url}/cookies)
- [Allergens & Delivery Standards]({base_url}/allergens-delivery)

## Contact
- Address: Keizersgracht 412, 1016 GC Amsterdam, Netherlands
- Phone: {current_app.config['BUSINESS_PHONE']}
- Email: {current_app.config['BUSINESS_EMAIL']}
"""
    return Response(content, mimetype="text/plain; charset=utf-8")


@seo_bp.route("/llms-full.txt")
def llms_full_txt():
    base_url = _base_url()
    products = Product.query.order_by(Product.category.asc(), Product.id.asc()).all()
    lines = [
        "# NidePizza — Complete Menu & Delivery Reference",
        "",
        f"Website: {base_url}",
        f"Opening Hours: {current_app.config['OPENING_HOURS']}",
        "Currency: EUR (€)",
        "",
        "## Menu Items",
    ]
    current_cat = None
    for p in products:
        if p.category != current_cat:
            current_cat = p.category
            lines.append("")
            lines.append(f"### {current_cat}")
        lines.append(
            f"- **{p.name}** (€{p.price:.2f}, {p.weight or '300g'}): {p.description} — {base_url}/product/{p.slug}"
        )

    lines.append("")
    lines.append("## Delivery Cities & FAQs")
    for c in get_all_cities():
        lines.append(f"### {c['name']} ({c['region']})")
        lines.append(f"URL: {base_url}/delivery/{c['slug']}")
        lines.append(f"Delivery: {c['delivery_time']} | Min Order: {c['min_order']} | Fee: {c['delivery_fee']}")
        lines.append(f"Neighborhoods: {', '.join(c['neighborhoods'])}")
        for faq in c.get("faqs", []):
            lines.append(f"Q: {faq['q']} A: {faq['a']}")
        lines.append("")

    return Response("\n".join(lines), mimetype="text/plain; charset=utf-8")


@seo_bp.route("/og-image/default.png")
def og_default():
    png = generate_og_image(
        static_dir=current_app.static_folder,
        title="Wood-Fired Pizza & Fresh Sushi",
        subtitle="48h sourdough Neapolitan pies & sashimi-grade rolls delivered in 30 minutes across the Netherlands.",
        eyebrow="NIDEPIZZA • ARTISAN KITCHEN",
        badge="Order Online • €9.50 – €16.50",
        image_filename="pizza1.jpg",
    )
    return Response(png, mimetype="image/png", headers={"Cache-Control": "public, max-age=86400"})


@seo_bp.route("/og-image/product/<slug>.png")
def og_product(slug: str):
    product = Product.query.filter_by(slug=slug).first()
    if not product:
        abort(404)
    png = generate_og_image(
        static_dir=current_app.static_folder,
        title=product.name,
        subtitle=product.description,
        eyebrow=f"NIDEPIZZA • {product.category.upper()}",
        badge=f"€{product.price:.2f} • {product.weight or '300g'}",
        image_filename=product.image,
    )
    return Response(png, mimetype="image/png", headers={"Cache-Control": "public, max-age=86400"})


@seo_bp.route("/og-image/city/<city_slug>.png")
def og_city(city_slug: str):
    city = get_city(city_slug)
    if not city:
        abort(404)
    png = generate_og_image(
        static_dir=current_app.static_folder,
        title=f"Pizza & Sushi in {city['name']}",
        subtitle=f"{city['delivery_time']} delivery across {', '.join(city['neighborhoods'][:3])}.",
        eyebrow=f"NIDEPIZZA • {city['region'].upper()}",
        badge=f"{city['delivery_time']} • {city['delivery_fee']}",
        image_filename="pizza2.jpg",
    )
    return Response(png, mimetype="image/png", headers={"Cache-Control": "public, max-age=86400"})


@seo_bp.route("/og-image/page/<page_key>.png")
def og_page(page_key: str):
    pages = {
        "all": ("Full Pizza & Sushi Menu", "Explore sourdough pizzas, hand-rolled maki, and chef signature sets.", "menu", "pizza1.jpg"),
        "menu": ("Full Pizza & Sushi Menu", "Explore sourdough pizzas, hand-rolled maki, and chef signature sets.", "menu", "pizza1.jpg"),
        "pizza": ("Artisan Wood-Fired Pizza", "48-hour fermented dough baked at 450°C with San Marzano tomatoes.", "pizza", "pepperoni.png"),
        "sushi": ("Fresh Hand-Rolled Sushi", "Norwegian salmon, yellowfin tuna, and tiger shrimp rolled to order.", "sushi", "1.png"),
        "sushi-sets": ("Signature Sushi Rolls", "Chef specialty rolls including Dragon Unagi and Philadelphia.", "sushi sets", "dragon.png"),
        "locations": ("Delivery Across the Netherlands", "Amsterdam, Rotterdam, Utrecht, Den Haag, Haarlem & Eindhoven.", "delivery", "pizza2.jpg"),
        "about": ("Our Story & Kitchen Craft", "Italian stone-oven tradition meets Japanese sushi mastery in Amsterdam.", "about us", "pizza2.jpg"),
        "legal": ("Policies, Allergens & Terms", "GDPR privacy, terms of service, cookies, and food allergen guide.", "legal & info", "pizza1.jpg"),
    }
    title, sub, tag, img = pages.get(page_key, pages["all"])
    png = generate_og_image(
        static_dir=current_app.static_folder,
        title=title,
        subtitle=sub,
        eyebrow=f"NIDEPIZZA • {tag.upper()}",
        badge="Fresh Daily 11:00–23:00",
        image_filename=img,
    )
    return Response(png, mimetype="image/png", headers={"Cache-Control": "public, max-age=86400"})
