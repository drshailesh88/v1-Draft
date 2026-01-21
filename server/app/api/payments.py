import os
import httpx
from fastapi import APIRouter, HTTPException, Depends, Header, Request
from pydantic import BaseModel
from typing import Optional, Literal
from core.database import supabase, get_user_from_token

router = APIRouter()


PADDLE_API_KEY = os.getenv("PADDLE_API_KEY")
PADDLE_CLIENT_ID = os.getenv("PADDLE_CLIENT_ID")
PADDLE_CLIENT_SECRET = os.getenv("PADDLE_CLIENT_SECRET")
RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID")
RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET")

SUBSCRIPTION_TIERS = {
    "free": {"price": 0, "usd": 0, "eur": 0, "gbp": 0, "inr": 0},
    "pro": {"price": 19, "usd": 19, "eur": 17, "gbp": 15, "inr": 1599},
    "team": {"price": 49, "usd": 49, "eur": 44, "gbp": 39, "inr": 4099},
}


class CreateCheckoutRequest(BaseModel):
    tier: Literal["free", "pro", "team"]
    currency: Literal["USD", "EUR", "GBP", "INR"]
    payment_method: Optional[Literal["auto", "paddle", "razorpay"]] = "auto"


class CreateCheckoutResponse(BaseModel):
    checkout_url: str
    payment_id: str
    payment_provider: str


class SubscriptionResponse(BaseModel):
    tier: str
    status: str
    payment_method: str
    currency: str
    amount: float
    started_at: str
    ends_at: Optional[str]


async def detect_currency_from_ip(client_ip: str) -> str:
    """Detect currency based on IP address"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"http://ip-api.com/json/{client_ip}")
            data = response.json()
            country_code = data.get("countryCode", "")

            if country_code == "IN":
                return "INR"
            elif country_code in ["GB"]:
                return "GBP"
            elif country_code in ["DE", "FR", "IT", "ES", "NL"]:
                return "EUR"
            else:
                return "USD"
    except Exception as e:
        print(f"Error detecting currency: {e}")
        return "USD"


def determine_payment_method(currency: str, preferred_method: str) -> str:
    """Determine payment method based on currency and user preference"""
    if preferred_method != "auto":
        return preferred_method

    if currency == "INR":
        return "razorpay"
    else:
        return "paddle"


async def create_paddle_checkout(
    user_id: str, tier: str, currency: str, success_url: str, cancel_url: str
) -> tuple[str, str]:
    """Create Paddle checkout session"""
    try:
        price = SUBSCRIPTION_TIERS[tier.lower()][currency.lower()]

        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.paddle.com/checkout-sessions",
                headers={
                    "Authorization": f"Bearer {PADDLE_API_KEY}",
                },
                json={
                    "items": [
                        {
                            "price_id": f"pri_{tier}_{currency.lower()}",
                            "quantity": 1,
                        }
                    ],
                    "custom_data": {"user_id": user_id, "tier": tier},
                    "success_url": success_url,
                    "cancel_url": cancel_url,
                    "customer_email": "",
                },
            )
            response.raise_for_status()
            data = response.json()
            return data["data"]["url"], data["data"]["id"]
    except Exception as e:
        print(f"Paddle checkout error: {e}")
        raise HTTPException(status_code=500, detail="Failed to create Paddle checkout")


async def create_razorpay_order(
    user_id: str, tier: str, currency: str
) -> tuple[str, str]:
    """Create Razorpay order"""
    try:
        price = SUBSCRIPTION_TIERS[tier.lower()][currency.lower()]
        amount_in_paise = int(price * 100)

        auth = f"{RAZORPAY_KEY_ID}:{RAZORPAY_KEY_SECRET}"
        encoded_auth = auth.encode("utf-8").decode("utf-8")

        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.razorpay.com/v1/orders",
                headers={
                    "Authorization": f"Basic {encoded_auth}",
                    "Content-Type": "application/json",
                },
                json={
                    "amount": amount_in_paise,
                    "currency": currency,
                    "notes": {"user_id": user_id, "tier": tier},
                },
            )
            response.raise_for_status()
            data = response.json()
            checkout_url = f"https://checkout.razorpay.com/v1/checkout?key={RAZORPAY_KEY_ID}&order_id={data['id']}"
            return checkout_url, data["id"]
    except Exception as e:
        print(f"Razorpay order error: {e}")
        raise HTTPException(status_code=500, detail="Failed to create Razorpay order")


@router.post("/create-checkout", response_model=CreateCheckoutResponse)
async def create_checkout(
    request: CreateCheckoutRequest,
    token: Optional[str] = Header(None, alias="Authorization"),
    client_ip: Optional[str] = Header(None, alias="X-Forwarded-For"),
):
    """Create checkout session for subscription"""
    user = await get_user_from_token(token.replace("Bearer ", "") if token else None)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    if request.tier == "free":
        await create_free_subscription(user["id"])
        return CreateCheckoutResponse(
            checkout_url="", payment_id="free", payment_provider="none"
        )

    currency = request.currency

    payment_method = determine_payment_method(currency, request.payment_method)

    user_id = user["id"]

    if payment_method == "paddle":
        success_url = f"{os.getenv('FRONTEND_URL', 'http://localhost:3000')}/subscription?success=true"
        cancel_url = f"{os.getenv('FRONTEND_URL', 'http://localhost:3000')}/subscription?cancel=true"

        checkout_url, payment_id = await create_paddle_checkout(
            user_id, request.tier, currency, success_url, cancel_url
        )
        return CreateCheckoutResponse(
            checkout_url=checkout_url, payment_id=payment_id, payment_provider="paddle"
        )
    else:
        checkout_url, payment_id = await create_razorpay_order(
            user_id, request.tier, currency
        )
        return CreateCheckoutResponse(
            checkout_url=checkout_url,
            payment_id=payment_id,
            payment_provider="razorpay",
        )


async def create_free_subscription(user_id: str):
    """Create free subscription"""
    try:
        subscription_data = {
            "user_id": user_id,
            "tier": "free",
            "payment_method": "none",
            "currency": "USD",
            "amount": 0,
            "status": "active",
            "started_at": "NOW()",
        }
        supabase.table("subscriptions").insert(subscription_data).execute()

        await update_user_tier(user_id, "free")
    except Exception as e:
        print(f"Error creating free subscription: {e}")


async def update_user_tier(user_id: str, tier: str):
    """Update user's subscription tier"""
    try:
        supabase.table("users").update({"subscription_tier": tier}).eq(
            "id", user_id
        ).execute()
    except Exception as e:
        print(f"Error updating user tier: {e}")


