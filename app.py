from flask import Flask, render_template, request, redirect, url_for, session
import requests
from flask_sqlalchemy import SQLAlchemy
import os
import re
import logging
from datetime import datetime
from mollie.api.client import Client as MollieClient



basedir = os.path.abspath(os.path.dirname(__file__))


app = Flask(__name__)
app.secret_key = 'your_secret_key'

mollie = MollieClient()
mollie.set_api_key("test_kSPVxjsPkJvzeWdreg7G85Dwdjmv5h")  # ТЕСТОВИЙ API-ключ

log_dir = os.path.join(basedir, 'logs')
os.makedirs(log_dir, exist_ok=True)

logging.basicConfig(
    filename=os.path.join(log_dir, 'orders.log'),
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

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
products_sushi = [
    {"id": 1, "name": "Philadelphia", "description": "Salted salmon, cream cheese, rice, cucumber. Weight: 300g", "price": 12, "image": "1.png"},
    {"id": 2, "name": "Cheese Roll", "description": "Salted salmon, cream cheese, cheddar cheese, rice, cucumber, unagi sauce. Weight: 300g", "price": 12, "image": "2.png"},
    {"id": 3, "name": "Ebi Red", "description": "Tiger shrimp, cream cheese, rice, avocado, spicy sauce, masago roe. Weight: 300g", "price": 12, "image": "3.png"},
    {"id": 4, "name": "Futomaki Seafood Mix", "description": "Tiger shrimp, salted salmon, snow crab, rice, cucumber, spicy sauce. Weight: 300g", "price": 12, "image": "4.png"},
    {"id": 5, "name": "Tiger Roll", "description": "Tiger shrimp, salted salmon, cream cheese, rice, cucumber, avocado, unagi sauce. Weight: 300g", "price": 12, "image": "5.png"},
    {"id": 6, "name": "Samurai", "description": "Salted salmon, cream cheese, rice, cucumber, unagi sauce, sesame seeds. Weight: 300g", "price": 12, "image": "6.png"},
    {"id": 7, "name": "Sicario", "description": "Salted salmon, snow crab, cream cheese, rice, cucumber, spicy sauce, masago roe. Weight: 300g", "price": 12, "image": "7.png"},
    {"id": 8, "name": "Kappa Green", "description": "Salted salmon, snow crab, cream cheese, rice, cucumber, sesame seeds. Weight: 300g", "price": 12, "image": "8.png"},
    {"id": 9, "name": "California Syake in Sesame", "description": "Salted salmon, rice, cucumber, avocado, sesame seeds. Weight: 300g", "price": 12, "image": "9.png"},
    {"id": 10, "name": "Green Day", "description": "Salted salmon, snow crab, masago roe, rice, cucumber. Weight: 300g", "price": 12, "image": "10.png"},
    {"id": 11, "name": "California Ebi in Roe", "description": "Tiger shrimp, masago roe, avocado, rice, cucumber, spicy sauce. Weight: 300g", "price": 12, "image": "11.png"},
    {"id": 12, "name": "Philadelphia Combo", "description": "Tiger shrimp, salted salmon, cream cheese, rice, cucumber. Weight: 300g", "price": 12, "image": "12.png"},
    {"id": 13, "name": "Futomaki with Salmon", "description": "Salted salmon, cream cheese, masago roe, spicy sauce, rice, cucumber. Weight: 300g", "price": 12, "image": "13.png"},
    {"id": 14, "name": "Philadelphia with Eel", "description": "Eel, cream cheese, unagi sauce, rice, cucumber. Weight: 300g", "price": 12, "image": "14.png"},
    {"id": 15, "name": "Philadelphia with Shrimp", "description": "Tiger shrimp, cream cheese, rice, cucumber. Weight: 300g", "price": 12, "image": "15.png"},
    {"id": 16, "name": "Hurricane", "description": "Salted salmon, cream cheese, rice, avocado, unagi sauce. Weight: 300g", "price": 12, "image": "16.png"},
    {"id": 17, "name": "Light Life", "description": "Tuna, salted salmon, snow crab, cream cheese, rice, spicy sauce. Weight: 300g", "price": 12, "image": "17.png"},
    {"id": 18, "name": "Okayama", "description": "Tiger shrimp, cream cheese, rice, cucumber, white sesame, unagi sauce. Weight: 300g", "price": 12, "image": "18.png"},
    {"id": 19, "name": "Futomaki with Tuna", "description": "Tuna, cream cheese, rice, avocado, cucumber, spicy sauce. Weight: 300g", "price": 12, "image": "19.png"},
    {"id": 20, "name": "Kani Red", "description": "Snow crab, cream cheese, masago roe, rice, cucumber. Weight: 300g", "price": 12, "image": "20.png"},
    {"id": 21, "name": "Banzai", "description": "Salted salmon, masago roe, cream cheese, rice, cucumber, spicy sauce. Weight: 300g", "price": 12, "image": "21.png"}
]

products_sushi_set = [
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
        product = db.session.get(Product, int(product_id))
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
        product = db.session.get(Product, int(product_id))
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

    # Создаем платёж в Mollie
    payment = mollie.payments.create({
        "amount": {
            "currency": "EUR",
            "value": f"{order.total:.2f}"  # сумма должна быть строкой, формат 10.00
        },
        "description": f"Order #{order.id}",
        "redirectUrl": url_for("payment_success", order_id=order.id, _external=True),
        "webhookUrl": url_for("mollie_webhook", _external=True),
        "metadata": {
            "order_id": order.id,
            "phone": phone
        }
    })

    session.pop('cart', None)

    # Перенаправляем клиента на Mollie
    return redirect(payment.checkout_url)

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

    # Логирование заказа в файл
    log_lines = [
        f"Order #{order.id}",
        f"Phone: {order.phone}",
    ]
    for item in order.items:
        log_lines.append(f"{item.name} — Quantity: {item.quantity}, Subtotal: {item.subtotal} €")
    log_lines.append(f"Total: {order.total} €")
    log_lines.append("-" * 40)

    logging.info("\n" + "\n".join(log_lines))

    session.pop('cart', None)
    return render_template('checkout_success.html', order=order)

@app.route("/mollie_webhook", methods=["POST"])
def mollie_webhook():
    payment_id = request.form.get("id")
    payment = mollie.payments.get(payment_id)

    if payment.is_paid():
        order_id = payment.metadata["order_id"]
        order = Order.query.get(order_id)
        # Можно обновить статус в базе данных
        print(f"Оплата подтверждена для заказа #{order.id}")

    return "", 200

@app.route("/payment_success")
def payment_success():
    order_id = request.args.get("order_id")
    order = Order.query.get(order_id)
    return render_template("checkout_success.html", order=order)

@app.route('/orders')
def show_orders():
    orders = Order.query.order_by(Order.id.desc()).all()
    return render_template('orders.html', orders=orders)

@app.route("/init_products")
def init_products():
    if Product.query.first():
        return "Products already initialized."

    for p in products_sushi:
        db.session.add(Product(**p, category="Pizza"))
    for s in products_sushi_set:
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
        print(">>> Flask is starting...")
    app.run(debug=True, host="0.0.0.0", port=5000)