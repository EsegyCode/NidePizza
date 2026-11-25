"""JSON-LD Schema.org builders for SEO & GEO structured data."""

from flask import current_app


def build_restaurant_schema(base_url: str, city_data: dict | None = None) -> dict:
    addr = current_app.config["BUSINESS_ADDRESS"]
    city_name = city_data["name"] if city_data else addr["city"]
    region_name = city_data["region"] if city_data else addr["region"]

    schema = {
        "@context": "https://schema.org",
        "@type": "Restaurant",
        "name": f"{current_app.config['BRAND_NAME']} — {city_name}" if city_data else current_app.config["BRAND_NAME"],
        "url": f"{base_url}/delivery/{city_data['slug']}" if city_data else base_url,
        "image": f"{base_url}/og-image/default.png",
        "telephone": current_app.config["BUSINESS_PHONE"],
        "email": current_app.config["BUSINESS_EMAIL"],
        "servesCuisine": ["Italian", "Neapolitan Pizza", "Japanese", "Sushi"],
        "priceRange": "€€",
        "acceptsReservations": "False",
        "openingHours": current_app.config["OPENING_HOURS"],
        "menu": f"{base_url}/menu",
        "address": {
            "@type": "PostalAddress",
            "streetAddress": addr["street"],
            "addressLocality": city_name,
            "addressRegion": region_name,
            "postalCode": addr["postal_code"],
            "addressCountry": addr["country"],
        },
        "areaServed": {
            "@type": "City",
            "name": city_name,
        },
    }
    if city_data:
        schema["geo"] = {
            "@type": "GeoCoordinates",
            "latitude": city_data["lat"],
            "longitude": city_data["lng"],
        }
    return schema


def build_product_schema(base_url: str, product) -> dict:
    return {
        "@context": "https://schema.org",
        "@type": "Product",
        "name": product.name,
        "description": product.description,
        "image": f"{base_url}/static/img/{product.image}",
        "category": product.category,
        "brand": {
            "@type": "Brand",
            "name": current_app.config["BRAND_NAME"],
        },
        "offers": {
            "@type": "Offer",
            "url": f"{base_url}/product/{product.slug}",
            "priceCurrency": current_app.config.get("CURRENCY", "EUR"),
            "price": f"{product.price:.2f}",
            "availability": "https://schema.org/InStock",
        },
    }


def build_breadcrumb_schema(base_url: str, items: list[tuple[str, str]]) -> dict:
    """items: list of (label, relative_path)."""
    return {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {
                "@type": "ListItem",
                "position": idx,
                "name": label,
                "item": f"{base_url}{path}",
            }
            for idx, (label, path) in enumerate(items, start=1)
        ],
    }


def build_faq_schema(faqs: list[dict]) -> dict:
    return {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name": item["q"],
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": item["a"],
                },
            }
            for item in faqs
        ],
    }
