"""
Shared pytest fixtures for auth_service tests.

Fixtures follow the Arrange–Act–Assert pattern:
  - 'api_client'    → unauthenticated DRF test client
  - 'user'          → a regular active user
  - 'admin_user'    → a staff / superuser
  - 'auth_client'   → client pre-authenticated as regular user
  - 'admin_client'  → client pre-authenticated as admin
"""
import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import AccessToken

User = get_user_model()

# ── Constants reused across tests ─────────────────────────────────────────────

USER_EMAIL = "testuser@example.com"
USER_PASSWORD = "TestPass123!"
USER_FULL_NAME = "Test User"

ADMIN_EMAIL = "admin@example.com"
ADMIN_PASSWORD = "AdminPass123!"
ADMIN_FULL_NAME = "Admin User"


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def api_client():
    """Unauthenticated API client."""
    return APIClient()


@pytest.fixture
def user(db):
    """A regular, active user stored in the test database."""
    return User.objects.create_user(
        email=USER_EMAIL,
        password=USER_PASSWORD,
        full_name=USER_FULL_NAME,
    )


@pytest.fixture
def admin_user(db):
    """A superuser stored in the test database."""
    return User.objects.create_superuser(
        email=ADMIN_EMAIL,
        password=ADMIN_PASSWORD,
        full_name=ADMIN_FULL_NAME,
    )


@pytest.fixture
def auth_client(user):
    """APIClient with a valid JWT Bearer token for the regular user."""
    client = APIClient()
    token = AccessToken.for_user(user)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    return client


@pytest.fixture
def admin_client(admin_user):
    """APIClient with a valid JWT Bearer token for the admin user."""
    client = APIClient()
    token = AccessToken.for_user(admin_user)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    return client
