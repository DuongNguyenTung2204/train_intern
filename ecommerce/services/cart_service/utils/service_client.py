"""
HTTP client used by cart_service to communicate with product_service.
All calls include the X-Service-Token header for internal auth.
"""
import requests
from django.conf import settings

PRODUCT_SERVICE_URL   = settings.PRODUCT_SERVICE_URL
INTERNAL_TOKEN        = settings.INTERNAL_SERVICE_TOKEN
_TIMEOUT              = 5   # seconds


def _headers():
    # Use "localhost" as Host to avoid Django rejecting Docker service names
    # (underscores in hostnames are invalid per RFC 1034/1035)
    return {
        "X-Service-Token": INTERNAL_TOKEN,
        "Content-Type": "application/json",
        "Host": "localhost",
    }


def get_product(product_id: int) -> dict | None:
    """Fetch a single product from product_service. Returns None if not found."""
    try:
        resp = requests.get(
            f"{PRODUCT_SERVICE_URL}/internal/products/{product_id}/",
            headers=_headers(),
            timeout=_TIMEOUT,
        )
        if resp.status_code == 200:
            return resp.json()
        return None
    except requests.RequestException:
        return None
