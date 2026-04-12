"""
HTTP client for order_service → cart_service and product_service calls.
"""
import requests
from django.conf import settings

CART_SERVICE_URL    = settings.CART_SERVICE_URL
PRODUCT_SERVICE_URL = settings.PRODUCT_SERVICE_URL
INTERNAL_TOKEN      = settings.INTERNAL_SERVICE_TOKEN
_TIMEOUT            = 5


def _headers():
    # Use "localhost" as Host to avoid Django rejecting Docker service names
    # (underscores in hostnames are invalid per RFC 1034/1035)
    return {
        "X-Service-Token": INTERNAL_TOKEN,
        "Content-Type": "application/json",
        "Host": "localhost",
    }


# ── Cart service ──────────────────────────────────────────────────────────────

def get_user_cart(user_id: int) -> dict:
    """Returns {"cart_id": ..., "items": [{"product_id": ..., "quantity": ...}]}"""
    resp = requests.get(
        f"{CART_SERVICE_URL}/internal/cart/{user_id}/",
        headers=_headers(),
        timeout=_TIMEOUT,
    )
    resp.raise_for_status()
    return resp.json()


def clear_user_cart(user_id: int) -> None:
    requests.delete(
        f"{CART_SERVICE_URL}/internal/cart/{user_id}/clear/",
        headers=_headers(),
        timeout=_TIMEOUT,
    )


# ── Product service ───────────────────────────────────────────────────────────

def get_product(product_id: int) -> dict | None:
    try:
        resp = requests.get(
            f"{PRODUCT_SERVICE_URL}/internal/products/{product_id}/",
            headers=_headers(),
            timeout=_TIMEOUT,
        )
        return resp.json() if resp.status_code == 200 else None
    except requests.RequestException:
        return None


def decrement_stock(product_id: int, quantity: int) -> dict:
    resp = requests.post(
        f"{PRODUCT_SERVICE_URL}/internal/products/{product_id}/decrement-stock/",
        json={"quantity": quantity},
        headers=_headers(),
        timeout=_TIMEOUT,
    )
    resp.raise_for_status()
    return resp.json()