@router.post("/webhook/paddle")
async def paddle_webhook(request: Request):
    """Handle Paddle webhook events"""
    try:
        webhook_data = await request.json()
        event_type = webhook_data.get("event_type")

        if event_type == "subscription.created":
            await handle_paddle_subscription_created(webhook_data)
        elif event_type == "subscription.cancelled":
            await handle_paddle_subscription_cancelled(webhook_data)
        elif event_type == "transaction.completed":
            await handle_paddle_payment_completed(webhook_data)

        return {"status": "success"}
    except Exception as e:
        print(f"Paddle webhook error: {e}")
        raise HTTPException(status_code=500, detail="Webhook processing failed")


async def handle_paddle_subscription_created(webhook_data: dict):
    """Handle Paddle subscription created event"""
    try:
        subscription = webhook_data.get("data", {})
        custom_data = subscription.get("custom_data", {})
        user_id = custom_data.get("user_id")
        tier = custom_data.get("tier")

        subscription_data = {
            "user_id": user_id,
            "tier": tier,
            "payment_method": "paddle",
            "currency": subscription.get("currency", "USD"),
            "amount": subscription.get("total_amount", 0),
            "status": "active",
            "paddle_customer_id": subscription.get("customer_id"),
            "paddle_subscription_id": subscription.get("id"),
            "started_at": subscription.get("created_at"),
            "ends_at": subscription.get("next_billed_at"),
        }

        supabase.table("subscriptions").insert(subscription_data).execute()
        await update_user_tier(user_id, tier)
    except Exception as e:
        print(f"Error handling Paddle subscription created: {e}")


