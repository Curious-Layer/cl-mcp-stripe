import json
import logging
from typing import Any, Dict, List, Optional

import httpx

from .config import STRIPE_API_BASE, DEFAULT_TIMEOUT, ENDPOINTS

logger = logging.getLogger("stripe-mcp-server")


class StripeClient:
    """Client for Stripe API."""

    def __init__(self, api_key: str):
        """Initialize Stripe API client.

        Args:
            api_key: Stripe API key (starts with sk_)
        """
        self.api_key = api_key
        self.base_url = STRIPE_API_BASE

    def _build_headers(self) -> Dict[str, str]:
        """Build request headers with Basic Auth."""
        # Stripe uses HTTP Basic Auth with API key as username
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/x-www-form-urlencoded",
        }

    async def _request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """Make HTTP request to Stripe API."""
        url = f"{self.base_url}{endpoint}"
        headers = self._build_headers()

        async with httpx.AsyncClient() as client:
            try:
                response = await client.request(
                    method=method,
                    url=url,
                    headers=headers,
                    data=data,  # Stripe uses form-encoded data
                    params=params,
                    timeout=DEFAULT_TIMEOUT,
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                error_body = e.response.text
                logger.error(
                    f"Stripe API error: {e.response.status_code} - {error_body}"
                )

                # Parse Stripe error response
                try:
                    error_data = e.response.json()
                    error_msg = error_data.get("error", {}).get("message", str(e))
                except:
                    error_msg = error_body

                raise Exception(f"Stripe API error: {error_msg}")

    # ========== Customer Management ==========

    async def create_customer(self, customer_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new customer."""
        return await self._request("POST", ENDPOINTS["customers"], data=customer_data)

    async def get_customer(self, customer_id: str) -> Dict[str, Any]:
        """Get a customer by ID."""
        endpoint = ENDPOINTS["customer"].format(customer_id=customer_id)
        return await self._request("GET", endpoint)

    async def update_customer(
        self, customer_id: str, update_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update a customer."""
        endpoint = ENDPOINTS["customer"].format(customer_id=customer_id)
        return await self._request("POST", endpoint, data=update_data)

    async def list_customers(
        self, limit: int = 10, starting_after: Optional[str] = None
    ) -> Dict[str, Any]:
        """List customers."""
        params = {"limit": limit}
        if starting_after:
            params["starting_after"] = starting_after
        return await self._request("GET", ENDPOINTS["customers"], params=params)

    async def search_customers(self, query: str, limit: int = 10) -> Dict[str, Any]:
        """Search customers."""
        params = {"query": query, "limit": limit}
        return await self._request("GET", ENDPOINTS["search_customers"], params=params)

    async def delete_customer(self, customer_id: str) -> Dict[str, Any]:
        """Delete a customer."""
        endpoint = ENDPOINTS["customer"].format(customer_id=customer_id)
        return await self._request("DELETE", endpoint)

    # ========== Charge Management ==========

    async def create_charge(self, charge_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new charge."""
        return await self._request("POST", ENDPOINTS["charges"], data=charge_data)

    async def get_charge(self, charge_id: str) -> Dict[str, Any]:
        """Get a charge by ID."""
        endpoint = ENDPOINTS["charge"].format(charge_id=charge_id)
        return await self._request("GET", endpoint)

    async def list_charges(
        self, limit: int = 10, customer: Optional[str] = None
    ) -> Dict[str, Any]:
        """List charges."""
        params = {"limit": limit}
        if customer:
            params["customer"] = customer
        return await self._request("GET", ENDPOINTS["charges"], params=params)

    # ========== Payment Intent Management ==========

    async def create_payment_intent(
        self, intent_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create a payment intent."""
        return await self._request(
            "POST", ENDPOINTS["payment_intents"], data=intent_data
        )

    async def get_payment_intent(self, intent_id: str) -> Dict[str, Any]:
        """Get a payment intent by ID."""
        endpoint = ENDPOINTS["payment_intent"].format(payment_intent_id=intent_id)
        return await self._request("GET", endpoint)

    async def update_payment_intent(
        self, intent_id: str, update_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update a payment intent."""
        endpoint = ENDPOINTS["payment_intent"].format(payment_intent_id=intent_id)
        return await self._request("POST", endpoint, data=update_data)

    async def confirm_payment_intent(self, intent_id: str) -> Dict[str, Any]:
        """Confirm a payment intent."""
        endpoint = ENDPOINTS["payment_intent"].format(payment_intent_id=intent_id)
        return await self._request("POST", f"{endpoint}/confirm")

    # ========== Refund Management ==========

    async def create_refund(
        self, charge_id: str, amount: Optional[int] = None
    ) -> Dict[str, Any]:
        """Create a refund for a charge."""
        data = {"charge": charge_id}
        if amount:
            data["amount"] = amount
        return await self._request("POST", ENDPOINTS["refunds"], data=data)

    async def get_refund(self, refund_id: str) -> Dict[str, Any]:
        """Get a refund by ID."""
        endpoint = ENDPOINTS["refund"].format(refund_id=refund_id)
        return await self._request("GET", endpoint)

    # ========== Product Management ==========

    async def create_product(self, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a product."""
        return await self._request("POST", ENDPOINTS["products"], data=product_data)

    async def get_product(self, product_id: str) -> Dict[str, Any]:
        """Get a product by ID."""
        endpoint = ENDPOINTS["product"].format(product_id=product_id)
        return await self._request("GET", endpoint)

    async def list_products(
        self, limit: int = 10, active: Optional[bool] = None
    ) -> Dict[str, Any]:
        """List products."""
        params = {"limit": limit}
        if active is not None:
            params["active"] = active
        return await self._request("GET", ENDPOINTS["products"], params=params)

    # ========== Price Management ==========

    async def create_price(self, price_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a price."""
        return await self._request("POST", ENDPOINTS["prices"], data=price_data)

    async def get_price(self, price_id: str) -> Dict[str, Any]:
        """Get a price by ID."""
        endpoint = ENDPOINTS["price"].format(price_id=price_id)
        return await self._request("GET", endpoint)

    async def list_prices(
        self, limit: int = 10, product: Optional[str] = None
    ) -> Dict[str, Any]:
        """List prices."""
        params = {"limit": limit}
        if product:
            params["product"] = product
        return await self._request("GET", ENDPOINTS["prices"], params=params)

    # ========== Subscription Management ==========

    async def create_subscription(
        self, subscription_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create a subscription."""
        return await self._request(
            "POST", ENDPOINTS["subscriptions"], data=subscription_data
        )

    async def get_subscription(self, subscription_id: str) -> Dict[str, Any]:
        """Get a subscription by ID."""
        endpoint = ENDPOINTS["subscription"].format(subscription_id=subscription_id)
        return await self._request("GET", endpoint)

    async def update_subscription(
        self, subscription_id: str, update_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update a subscription."""
        endpoint = ENDPOINTS["subscription"].format(subscription_id=subscription_id)
        return await self._request("POST", endpoint, data=update_data)

    async def cancel_subscription(
        self, subscription_id: str, cancel_at_period_end: bool = True
    ) -> Dict[str, Any]:
        """Cancel a subscription."""
        endpoint = ENDPOINTS["cancel_subscription"].format(
            subscription_id=subscription_id
        )
        data = {"cancel_at_period_end": cancel_at_period_end}
        return await self._request("DELETE", endpoint, data=data)

    async def list_subscriptions(
        self, limit: int = 10, customer: Optional[str] = None
    ) -> Dict[str, Any]:
        """List subscriptions."""
        params = {"limit": limit}
        if customer:
            params["customer"] = customer
        return await self._request("GET", ENDPOINTS["subscriptions"], params=params)

    # ========== Balance ==========

    async def get_balance(self) -> Dict[str, Any]:
        """Get account balance."""
        return await self._request("GET", ENDPOINTS["balance"])
