from flask import Blueprint, abort, current_app, render_template, request
from app.geo_data import get_all_cities, get_city
from app.models import Product
from app.services.seo_schema import (
    build_breadcrumb_schema,
    build_faq_schema,
    build_restaurant_schema,
)

geo_bp = Blueprint("geo", __name__)


def _base_url() -> str:
    return request.url_root.rstrip("/") if request else current_app.config["SITE_URL"]


@geo_bp.route("/locations")
def locations():
    cities = get_all_cities()
    base_url = _base_url()
    return render_template(
        "locations.html",
        cities=cities,
        active_page="locations",
        seo={
            "title": "Delivery Locations in the Netherlands | NidePizza",
            "description": "Fast 25–40 min pizza & sushi delivery across Amsterdam, Rotterdam, Utrecht, Den Haag, Haarlem, and Eindhoven.",
            "canonical": f"{base_url}/locations",
            "og_image": f"{base_url}/og-image/page/locations.png",
        },
        schemas=[
            build_restaurant_schema(base_url),
            build_breadcrumb_schema(base_url, [("Home", "/"), ("Delivery Locations", "/locations")]),
        ],
    )


@geo_bp.route("/delivery/<city_slug>")
def city_landing(city_slug: str):
    city = get_city(city_slug)
    if not city:
        abort(404)

    featured = Product.query.filter_by(is_featured=True).limit(6).all()
    if not featured:
        featured = Product.query.limit(6).all()

    base_url = _base_url()
    schemas = [
        build_restaurant_schema(base_url, city_data=city),
        build_breadcrumb_schema(
            base_url,
            [
                ("Home", "/"),
                ("Delivery Locations", "/locations"),
                (city["name"], f"/delivery/{city['slug']}"),
            ],
        ),
    ]
    if city.get("faqs"):
        schemas.append(build_faq_schema(city["faqs"]))

    return render_template(
        "geo_city.html",
        city=city,
        other_cities=[c for c in get_all_cities() if c["slug"] != city["slug"]],
        featured=featured,
        active_page="locations",
        seo={
            "title": f"{city['headline']} | NidePizza",
            "description": city["summary"],
            "canonical": f"{base_url}/delivery/{city['slug']}",
            "og_image": f"{base_url}/og-image/city/{city['slug']}.png",
        },
        schemas=schemas,
    )
