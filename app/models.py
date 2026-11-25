from datetime import datetime, timezone
from app.extensions import db


class Product(db.Model):
    """Menu item (Pizza, Sushi, or Sushi Set)."""

    __tablename__ = "product"

    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(140), unique=True, nullable=True, index=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=False, default="")
    price = db.Column(db.Float, nullable=False)
    image = db.Column(db.String(120), nullable=False, default="margherita.png")
    category = db.Column(db.String(50), nullable=False, index=True)  # Pizza, Sushi, SushiSet
    weight = db.Column(db.String(40), nullable=True, default="320g")
    badge = db.Column(db.String(40), nullable=True)  # e.g. "Chef's Pick", "Spicy", "Vegetarian"
    is_featured = db.Column(db.Boolean, default=False, nullable=False)

    def __repr__(self) -> str:
        return f"<Product {self.id}: {self.name}>"


class Order(db.Model):
    """Customer order."""

    __tablename__ = "order"

    id = db.Column(db.Integer, primary_key=True)
    phone = db.Column(db.String(20), nullable=False)
    customer_name = db.Column(db.String(120), nullable=True)
    delivery_city = db.Column(db.String(80), nullable=True)
    delivery_address = db.Column(db.String(240), nullable=True)
    total = db.Column(db.Float, nullable=False, default=0.0)
    is_paid = db.Column(db.Boolean, default=False, nullable=False)
    payment_id = db.Column(db.String(64), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    items = db.relationship("OrderItem", backref="order", lazy=True, cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Order #{self.id} total={self.total}>"


class OrderItem(db.Model):
    """Line item belonging to an Order."""

    __tablename__ = "order_item"

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("order.id"), nullable=False)
    product_id = db.Column(db.Integer, nullable=True)
    name = db.Column(db.String(120), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    subtotal = db.Column(db.Float, nullable=False, default=0.0)

    def __repr__(self) -> str:
        return f"<OrderItem {self.name} x{self.quantity}>"
