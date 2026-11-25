import re
from app.extensions import db
from app.models import Product


def slugify(text: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return slug


PIZZA_PRODUCTS = [
    {
        "name": "Margherita Classica",
        "description": "San Marzano DOP tomato sauce, fior di latte mozzarella, fresh basil leaves, extra virgin olive oil on 48h fermented sourdough.",
        "price": 13.50,
        "image": "margherita.png",
        "category": "Pizza",
        "weight": "420g",
        "badge": "Vegetarian",
        "is_featured": True,
    },
    {
        "name": "Pepperoni Diavola",
        "description": "Crispy artisan pepperoni cups, fior di latte, San Marzano tomato base, oregano, and chili-infused honey drizzle.",
        "price": 15.50,
        "image": "pepperoni.png",
        "category": "Pizza",
        "weight": "450g",
        "badge": "Bestseller",
        "is_featured": True,
    },
    {
        "name": "Quattro Formaggi",
        "description": "Creamy white base with mozzarella, aged Parmigiano Reggiano, gorgonzola dolce, and smoked provolone.",
        "price": 15.00,
        "image": "four_cheese.png",
        "category": "Pizza",
        "weight": "440g",
        "badge": "Vegetarian",
        "is_featured": False,
    },
    {
        "name": "Smoky BBQ Chicken",
        "description": "Char-grilled free-range chicken, smoky hickory BBQ glaze, red onion, sweetcorn, and melted mozzarella.",
        "price": 16.00,
        "image": "bbq_chicken.png",
        "category": "Pizza",
        "weight": "470g",
        "badge": "Chef's Pick",
        "is_featured": True,
    },
    {
        "name": "Bianca Tartufo",
        "description": "Velvety truffle cream, fior di latte, wild mushrooms, parmesan shavings, and fresh thyme.",
        "price": 16.50,
        "image": "bianka.png",
        "category": "Pizza",
        "weight": "430g",
        "badge": "Gourmet",
        "is_featured": False,
    },
    {
        "name": "Hawaiian Tropica",
        "description": "Roasted honey ham, caramelized golden pineapple, fior di latte mozzarella, and San Marzano tomato sauce.",
        "price": 14.50,
        "image": "hawaiian.png",
        "category": "Pizza",
        "weight": "450g",
        "badge": None,
        "is_featured": False,
    },
    {
        "name": "Veggie Garden",
        "description": "Roasted bell peppers, Kalamata olives, courgette ribbons, cherry tomatoes, red onion, and basil pesto.",
        "price": 14.00,
        "image": "veggie.png",
        "category": "Pizza",
        "weight": "440g",
        "badge": "Vegetarian",
        "is_featured": False,
    },
]

SUSHI_PRODUCTS = [
    {"name": "Philadelphia Classic", "description": "Fresh Norwegian salmon, velvety cream cheese, seasoned sushi rice, crisp cucumber.", "price": 12.00, "image": "1.png", "weight": "300g", "badge": "Bestseller", "is_featured": True},
    {"name": "Cheese Roll", "description": "Salted salmon, cream cheese, aged cheddar, seasoned rice, cucumber, unagi glaze.", "price": 12.50, "image": "2.png", "weight": "300g", "badge": None, "is_featured": False},
    {"name": "Ebi Red", "description": "Tiger shrimp, cream cheese, avocado, spicy mayo, masago tobiko roe.", "price": 13.00, "image": "3.png", "weight": "300g", "badge": "Spicy", "is_featured": False},
    {"name": "Futomaki Seafood Mix", "description": "Tiger shrimp, fresh salmon, snow crab, crisp cucumber, spicy chef sauce.", "price": 13.50, "image": "4.png", "weight": "310g", "badge": "Chef's Pick", "is_featured": True},
    {"name": "Tiger Roll", "description": "Tiger shrimp, salted salmon, cream cheese, cucumber, ripe avocado, unagi sauce.", "price": 13.00, "image": "5.png", "weight": "300g", "badge": None, "is_featured": False},
    {"name": "Samurai", "description": "Salted salmon, cream cheese, cucumber, roasted sesame seeds, unagi glaze.", "price": 12.00, "image": "6.png", "weight": "300g", "badge": None, "is_featured": False},
    {"name": "Sicario", "description": "Salted salmon, snow crab, cream cheese, cucumber, spicy sauce, masago roe.", "price": 13.00, "image": "7.png", "weight": "300g", "badge": "Spicy", "is_featured": False},
    {"name": "Kappa Green", "description": "Salted salmon, snow crab, cream cheese, cucumber, toasted sesame.", "price": 12.00, "image": "8.png", "weight": "300g", "badge": None, "is_featured": False},
    {"name": "California Syake Sesame", "description": "Salted salmon, ripe avocado, crisp cucumber, toasted sesame seeds.", "price": 12.00, "image": "9.png", "weight": "290g", "badge": None, "is_featured": False},
    {"name": "Green Day", "description": "Salted salmon, snow crab, masago roe, seasoned rice, fresh cucumber.", "price": 12.50, "image": "10.png", "weight": "300g", "badge": None, "is_featured": False},
    {"name": "California Ebi in Roe", "description": "Tiger shrimp, masago roe, avocado, cucumber, spicy chef drizzle.", "price": 13.00, "image": "11.png", "weight": "300g", "badge": None, "is_featured": False},
    {"name": "Philadelphia Combo", "description": "Double-fish roll with tiger shrimp, fresh salmon, cream cheese, cucumber.", "price": 14.00, "image": "12.png", "weight": "320g", "badge": "Chef's Pick", "is_featured": False},
    {"name": "Futomaki with Salmon", "description": "Salted salmon, cream cheese, masago roe, spicy sauce, cucumber.", "price": 12.50, "image": "13.png", "weight": "300g", "badge": None, "is_featured": False},
    {"name": "Philadelphia with Eel", "description": "Smoked unagi eel, cream cheese, unagi glaze, crisp cucumber.", "price": 14.50, "image": "14.png", "weight": "300g", "badge": "Gourmet", "is_featured": False},
    {"name": "Philadelphia with Shrimp", "description": "Sweet tiger shrimp, cream cheese, seasoned sushi rice, cucumber.", "price": 13.00, "image": "15.png", "weight": "300g", "badge": None, "is_featured": False},
    {"name": "Hurricane", "description": "Salted salmon, cream cheese, avocado, unagi sauce.", "price": 12.50, "image": "16.png", "weight": "300g", "badge": None, "is_featured": False},
    {"name": "Light Life", "description": "Yellowfin tuna, salted salmon, snow crab, cream cheese, spicy sauce.", "price": 13.50, "image": "17.png", "weight": "300g", "badge": None, "is_featured": False},
    {"name": "Okayama", "description": "Tiger shrimp, cream cheese, cucumber, white sesame, unagi sauce.", "price": 12.50, "image": "18.png", "weight": "300g", "badge": None, "is_featured": False},
    {"name": "Futomaki with Tuna", "description": "Yellowfin tuna, cream cheese, avocado, cucumber, spicy sauce.", "price": 13.50, "image": "19.png", "weight": "300g", "badge": "Spicy", "is_featured": False},
    {"name": "Kani Red", "description": "Snow crab, cream cheese, masago roe, seasoned rice, cucumber.", "price": 12.50, "image": "20.png", "weight": "300g", "badge": None, "is_featured": False},
    {"name": "Banzai", "description": "Salted salmon, masago roe, cream cheese, cucumber, spicy sauce.", "price": 13.00, "image": "21.png", "weight": "300g", "badge": "Spicy", "is_featured": False},
]

SUSHI_SET_PRODUCTS = [
    {"name": "Philadelphia Signature Roll", "description": "Nori, seasoned rice, fresh Norwegian salmon, cream cheese, ripe avocado.", "price": 12.50, "image": "philadelphia.png", "weight": "320g", "badge": "Bestseller", "is_featured": True},
    {"name": "California Classic Roll", "description": "Nori, seasoned rice, surimi crab, avocado, cucumber, toasted sesame seeds.", "price": 10.50, "image": "california.png", "weight": "290g", "badge": None, "is_featured": False},
    {"name": "Spicy Tuna Roll", "description": "Nori, seasoned rice, raw yellowfin tuna, sriracha mayo, cucumber, chili flakes.", "price": 11.50, "image": "spicy_tuna.png", "weight": "300g", "badge": "Spicy", "is_featured": False},
    {"name": "Dragon Unagi Roll", "description": "Shrimp tempura, glazed smoked eel, creamy avocado, sweet tare unagi sauce.", "price": 14.50, "image": "dragon.png", "weight": "330g", "badge": "Chef's Pick", "is_featured": True},
    {"name": "Ebi Tempura Crunch", "description": "Crispy tempura shrimp, butterhead lettuce, cucumber, spicy chef sauce.", "price": 12.00, "image": "ebi_tempura.png", "weight": "310g", "badge": None, "is_featured": False},
    {"name": "Zen Vegetarian Roll", "description": "Creamy avocado, crisp cucumber, sweet carrot, marinated tofu, sesame seeds.", "price": 9.50, "image": "vegetarian.png", "weight": "280g", "badge": "Vegetarian", "is_featured": False},
]


def ensure_seed_data() -> int:
    """Populate initial products if missing and backfill slugs for existing rows."""
    # Backfill slugs on any existing products from legacy DB
    existing = Product.query.all()
    if existing:
        changed = False
        for prod in existing:
            if not prod.slug:
                prod.slug = f"{slugify(prod.name)}-{prod.id}"
                changed = True
            if not prod.weight:
                prod.weight = "300g"
                changed = True
        # Also add Pizza items if legacy DB only had Sushi/SushiSet
        has_pizza = any(p.category == "Pizza" for p in existing)
        if not has_pizza:
            for item in PIZZA_PRODUCTS:
                db.session.add(Product(slug=slugify(item["name"]), **item))
            changed = True
        if changed:
            db.session.commit()
        return 0

    added = 0
    for item in PIZZA_PRODUCTS:
        db.session.add(Product(slug=slugify(item["name"]), **item))
        added += 1

    for item in SUSHI_PRODUCTS:
        db.session.add(Product(slug=slugify(item["name"]), category="Sushi", **item))
        added += 1

    for item in SUSHI_SET_PRODUCTS:
        db.session.add(Product(slug=slugify(item["name"]), category="SushiSet", **item))
        added += 1

    db.session.commit()
    return added
