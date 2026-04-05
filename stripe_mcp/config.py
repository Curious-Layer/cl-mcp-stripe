import logging
import os

# Stripe API Configuration
STRIPE_API_BASE = "https://api.stripe.com"
STRIPE_API_VERSION = "v1"

# API Endpoints
ENDPOINTS = {
    # Customers
    "customers": "/v1/customers",
    "customer": "/v1/customers/{customer_id}",
    "search_customers": "/v1/customers/search",
    # Charges
    "charges": "/v1/charges",
    "charge": "/v1/charges/{charge_id}",
    # Payment Intents
    "payment_intents": "/v1/payment_intents",
    "payment_intent": "/v1/payment_intents/{payment_intent_id}",
    # Refunds
    "refunds": "/v1/refunds",
    "refund": "/v1/refunds/{refund_id}",
    # Products
    "products": "/v1/products",
    "product": "/v1/products/{product_id}",
    # Prices
    "prices": "/v1/prices",
    "price": "/v1/prices/{price_id}",
    # Subscriptions
    "subscriptions": "/v1/subscriptions",
    "subscription": "/v1/subscriptions/{subscription_id}",
    "cancel_subscription": "/v1/subscriptions/{subscription_id}",
    # Balance
    "balance": "/v1/balance",
}

# Defaults
DEFAULT_LIMIT = 10
MAX_LIMIT = 100
DEFAULT_TIMEOUT = 30


def configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler()],
    )
