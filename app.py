from flask import Flask, render_template, request, redirect, url_for, session
import requests
from flask_sqlalchemy import SQLAlchemy
import os
import re

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Telegram config
TELEGRAM_BOT_TOKEN = '7551814443:AAHBCiY0Q_6Fygmuu8JELvfWYarII5_yV1Q'
TELEGRAM_CHAT_ID = '-1002318381366'

# DB config
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'shop.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# MODELS
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    description = db.Column(db.Text)
    price = db.Column(db.Float)
    image = db.Column(db.String(120))
    category = db.Column(db.String(50))  # Pizza или Sushi

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    phone = db.Column(db.String(20))
    total = db.Column(db.Float)
    items = db.relationship('OrderItem', backref='order', lazy=True)

class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    product_id = db.Column(db.Integer)
    name = db.Column(db.String(120))
    quantity = db.Column(db.Integer)
    subtotal = db.Column(db.Float)

# INITIAL DATA
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

# TELEGRAM
def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "HTML"}
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print("Ошибка отправки в Telegram:", e)

# ROUTES
@app.route("/")
def index():
    products = Product.query.all()
    return render_template("index.html", products=products, active_page='main')

@app.route("/pizza")
def pizza():
    products = Product.query.filter_by(category="Pizza").all()
    return render_template("shop.html", products=products, category="Pizza", active_page='pizza')

@app.route("/sushi")
def sushi():
    products = Product.query.filter_by(category="Sushi").all()
    return render_template("shop.html", products=products, category="Sushi", active_page='sushi')

@app.route("/cart")
def cart():
    cart = session.get("cart", {})
    cart_items = []
    total = 0

    for product_id, quantity in cart.items():
        product = Product.query.get(int(product_id))
        if product:
            subtotal = product.price * quantity
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
    return redirect(request.referrer or url_for("index"))

@app.route('/about')
def about():
    return render_template("about.html")

@app.route('/checkout', methods=['POST'])
def checkout():
    cart = session.get('cart', {})
    if not cart:
        return redirect(url_for('cart'))

    phone = request.form.get('phone', '').strip()
    if not re.match(r'^\+\d{7,15}$', phone):
        return "Invalid phone number format. Use +31612345678.", 400

    order = Order(phone=phone, total=0)
    db.session.add(order)

    total = 0
    for product_id, quantity in cart.items():
        product = Product.query.get(int(product_id))
        if product:
            subtotal = product.price * quantity
            total += subtotal
            db.session.add(OrderItem(
                order=order,
                product_id=product.id,
                name=product.name,
                quantity=quantity,
                subtotal=subtotal
            ))

    order.total = total
    db.session.commit()

    # Telegram message
    msg_lines = [
        f"<b>New Order #{order.id}</b>",
        f"Phone: {order.phone}",
        "Items:"
    ]
    for item in order.items:
        msg_lines.append(f"{item.name} — Quantity: {item.quantity}, Subtotal: {item.subtotal} €")
    msg_lines.append(f"<b>Total: {order.total} €</b>")
    send_telegram_message("\n".join(msg_lines))

    session.pop('cart', None)
    return render_template('checkout_success.html', order=order)

@app.route('/orders')
def show_orders():
    orders = Order.query.order_by(Order.id.desc()).all()
    return render_template('orders.html', orders=orders)

@app.route("/init_products")
def init_products():
    if Product.query.first():
        return "Products already initialized."

    for p in products_pizza:
        db.session.add(Product(**p, category="Pizza"))
    for s in products_sushi:
        db.session.add(Product(**s, category="Sushi"))
    db.session.commit()
    return "Products added to DB"

@app.route("/clear_products")
def clear_products():
    Product.query.delete()
    db.session.commit()
    return "All products deleted."

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)