async def handle_paddle_subscription_cancelled(webhook_data: dict):
    """Handle Paddle subscription cancelled event"""
    try:
        subscription = webhook_data.get("data", {})
        paddle_subscription_id = subscription.get("id")

        supabase.table("subscriptions").update({"status": "cancelled"}).eq(
            "paddle_subscription_id", paddle_subscription_id
        ).execute()

        response = (
            supabase.table("subscriptions")
            .select("user_id")
            .eq("paddle_subscription_id", paddle_subscription_id)
            .execute()
        )

        if response.data:
            await update_user_tier(response.data[0]["user_id"], "free")
    except Exception as e:
        print(f"Error handling Paddle subscription cancelled: {e}")


async def handle_paddle_payment_completed(webhook_data: dict):
    """Handle Paddle payment completed event"""
    try:
        transaction = webhook_data.get("data", {})
        subscription_id = transaction.get("subscription_id")

        transaction_data = {
            "subscription_id": subscription_id,
            "amount": transaction.get("total_amount", 0),
            "currency": transaction.get("currency", "USD"),
            "status": "completed",
            "payment_method": "paddle",
            "paddle_transaction_id": transaction.get("id"),
            "created_at": transaction.get("created_at"),
        }

        supabase.table("transactions").insert(transaction_data).execute()
    except Exception as e:
        print(f"Error handling Paddle payment completed: {e}")


@router.post("/webhook/razorpay")
async def razorpay_webhook(request: Request):
    """Handle Razorpay webhook events"""
    try:
        webhook_data = await request.json()
        event_type = webhook_data.get("event")

        if event_type == "subscription.created":
            await handle_razorpay_subscription_created(webhook_data)
        elif event_type == "subscription.cancelled":
            await handle_razorpay_subscription_cancelled(webhook_data)
        elif event_type == "payment.captured":
            await handle_razorpay_payment_captured(webhook_data)

        return {"status": "success"}
    except Exception as e:
        print(f"Razorpay webhook error: {e}")
        raise HTTPException(status_code=500, detail="Webhook processing failed")


async def handle_razorpay_subscription_created(webhook_data: dict):
    """Handle Razorpay subscription created event"""
    try:
        subscription = webhook_data.get("payload", {}).get("subscription", {})
        entity = subscription.get("entity", {})
        notes = entity.get("notes", {})
        user_id = notes.get("user_id")
        tier = notes.get("tier")

        subscription_data = {
            "user_id": user_id,
            "tier": tier,
            "payment_method": "razorpay",
            "currency": entity.get("currency", "INR"),
            "amount": entity.get("amount", 0) / 100,
            "status": "active",
            "razorpay_subscription_id": entity.get("id"),
            "started_at": entity.get("created_at"),
            "ends_at": entity.get("current_end"),
        }

        supabase.table("subscriptions").insert(subscription_data).execute()
        await update_user_tier(user_id, tier)
    except Exception as e:
        print(f"Error handling Razorpay subscription created: {e}")


async def handle_razorpay_subscription_cancelled(webhook_data: dict):
    """Handle Razorpay subscription cancelled event"""
    try:
        subscription = webhook_data.get("payload", {}).get("subscription", {})
        entity = subscription.get("entity", {})
        razorpay_subscription_id = entity.get("id")

        supabase.table("subscriptions").update({"status": "cancelled"}).eq(
            "razorpay_subscription_id", razorpay_subscription_id
        ).execute()

        response = (
            supabase.table("subscriptions")
            .select("user_id")
            .eq("razorpay_subscription_id", razorpay_subscription_id)
            .execute()
        )

        if response.data:
            await update_user_tier(response.data[0]["user_id"], "free")
    except Exception as e:
        print(f"Error handling Razorpay subscription cancelled: {e}")


