from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = 'your_secret_key'

products_pizza = [
    {"id": 1, "name": "Margherita Pizza", "description": "Thin crust, tomato sauce, mozzarella, fresh basil", "price": 10, "image": "margherita.png"},
    {"id": 2, "name": "Hawaiian Chicken", "description": "Thin crust, tomato sauce, mozzarella, pineapple, grilled chicken", "price": 12, "image": "hawaiian.png"},
    {"id": 3, "name": "Pepperoni Feast", "description": "Classic crust, tomato sauce, mozzarella, spicy pepperoni slices", "price": 13, "image": "pepperoni.png"},
    {"id": 4, "name": "Veggie Delight", "description": "Thin crust, tomato sauce, mozzarella, bell peppers, olives, mushrooms, onions", "price": 11, "image": "veggie.png"},
    {"id": 5, "name": "BBQ Chicken", "description": "Thick crust, BBQ sauce base, mozzarella, smoked chicken, red onions, cilantro", "price": 13, "image": "bbq_chicken.png"},
    {"id": 6, "name": "Four Cheese", "description": "Thin crust, creamy white sauce, mozzarella, cheddar, parmesan, gorgonzola", "price": 14, "image": "four_cheese.png"}
]

products_sushi = [
    {"id": 101, "name": "Philadelphia Roll", "description": "Rice, nori, fresh salmon, cream cheese, avocado", "price": 12, "image": "philadelphia.png"},
    {"id": 102, "name": "California Roll", "description": "Rice, nori, surimi crab, avocado, cucumber, sesame seeds", "price": 10.5, "image": "california.png"},
    {"id": 103, "name": "Spicy Tuna Roll", "description": "Rice, nori, raw tuna, spicy mayo, cucumber, chili flakes", "price": 11.5, "image": "spicy_tuna.png"},
    {"id": 104, "name": "Dragon Roll", "description": "Rice, nori, shrimp tempura, eel, avocado, eel sauce", "price": 13.5, "image": "dragon.png"},
    {"id": 105, "name": "Ebi Tempura Roll", "description": "Rice, nori, tempura shrimp, lettuce, cucumber, spicy sauce", "price": 11.5, "image": "ebi_tempura.png"},
    {"id": 106, "name": "Vegetarian Roll", "description": "Rice, nori, avocado, cucumber, carrot, tofu, sesame seeds", "price": 9.5, "image": "vegetarian.png"}
]

all_products = products_pizza + products_sushi

# Глобальный список для хранения заказов
orders = []

@app.route("/")
def index():
    return render_template("index.html", products=all_products, active_page='main')

@app.route("/pizza")
def pizza():
    return render_template("shop.html", products=products_pizza, category="Pizza", active_page='pizza')

@app.route("/sushi")
def sushi():
    return render_template("shop.html", products=products_sushi, category="Sushi", active_page='sushi')

@app.route("/cart")
def cart():
    cart = session.get("cart", {})
    cart_items = []
    total = 0

    for product_id, quantity in cart.items():
        product = next((p for p in all_products if p["id"] == int(product_id)), None)
        if product:
            subtotal = product["price"] * quantity
            total += subtotal
            cart_items.append({
                "product": product,
                "quantity": quantity,
                "subtotal": subtotal
            })

    return render_template("cart.html", cart_items=cart_items, total=total)

@app.route("/add_to_cart/<int:product_id>", methods=["POST"])
def add_to_cart(product_id):
    cart = session.get("cart", {})
    cart[str(product_id)] = cart.get(str(product_id), 0) + 1
    session["cart"] = cart
    return redirect(url_for("index"))

@app.route('/about')
def about():
    return render_template("about.html")

@app.route('/checkout', methods=['POST'])
def checkout():
    cart = session.get('cart', {})
    if not cart:
        return redirect(url_for('cart'))  # корзина пустая, перенаправляем назад

    # Собираем детали заказа (продукты + кол-во)
    order_items = []
    total = 0
    for product_id, quantity in cart.items():
        product = next((p for p in all_products if p["id"] == int(product_id)), None)
        if product:
            subtotal = product["price"] * quantity
            total += subtotal
            order_items.append({
                "product_id": product["id"],
                "name": product["name"],
                "quantity": quantity,
                "subtotal": subtotal
            })

    order = {
        "items": order_items,
        "total": total
    }

    # Добавляем заказ в глобальный массив заказов
    orders.append(order)

    # Очищаем корзину пользователя
    session.pop('cart', None)

    return render_template('checkout_success.html', order=order)

# Новый маршрут для просмотра всех заказов
@app.route('/orders')
def show_orders():
    return render_template('orders.html', orders=orders)

if __name__ == "__main__":
    app.run(debug=True)