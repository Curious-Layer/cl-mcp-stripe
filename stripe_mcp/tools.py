import json
import logging

from fastmcp import FastMCP
from pydantic import Field

from .service import StripeClient

logger = logging.getLogger("stripe-mcp-server")


def register_tools(mcp: FastMCP) -> None:
    """Register all Stripe MCP tools."""

    # ========== Customer Tools ==========

    @mcp.tool(
        name="stripe_create_customer",
        description="Create a new customer in Stripe. Customers represent your users and can have payment methods, subscriptions, and invoices.",
    )
    async def stripe_create_customer(
        api_key: str = Field(..., description="Stripe API key (starts with sk_)"),
        email: str = Field(default=None, description="Customer's email address"),
        name: str = Field(default=None, description="Customer's full name"),
        description: str = Field(
            default=None, description="Description of the customer"
        ),
        metadata: str = Field(
            default="{}", description="JSON string of metadata key-value pairs"
        ),
    ) -> str:
        """Create a Stripe customer."""
        try:
            client = StripeClient(api_key)

            customer_data = {}
            if email:
                customer_data["email"] = email
            if name:
                customer_data["name"] = name
            if description:
                customer_data["description"] = description

            # Parse metadata
            try:
                metadata_dict = json.loads(metadata)
                if metadata_dict:
                    for key, value in metadata_dict.items():
                        customer_data[f"metadata[{key}]"] = value
            except json.JSONDecodeError as e:
                return json.dumps(
                    {"success": False, "error": f"Invalid metadata JSON: {str(e)}"}
                )

            result = await client.create_customer(customer_data)

            output = {
                "success": True,
                "customer_id": result.get("id"),
                "email": result.get("email"),
                "name": result.get("name"),
                "description": result.get("description"),
                "created": result.get("created"),
                "metadata": result.get("metadata"),
            }
            logger.info(f"Created customer: {output['customer_id']}")
            return json.dumps(output, indent=2)
        except Exception as e:
            logger.error(f"Failed to create customer: {e}", exc_info=True)
            return json.dumps({"success": False, "error": str(e)})

    @mcp.tool(
        name="stripe_get_customer",
        description="Retrieve a customer by ID. Returns all customer details including email, name, and metadata.",
    )
    async def stripe_get_customer(
        api_key: str = Field(..., description="Stripe API key"),
        customer_id: str = Field(..., description="Customer ID (e.g., 'cus_xxx')"),
    ) -> str:
        """Get a Stripe customer."""
        try:
            client = StripeClient(api_key)
            result = await client.get_customer(customer_id)

            output = {
                "success": True,
                "customer_id": result.get("id"),
                "email": result.get("email"),
                "name": result.get("name"),
                "description": result.get("description"),
                "balance": result.get("balance"),
                "created": result.get("created"),
                "delinquent": result.get("delinquent"),
                "metadata": result.get("metadata"),
            }
            logger.info(f"Retrieved customer: {customer_id}")
            return json.dumps(output, indent=2)
        except Exception as e:
            logger.error(f"Failed to get customer {customer_id}: {e}", exc_info=True)
            return json.dumps({"success": False, "error": str(e)})

    @mcp.tool(
        name="stripe_update_customer",
        description="Update an existing customer. Can update email, name, description, or metadata.",
    )
    async def stripe_update_customer(
        api_key: str = Field(..., description="Stripe API key"),
        customer_id: str = Field(..., description="Customer ID to update"),
        email: str = Field(default=None, description="New email address"),
        name: str = Field(default=None, description="New name"),
        description: str = Field(default=None, description="New description"),
        metadata: str = Field(
            default=None, description="JSON string of metadata to merge"
        ),
    ) -> str:
        """Update a Stripe customer."""
        try:
            client = StripeClient(api_key)

            update_data = {}
            if email:
                update_data["email"] = email
            if name:
                update_data["name"] = name
            if description:
                update_data["description"] = description

            if metadata:
                try:
                    metadata_dict = json.loads(metadata)
                    for key, value in metadata_dict.items():
                        update_data[f"metadata[{key}]"] = value
                except json.JSONDecodeError as e:
                    return json.dumps(
                        {"success": False, "error": f"Invalid metadata JSON: {str(e)}"}
                    )

            result = await client.update_customer(customer_id, update_data)

            output = {
                "success": True,
                "customer_id": result.get("id"),
                "email": result.get("email"),
                "name": result.get("name"),
                "metadata": result.get("metadata"),
            }
            logger.info(f"Updated customer: {customer_id}")
            return json.dumps(output, indent=2)
        except Exception as e:
            logger.error(f"Failed to update customer {customer_id}: {e}", exc_info=True)
            return json.dumps({"success": False, "error": str(e)})

    @mcp.tool(
        name="stripe_list_customers",
        description="List all customers with pagination. Returns up to 100 customers per page.",
    )
    async def stripe_list_customers(
        api_key: str = Field(..., description="Stripe API key"),
        limit: int = Field(
            default=10,
            description="Number of customers to return (1-100)",
            ge=1,
            le=100,
        ),
        starting_after: str = Field(
            default=None, description="Customer ID to start after for pagination"
        ),
    ) -> str:
        """List Stripe customers."""
        try:
            client = StripeClient(api_key)
            result = await client.list_customers(
                limit=limit, starting_after=starting_after
            )

            customers = []
            for c in result.get("data", []):
                customers.append(
                    {
                        "id": c.get("id"),
                        "email": c.get("email"),
                        "name": c.get("name"),
                        "created": c.get("created"),
                    }
                )

            output = {
                "success": True,
                "has_more": result.get("has_more", False),
                "count": len(customers),
                "customers": customers,
            }
            logger.info(f"Listed {output['count']} customers")
            return json.dumps(output, indent=2)
        except Exception as e:
            logger.error(f"Failed to list customers: {e}", exc_info=True)
            return json.dumps({"success": False, "error": str(e)})

    @mcp.tool(
        name="stripe_search_customers",
        description="Search customers using Stripe's search query language. Useful for finding customers by email or name.",
    )
    async def stripe_search_customers(
        api_key: str = Field(..., description="Stripe API key"),
        query: str = Field(
            ...,
            description="Search query (e.g., 'email:\"user@example.com\"' or 'name:\"John\"')",
        ),
        limit: int = Field(
            default=10, description="Number of results to return (1-100)", ge=1, le=100
        ),
    ) -> str:
        """Search Stripe customers."""
        try:
            client = StripeClient(api_key)
            result = await client.search_customers(query, limit=limit)

            customers = []
            for c in result.get("data", []):
                customers.append(
                    {
                        "id": c.get("id"),
                        "email": c.get("email"),
                        "name": c.get("name"),
                        "created": c.get("created"),
                    }
                )

            output = {
                "success": True,
                "has_more": result.get("has_more", False),
                "count": len(customers),
                "customers": customers,
            }
            logger.info(f"Searched customers, found {output['count']} results")
            return json.dumps(output, indent=2)
        except Exception as e:
            logger.error(f"Failed to search customers: {e}", exc_info=True)
            return json.dumps({"success": False, "error": str(e)})

    @mcp.tool(
        name="stripe_delete_customer",
        description="Delete a customer. This will also delete any active subscriptions.",
    )
    async def stripe_delete_customer(
        api_key: str = Field(..., description="Stripe API key"),
        customer_id: str = Field(..., description="Customer ID to delete"),
    ) -> str:
        """Delete a Stripe customer."""
        try:
            client = StripeClient(api_key)
            result = await client.delete_customer(customer_id)

            output = {
                "success": True,
                "customer_id": customer_id,
                "deleted": result.get("deleted", True),
            }
            logger.info(f"Deleted customer: {customer_id}")
            return json.dumps(output, indent=2)
        except Exception as e:
            logger.error(f"Failed to delete customer {customer_id}: {e}", exc_info=True)
            return json.dumps({"success": False, "error": str(e)})

    # ========== Charge Tools ==========

    @mcp.tool(
        name="stripe_create_charge",
        description="Create a new charge (payment). Charges money directly from a customer's payment method.",
    )
    async def stripe_create_charge(
        api_key: str = Field(..., description="Stripe API key"),
        amount: int = Field(..., description="Amount in cents (e.g., $10.00 = 1000)"),
        currency: str = Field(
            default="usd", description="Currency code (usd, eur, gbp, etc.)"
        ),
        customer_id: str = Field(default=None, description="Customer ID to charge"),
        description: str = Field(default=None, description="Description of the charge"),
        metadata: str = Field(default="{}", description="JSON string of metadata"),
    ) -> str:
        """Create a Stripe charge."""
        try:
            client = StripeClient(api_key)

            charge_data = {
                "amount": amount,
                "currency": currency,
            }

            if customer_id:
                charge_data["customer"] = customer_id
            if description:
                charge_data["description"] = description

            # Parse metadata
            try:
                metadata_dict = json.loads(metadata)
                for key, value in metadata_dict.items():
                    charge_data[f"metadata[{key}]"] = value
            except json.JSONDecodeError as e:
                return json.dumps(
                    {"success": False, "error": f"Invalid metadata JSON: {str(e)}"}
                )

            result = await client.create_charge(charge_data)

            output = {
                "success": True,
                "charge_id": result.get("id"),
                "amount": result.get("amount"),
                "currency": result.get("currency"),
                "status": result.get("status"),
                "paid": result.get("paid"),
                "customer": result.get("customer"),
                "description": result.get("description"),
            }
            logger.info(f"Created charge: {output['charge_id']}")
            return json.dumps(output, indent=2)
        except Exception as e:
            logger.error(f"Failed to create charge: {e}", exc_info=True)
            return json.dumps({"success": False, "error": str(e)})

    @mcp.tool(
        name="stripe_get_charge",
        description="Retrieve a charge by ID. Returns charge details including status and payment information.",
    )
    async def stripe_get_charge(
        api_key: str = Field(..., description="Stripe API key"),
        charge_id: str = Field(..., description="Charge ID (e.g., 'ch_xxx')"),
    ) -> str:
        """Get a Stripe charge."""
        try:
            client = StripeClient(api_key)
            result = await client.get_charge(charge_id)

            output = {
                "success": True,
                "charge_id": result.get("id"),
                "amount": result.get("amount"),
                "currency": result.get("currency"),
                "status": result.get("status"),
                "paid": result.get("paid"),
                "refunded": result.get("refunded"),
                "customer": result.get("customer"),
                "description": result.get("description"),
                "created": result.get("created"),
            }
            logger.info(f"Retrieved charge: {charge_id}")
            return json.dumps(output, indent=2)
        except Exception as e:
            logger.error(f"Failed to get charge {charge_id}: {e}", exc_info=True)
            return json.dumps({"success": False, "error": str(e)})

    # ========== Payment Intent Tools ==========

    @mcp.tool(
        name="stripe_create_payment_intent",
        description="Create a payment intent for collecting payments. Returns a client secret for frontend confirmation.",
    )
    async def stripe_create_payment_intent(
        api_key: str = Field(..., description="Stripe API key"),
        amount: int = Field(..., description="Amount in cents"),
        currency: str = Field(default="usd", description="Currency code"),
        customer_id: str = Field(default=None, description="Customer ID"),
        description: str = Field(default=None, description="Description"),
        metadata: str = Field(default="{}", description="JSON string of metadata"),
        confirm: bool = Field(
            default=False, description="Confirm the payment intent immediately"
        ),
    ) -> str:
        """Create a Stripe payment intent."""
        try:
            client = StripeClient(api_key)

            intent_data = {
                "amount": amount,
                "currency": currency,
            }

            if customer_id:
                intent_data["customer"] = customer_id
            if description:
                intent_data["description"] = description
            if confirm:
                intent_data["confirm"] = True

            # Parse metadata
            try:
                metadata_dict = json.loads(metadata)
                for key, value in metadata_dict.items():
                    intent_data[f"metadata[{key}]"] = value
            except json.JSONDecodeError as e:
                return json.dumps(
                    {"success": False, "error": f"Invalid metadata JSON: {str(e)}"}
                )

            result = await client.create_payment_intent(intent_data)

            output = {
                "success": True,
                "payment_intent_id": result.get("id"),
                "client_secret": result.get("client_secret"),
                "amount": result.get("amount"),
                "currency": result.get("currency"),
                "status": result.get("status"),
                "customer": result.get("customer"),
            }
            logger.info(f"Created payment intent: {output['payment_intent_id']}")
            return json.dumps(output, indent=2)
        except Exception as e:
            logger.error(f"Failed to create payment intent: {e}", exc_info=True)
            return json.dumps({"success": False, "error": str(e)})

    @mcp.tool(
        name="stripe_confirm_payment_intent",
        description="Confirm a payment intent. Use this after collecting payment details on the client side.",
    )
    async def stripe_confirm_payment_intent(
        api_key: str = Field(..., description="Stripe API key"),
        payment_intent_id: str = Field(..., description="Payment Intent ID to confirm"),
    ) -> str:
        """Confirm a Stripe payment intent."""
        try:
            client = StripeClient(api_key)
            result = await client.confirm_payment_intent(payment_intent_id)

            output = {
                "success": True,
                "payment_intent_id": result.get("id"),
                "status": result.get("status"),
            }
            logger.info(f"Confirmed payment intent: {payment_intent_id}")
            return json.dumps(output, indent=2)
        except Exception as e:
            logger.error(
                f"Failed to confirm payment intent {payment_intent_id}: {e}",
                exc_info=True,
            )
            return json.dumps({"success": False, "error": str(e)})

    # ========== Product & Price Tools ==========

    @mcp.tool(
        name="stripe_create_product",
        description="Create a product. Products are goods or services you sell, with associated prices.",
    )
    async def stripe_create_product(
        api_key: str = Field(..., description="Stripe API key"),
        name: str = Field(..., description="Product name"),
        description: str = Field(default=None, description="Product description"),
        metadata: str = Field(default="{}", description="JSON string of metadata"),
    ) -> str:
        """Create a Stripe product."""
        try:
            client = StripeClient(api_key)

            product_data = {"name": name}
            if description:
                product_data["description"] = description

            try:
                metadata_dict = json.loads(metadata)
                for key, value in metadata_dict.items():
                    product_data[f"metadata[{key}]"] = value
            except json.JSONDecodeError as e:
                return json.dumps(
                    {"success": False, "error": f"Invalid metadata JSON: {str(e)}"}
                )

            result = await client.create_product(product_data)

            output = {
                "success": True,
                "product_id": result.get("id"),
                "name": result.get("name"),
                "description": result.get("description"),
                "active": result.get("active"),
            }
            logger.info(f"Created product: {output['product_id']}")
            return json.dumps(output, indent=2)
        except Exception as e:
            logger.error(f"Failed to create product: {e}", exc_info=True)
            return json.dumps({"success": False, "error": str(e)})

    @mcp.tool(
        name="stripe_create_price",
        description="Create a price for a product. Prices define the amount and currency for subscriptions or one-time payments.",
    )
    async def stripe_create_price(
        api_key: str = Field(..., description="Stripe API key"),
        product_id: str = Field(
            ..., description="Product ID to associate with this price"
        ),
        unit_amount: int = Field(..., description="Amount in cents"),
        currency: str = Field(default="usd", description="Currency code"),
        recurring_interval: str = Field(
            default=None, description="Subscription interval: 'month' or 'year'"
        ),
    ) -> str:
        """Create a Stripe price."""
        try:
            client = StripeClient(api_key)

            price_data = {
                "product": product_id,
                "unit_amount": unit_amount,
                "currency": currency,
            }

            if recurring_interval:
                price_data["recurring[interval]"] = recurring_interval

            result = await client.create_price(price_data)

            output = {
                "success": True,
                "price_id": result.get("id"),
                "product": result.get("product"),
                "unit_amount": result.get("unit_amount"),
                "currency": result.get("currency"),
                "recurring": result.get("recurring"),
            }
            logger.info(f"Created price: {output['price_id']}")
            return json.dumps(output, indent=2)
        except Exception as e:
            logger.error(f"Failed to create price: {e}", exc_info=True)
            return json.dumps({"success": False, "error": str(e)})

    # ========== Subscription Tools ==========

    @mcp.tool(
        name="stripe_create_subscription",
        description="Create a subscription for a customer. Requires a price ID and customer ID.",
    )
    async def stripe_create_subscription(
        api_key: str = Field(..., description="Stripe API key"),
        customer_id: str = Field(..., description="Customer ID"),
        price_id: str = Field(..., description="Price ID for the subscription"),
        trial_period_days: int = Field(
            default=None, description="Trial period in days"
        ),
        metadata: str = Field(default="{}", description="JSON string of metadata"),
    ) -> str:
        """Create a Stripe subscription."""
        try:
            client = StripeClient(api_key)

            subscription_data = {
                "customer": customer_id,
                "items[0][price]": price_id,
            }

            if trial_period_days:
                subscription_data["trial_period_days"] = trial_period_days

            try:
                metadata_dict = json.loads(metadata)
                for key, value in metadata_dict.items():
                    subscription_data[f"metadata[{key}]"] = value
            except json.JSONDecodeError as e:
                return json.dumps(
                    {"success": False, "error": f"Invalid metadata JSON: {str(e)}"}
                )

            result = await client.create_subscription(subscription_data)

            output = {
                "success": True,
                "subscription_id": result.get("id"),
                "customer": result.get("customer"),
                "status": result.get("status"),
                "current_period_start": result.get("current_period_start"),
                "current_period_end": result.get("current_period_end"),
            }
            logger.info(f"Created subscription: {output['subscription_id']}")
            return json.dumps(output, indent=2)
        except Exception as e:
            logger.error(f"Failed to create subscription: {e}", exc_info=True)
            return json.dumps({"success": False, "error": str(e)})

    @mcp.tool(
        name="stripe_cancel_subscription",
        description="Cancel a customer's subscription. Can cancel immediately or at period end.",
    )
    async def stripe_cancel_subscription(
        api_key: str = Field(..., description="Stripe API key"),
        subscription_id: str = Field(..., description="Subscription ID to cancel"),
        cancel_at_period_end: bool = Field(
            default=True,
            description="Cancel at period end (true) or immediately (false)",
        ),
    ) -> str:
        """Cancel a Stripe subscription."""
        try:
            client = StripeClient(api_key)
            result = await client.cancel_subscription(
                subscription_id, cancel_at_period_end
            )

            output = {
                "success": True,
                "subscription_id": result.get("id"),
                "status": result.get("status"),
                "cancel_at_period_end": result.get("cancel_at_period_end"),
            }
            logger.info(f"Cancelled subscription: {subscription_id}")
            return json.dumps(output, indent=2)
        except Exception as e:
            logger.error(
                f"Failed to cancel subscription {subscription_id}: {e}", exc_info=True
            )
            return json.dumps({"success": False, "error": str(e)})

    # ========== Balance Tools ==========

    @mcp.tool(
        name="stripe_get_balance",
        description="Get account balance. Returns available and pending balances by currency.",
    )
    async def stripe_get_balance(
        api_key: str = Field(..., description="Stripe API key"),
    ) -> str:
        """Get Stripe account balance."""
        try:
            client = StripeClient(api_key)
            result = await client.get_balance()

            output = {
                "success": True,
                "available": result.get("available", []),
                "pending": result.get("pending", []),
                "livemode": result.get("livemode"),
            }
            logger.info("Retrieved account balance")
            return json.dumps(output, indent=2)
        except Exception as e:
            logger.error(f"Failed to get balance: {e}", exc_info=True)
            return json.dumps({"success": False, "error": str(e)})

    # ========== Utility Tools ==========

    @mcp.tool(
        name="stripe_health_check",
        description="Check server readiness and basic connectivity.",
    )
    def stripe_health_check() -> str:
        """Health check endpoint."""
        return json.dumps(
            {
                "status": "ok",
                "server": "CL Stripe MCP Server",
                "type": "third-party integration",
                "auth_required": "for all endpoints",
            }
        )
