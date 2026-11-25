from flask import Blueprint, current_app, render_template, request
from app.services.seo_schema import build_breadcrumb_schema

legal_bp = Blueprint("legal", __name__)


def _base_url() -> str:
    return request.url_root.rstrip("/") if request else current_app.config["SITE_URL"]


@legal_bp.route("/privacy")
def privacy():
    base_url = _base_url()
    return render_template(
        "legal/privacy.html",
        active_page="legal",
        seo={
            "title": "Privacy Policy (GDPR) | NidePizza",
            "description": "How NidePizza collects, processes, and protects your personal data under EU GDPR regulations.",
            "canonical": f"{base_url}/privacy",
            "og_image": f"{base_url}/og-image/page/legal.png",
        },
        schemas=[build_breadcrumb_schema(base_url, [("Home", "/"), ("Privacy Policy", "/privacy")])],
    )


@legal_bp.route("/terms")
def terms():
    base_url = _base_url()
    return render_template(
        "legal/terms.html",
        active_page="legal",
        seo={
            "title": "Terms & Conditions | NidePizza",
            "description": "Terms of service, online ordering, Mollie payments, and delivery conditions for NidePizza.",
            "canonical": f"{base_url}/terms",
            "og_image": f"{base_url}/og-image/page/legal.png",
        },
        schemas=[build_breadcrumb_schema(base_url, [("Home", "/"), ("Terms & Conditions", "/terms")])],
    )


@legal_bp.route("/cookies")
def cookies():
    base_url = _base_url()
    return render_template(
        "legal/cookies.html",
        active_page="legal",
        seo={
            "title": "Cookie Policy | NidePizza",
            "description": "Details about essential session cookies used for your shopping cart at NidePizza.",
            "canonical": f"{base_url}/cookies",
            "og_image": f"{base_url}/og-image/page/legal.png",
        },
        schemas=[build_breadcrumb_schema(base_url, [("Home", "/"), ("Cookie Policy", "/cookies")])],
    )


@legal_bp.route("/allergens-delivery")
def allergens_delivery():
    base_url = _base_url()
    return render_template(
        "legal/delivery.html",
        active_page="legal",
        seo={
            "title": "Allergens, Nutrition & Delivery Info | NidePizza",
            "description": "Allergen guide (gluten, dairy, fish, crustaceans, sesame, soy) and dual-zone delivery standards at NidePizza.",
            "canonical": f"{base_url}/allergens-delivery",
            "og_image": f"{base_url}/og-image/page/legal.png",
        },
        schemas=[build_breadcrumb_schema(base_url, [("Home", "/"), ("Allergens & Delivery", "/allergens-delivery")])],
    )
