import logging
from flask import current_app, url_for
from mollie.api.client import Client as MollieClient

logger = logging.getLogger(__name__)


def create_mollie_payment(order, phone: str) -> str | None:
    """Create a Mollie payment and return checkout URL, or None if in local/demo mode."""
    api_key = current_app.config.get("MOLLIE_API_KEY", "").strip()
    if not api_key:
        logger.info("MOLLIE_API_KEY not configured; using local confirmation flow for order #%s", order.id)
        return None

    client = MollieClient()
    client.set_api_key(api_key)

    payment = client.payments.create(
        {
            "amount": {
                "currency": current_app.config.get("CURRENCY", "EUR"),
                "value": f"{order.total:.2f}",
            },
            "description": f"NidePizza Order #{order.id}",
            "redirectUrl": url_for("main.payment_success", order_id=order.id, _external=True),
            "webhookUrl": url_for("main.mollie_webhook", _external=True),
            "metadata": {
                "order_id": order.id,
                "phone": phone,
            },
        }
    )
    return payment.checkout_url


def fetch_mollie_payment(payment_id: str):
    """Fetch payment status from Mollie API."""
    api_key = current_app.config.get("MOLLIE_API_KEY", "").strip()
    if not api_key:
        return None
    client = MollieClient()
    client.set_api_key(api_key)
    return client.payments.get(payment_id)
