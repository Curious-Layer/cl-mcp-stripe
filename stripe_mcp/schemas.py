from typing import Any, Dict, List, Optional
from typing_extensions import TypedDict


# Customer Schemas
class CustomerAddress(TypedDict, total=False):
    """Customer address."""

    city: str
    country: str
    line1: str
    line2: str
    postal_code: str
    state: str


class CustomerShipping(TypedDict, total=False):
    """Customer shipping information."""

    address: CustomerAddress
    name: str
    phone: str


class Customer(TypedDict, total=False):
    """Customer object."""

    id: str
    object: str
    email: str
    name: str
    description: str
    metadata: Dict[str, str]
    address: Optional[CustomerAddress]
    shipping: Optional[CustomerShipping]
    balance: int
    created: int
    currency: str
    delinquent: bool


class CreateCustomerRequest(TypedDict, total=False):
    """Request to create a customer."""

    email: str
    name: str
    description: str
    metadata: Dict[str, str]
    address: CustomerAddress
    shipping: CustomerShipping
    payment_method: str


class UpdateCustomerRequest(TypedDict, total=False):
    """Request to update a customer."""

    email: str
    name: str
    description: str
    metadata: Dict[str, str]
    address: CustomerAddress
    shipping: CustomerShipping


# Charge Schemas
class Charge(TypedDict, total=False):
    """Charge object."""

    id: str
    object: str
    amount: int
    currency: str
    customer: str
    description: str
    status: str
    paid: bool
    refunded: bool
    metadata: Dict[str, str]
    created: int


class CreateChargeRequest(TypedDict, total=False):
    """Request to create a charge."""

    amount: int
    currency: str
    customer: str
    description: str
    metadata: Dict[str, str]
    source: str  # Payment method ID or token
    capture: bool


# Payment Intent Schemas
class PaymentIntent(TypedDict, total=False):
    """Payment Intent object."""

    id: str
    object: str
    amount: int
    currency: str
    customer: str
    status: str
    client_secret: str
    metadata: Dict[str, str]
    created: int


class CreatePaymentIntentRequest(TypedDict, total=False):
    """Request to create a payment intent."""

    amount: int
    currency: str
    customer: str
    description: str
    metadata: Dict[str, str]
    payment_method_types: List[str]
    confirm: bool


# Product Schemas
class Product(TypedDict, total=False):
    """Product object."""

    id: str
    object: str
    name: str
    description: str
    metadata: Dict[str, str]
    active: bool
    created: int


class CreateProductRequest(TypedDict, total=False):
    """Request to create a product."""

    name: str
    description: str
    metadata: Dict[str, str]
    active: bool


# Price Schemas
class Price(TypedDict, total=False):
    """Price object."""

    id: str
    object: str
    product: str
    unit_amount: int
    currency: str
    recurring: Optional[Dict[str, str]]
    metadata: Dict[str, str]
    active: bool
    created: int


class CreatePriceRequest(TypedDict, total=False):
    """Request to create a price."""

    product: str
    unit_amount: int
    currency: str
    recurring: Dict[str, str]  # {"interval": "month" or "year"}
    metadata: Dict[str, str]
    active: bool


# Subscription Schemas
class Subscription(TypedDict, total=False):
    """Subscription object."""

    id: str
    object: str
    customer: str
    status: str
    items: Dict[str, Any]
    metadata: Dict[str, str]
    current_period_start: int
    current_period_end: int
    cancel_at_period_end: bool
    created: int


class CreateSubscriptionRequest(TypedDict, total=False):
    """Request to create a subscription."""

    customer: str
    items: List[Dict[str, str]]  # [{"price": "price_123"}]
    metadata: Dict[str, str]
    trial_period_days: int
    cancel_at_period_end: bool


# Balance Schemas
class Balance(TypedDict, total=False):
    """Balance object."""

    available: List[Dict[str, Any]]
    pending: List[Dict[str, Any]]
    livemode: bool


# Pagination Schemas
class ListResponse(TypedDict):
    """List response from Stripe."""

    object: str
    data: List[Dict[str, Any]]
    has_more: bool
    url: str