async def handle_razorpay_payment_captured(webhook_data: dict):
    """Handle Razorpay payment captured event"""
    try:
        payment = webhook_data.get("payload", {}).get("payment", {})
        entity = payment.get("entity", {})
        subscription_id = entity.get("subscription_id")

        transaction_data = {
            "subscription_id": subscription_id,
            "amount": entity.get("amount", 0) / 100,
            "currency": entity.get("currency", "INR"),
            "status": "completed",
            "payment_method": "razorpay",
            "razorpay_order_id": entity.get("order_id"),
            "razorpay_payment_id": entity.get("id"),
            "created_at": entity.get("created_at"),
        }

        supabase.table("transactions").insert(transaction_data).execute()
    except Exception as e:
        print(f"Error handling Razorpay payment captured: {e}")


@router.get("/subscription", response_model=SubscriptionResponse)
async def get_subscription(token: Optional[str] = Header(None, alias="Authorization")):
    """Get user's subscription status"""
    user = await get_user_from_token(token.replace("Bearer ", "") if token else None)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    response = (
        supabase.table("subscriptions")
        .select("*")
        .eq("user_id", user["id"])
        .order("started_at", desc=True)
        .limit(1)
        .execute()
    )

    if not response.data:
        return SubscriptionResponse(
            tier="free",
            status="active",
            payment_method="none",
            currency="USD",
            amount=0,
            started_at="",
            ends_at=None,
        )

    subscription = response.data[0]
    return SubscriptionResponse(
        tier=subscription["tier"],
        status=subscription["status"],
        payment_method=subscription["payment_method"],
        currency=subscription["currency"],
        amount=subscription["amount"],
        started_at=str(subscription["started_at"]),
        ends_at=str(subscription["ends_at"]) if subscription["ends_at"] else None,
    )


@router.post("/cancel")
async def cancel_subscription(
    token: Optional[str] = Header(None, alias="Authorization"),
):
    """Cancel active subscription"""
    user = await get_user_from_token(token.replace("Bearer ", "") if token else None)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    response = (
        supabase.table("subscriptions")
        .select("*")
        .eq("user_id", user["id"])
        .eq("status", "active")
        .order("started_at", desc=True)
        .limit(1)
        .execute()
    )

    if not response.data:
        raise HTTPException(status_code=404, detail="No active subscription found")

    subscription = response.data[0]

    if subscription["payment_method"] == "paddle":
        await cancel_paddle_subscription(subscription["paddle_subscription_id"])
    elif subscription["payment_method"] == "razorpay":
        await cancel_razorpay_subscription(subscription["razorpay_subscription_id"])

    supabase.table("subscriptions").update({"status": "cancelled"}).eq(
        "id", subscription["id"]
    ).execute()

    await update_user_tier(user["id"], "free")

    return {"status": "success", "message": "Subscription cancelled successfully"}


async def cancel_paddle_subscription(paddle_subscription_id: str):
    """Cancel Paddle subscription"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.patch(
                f"https://api.paddle.com/subscriptions/{paddle_subscription_id}/cancel",
                headers={
                    "Authorization": f"Bearer {PADDLE_API_KEY}",
                },
            )
            response.raise_for_status()
    except Exception as e:
        print(f"Error cancelling Paddle subscription: {e}")
        raise HTTPException(status_code=500, detail="Failed to cancel subscription")


async def cancel_razorpay_subscription(razorpay_subscription_id: str):
    """Cancel Razorpay subscription"""
    try:
        auth = f"{RAZORPAY_KEY_ID}:{RAZORPAY_KEY_SECRET}"
        encoded_auth = auth.encode("utf-8").decode("utf-8")

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"https://api.razorpay.com/v1/subscriptions/{razorpay_subscription_id}/cancel",
                headers={
                    "Authorization": f"Basic {encoded_auth}",
                    "Content-Type": "application/json",
                },
            )
            response.raise_for_status()
    except Exception as e:
        print(f"Error cancelling Razorpay subscription: {e}")
        raise HTTPException(status_code=500, detail="Failed to cancel subscription")


@router.get("/currency")
async def get_currency(
    client_ip: Optional[str] = Header(None, alias="X-Forwarded-For"),
):
    """Get detected currency based on IP"""
    if client_ip:
        currency = await detect_currency_from_ip(client_ip.split(",")[0].strip())
        return {"currency": currency}
    return {"currency": "USD"}
