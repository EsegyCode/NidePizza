import io
import json
import re
import xml.etree.ElementTree as ET
import pytest
from PIL import Image

from app import create_app
from app.config import TestConfig
from app.models import Order, Product


@pytest.fixture
def client():
    app = create_app(TestConfig)
    with app.test_client() as client:
        yield client


def test_core_and_legacy_pages(client):
    for path in ["/", "/menu", "/menu/pizza", "/menu/sushi", "/menu/sushi-sets", "/sushi", "/sushiset", "/about", "/orders", "/admin/add-product"]:
        res = client.get(path)
        assert res.status_code == 200, f"Expected 200 for {path}, got {res.status_code}"


def test_legal_pages(client):
    for path in ["/privacy", "/terms", "/cookies", "/allergens-delivery"]:
        res = client.get(path)
        assert res.status_code == 200, f"Expected 200 for {path}"


def test_geo_pages(client):
    res = client.get("/locations")
    assert res.status_code == 200
    assert b"Amsterdam" in res.data

    for city in ["amsterdam", "rotterdam", "utrecht", "den-haag", "haarlem", "eindhoven"]:
        city_res = client.get(f"/delivery/{city}")
        assert city_res.status_code == 200

    assert client.get("/delivery/unknown-city").status_code == 404


def test_product_detail_and_jsonld(client):
    with client.application.app_context():
        prod = Product.query.first()
        assert prod is not None and prod.slug

    res = client.get(f"/product/{prod.slug}")
    assert res.status_code == 200
    html = res.data.decode("utf-8")

    # Verify JSON-LD scripts parse cleanly
    scripts = re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.S)
    assert len(scripts) >= 2
    types = [json.loads(s)["@type"] for s in scripts]
    assert "Product" in types
    assert "BreadcrumbList" in types


def test_geo_city_jsonld_has_restaurant_and_faq(client):
    res = client.get("/delivery/amsterdam")
    assert res.status_code == 200
    html = res.data.decode("utf-8")
    scripts = re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.S)
    types = [json.loads(s)["@type"] for s in scripts]
    assert "Restaurant" in types
    assert "FAQPage" in types
    assert "BreadcrumbList" in types


def test_robots_sitemap_and_llms(client):
    robots = client.get("/robots.txt")
    assert robots.status_code == 200
    assert b"Sitemap:" in robots.data
    assert b"llms.txt" in robots.data

    sitemap = client.get("/sitemap.xml")
    assert sitemap.status_code == 200
    root = ET.fromstring(sitemap.data)
    locs = [el.text for el in root.findall(".//{http://www.sitemaps.org/schemas/sitemap/0.9}loc")]
    assert any("/menu/pizza" in loc for loc in locs)
    assert any("/delivery/amsterdam" in loc for loc in locs)
    assert any("/product/" in loc for loc in locs)

    llms = client.get("/llms.txt")
    assert llms.status_code == 200
    assert b"# NidePizza" in llms.data

    llms_full = client.get("/llms-full.txt")
    assert llms_full.status_code == 200
    assert b"Margherita Classica" in llms_full.data


def test_og_image_generation(client):
    with client.application.app_context():
        prod = Product.query.first()

    for path in [
        "/og-image/default.png",
        f"/og-image/product/{prod.slug}.png",
        "/og-image/city/amsterdam.png",
        "/og-image/page/pizza.png",
    ]:
        res = client.get(path)
        assert res.status_code == 200, f"OG image failed for {path}"
        assert res.mimetype == "image/png"
        img = Image.open(io.BytesIO(res.data))
        assert img.size == (1200, 630)


def test_cart_and_checkout_flow(client):
    with client.application.app_context():
        prod = Product.query.first()

    # AJAX add to cart
    add_res = client.post(
        f"/add_to_cart/{prod.id}",
        headers={"X-Requested-With": "XMLHttpRequest"},
    )
    assert add_res.status_code == 200
    data = add_res.get_json()
    assert data["ok"] is True
    assert data["cart_count"] == 1

    # Increment quantity
    client.post(f"/cart/update/{prod.id}", data={"action": "inc"})
    cart_page = client.get("/cart")
    assert cart_page.status_code == 200
    assert prod.name.encode("utf-8") in cart_page.data

    # Invalid phone returns 400
    bad_checkout = client.post("/checkout", data={"phone": "12345"})
    assert bad_checkout.status_code == 400

    # Valid checkout redirects to payment_success and persists order
    good_checkout = client.post(
        "/checkout",
        data={
            "phone": "+31612345678",
            "customer_name": "Tester",
            "delivery_city": "Amsterdam",
            "delivery_address": "Keizersgracht 1",
        },
        follow_redirects=True,
    )
    assert good_checkout.status_code == 200
    assert b"Thank you for your order!" in good_checkout.data

    with client.application.app_context():
        order = Order.query.first()
        assert order is not None
        assert order.phone == "+31612345678"
        assert order.total == pytest.approx(prod.price * 2)
