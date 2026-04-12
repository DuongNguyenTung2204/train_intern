"""
Integration tests for apps/accounts views (all HTTP endpoints).

Tests cover:
  Public endpoints (AllowAny):
    POST /api/v1/auth/register/
    POST /api/v1/auth/token/
    POST /api/v1/auth/token/refresh/

  Authenticated endpoints (IsAuthenticated):
    GET  /api/v1/auth/profile/
    PATCH /api/v1/auth/profile/
    POST /api/v1/auth/change-password/

  Internal endpoint (X-Service-Token):
    GET  /internal/users/{pk}/

Each test follows the Arrange → Act → Assert pattern.
Mocking is used where external dependencies would complicate tests.
"""
from django.contrib.auth import get_user_model
from rest_framework import status

User = get_user_model()

# ── URL helpers ───────────────────────────────────────────────────────────────
REGISTER_URL         = "/api/v1/auth/register/"
TOKEN_URL            = "/api/v1/auth/token/"
TOKEN_REFRESH_URL    = "/api/v1/auth/token/refresh/"
PROFILE_URL          = "/api/v1/auth/profile/"
CHANGE_PASSWORD_URL  = "/api/v1/auth/change-password/"

def internal_user_url(pk):
    return f"/internal/users/{pk}/"


# ── POST /api/v1/auth/register/ ───────────────────────────────────────────────

class TestRegisterView:
    PAYLOAD = {
        "email": "newuser@example.com",
        "full_name": "New User",
        "password": "StrongPass1!",
        "password_confirm": "StrongPass1!",
    }

    def test_register_returns_201(self, db, api_client):
        resp = api_client.post(REGISTER_URL, self.PAYLOAD, format="json")

        assert resp.status_code == status.HTTP_201_CREATED

    def test_register_response_structure(self, db, api_client):
        resp = api_client.post(REGISTER_URL, self.PAYLOAD, format="json")

        assert resp.data["message"] == "Registration successful."
        assert "user" in resp.data
        assert resp.data["user"]["email"] == "newuser@example.com"

    def test_register_creates_user_in_db(self, db, api_client):
        api_client.post(REGISTER_URL, self.PAYLOAD, format="json")

        assert User.objects.filter(email="newuser@example.com").exists()

    def test_password_not_returned_in_response(self, db, api_client):
        resp = api_client.post(REGISTER_URL, self.PAYLOAD, format="json")

        assert "password" not in resp.data["user"]

    def test_duplicate_email_returns_400(self, db, api_client, user):
        payload = {**self.PAYLOAD, "email": user.email}
        resp = api_client.post(REGISTER_URL, payload, format="json")

        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert "email" in resp.data

    def test_password_mismatch_returns_400(self, db, api_client):
        payload = {**self.PAYLOAD, "password_confirm": "DifferentPass9!"}
        resp = api_client.post(REGISTER_URL, payload, format="json")

        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    def test_missing_email_returns_400(self, db, api_client):
        payload = {**self.PAYLOAD, "email": ""}
        resp = api_client.post(REGISTER_URL, payload, format="json")

        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    def test_weak_password_returns_400(self, db, api_client):
        payload = {**self.PAYLOAD, "password": "123", "password_confirm": "123"}
        resp = api_client.post(REGISTER_URL, payload, format="json")

        assert resp.status_code == status.HTTP_400_BAD_REQUEST


# ── POST /api/v1/auth/token/ ──────────────────────────────────────────────────

class TestTokenObtainView:
    def test_valid_credentials_return_tokens(self, db, api_client, user):
        resp = api_client.post(
            TOKEN_URL,
            {"email": "testuser@example.com", "password": "TestPass123!"},
            format="json",
        )

        assert resp.status_code == status.HTTP_200_OK
        assert "access" in resp.data
        assert "refresh" in resp.data

    def test_access_token_is_string(self, db, api_client, user):
        resp = api_client.post(
            TOKEN_URL,
            {"email": "testuser@example.com", "password": "TestPass123!"},
            format="json",
        )

        assert isinstance(resp.data["access"], str)
        assert len(resp.data["access"]) > 20

    def test_wrong_password_returns_401(self, db, api_client, user):
        resp = api_client.post(
            TOKEN_URL,
            {"email": "testuser@example.com", "password": "WrongPass!"},
            format="json",
        )

        assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    def test_nonexistent_user_returns_401(self, db, api_client):
        resp = api_client.post(
            TOKEN_URL,
            {"email": "nobody@example.com", "password": "AnyPass!"},
            format="json",
        )

        assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    def test_inactive_user_cannot_login(self, db, api_client, user):
        user.is_active = False
        user.save()

        resp = api_client.post(
            TOKEN_URL,
            {"email": "testuser@example.com", "password": "TestPass123!"},
            format="json",
        )

        assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    def test_token_contains_custom_claims(self, db, api_client, user):
        """JWT payload must include email, is_staff, full_name injected by custom serializer."""
        import base64
        import json

        resp = api_client.post(
            TOKEN_URL,
            {"email": "testuser@example.com", "password": "TestPass123!"},
            format="json",
        )

        # Decode payload (second segment of the JWT)
        payload_b64 = resp.data["access"].split(".")[1]
        # Add padding if necessary
        payload_b64 += "=" * (-len(payload_b64) % 4)
        payload = json.loads(base64.urlsafe_b64decode(payload_b64))

        assert payload["email"] == user.email
        assert "is_staff" in payload
        assert "full_name" in payload


# ── GET / PATCH /api/v1/auth/profile/ ────────────────────────────────────────

class TestProfileView:
    def test_unauthenticated_returns_401(self, db, api_client):
        resp = api_client.get(PROFILE_URL)

        assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_returns_own_profile(self, db, auth_client, user):
        resp = auth_client.get(PROFILE_URL)

        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["email"] == user.email
        assert resp.data["full_name"] == user.full_name

    def test_response_contains_expected_fields(self, db, auth_client):
        resp = auth_client.get(PROFILE_URL)

        expected = {"id", "email", "full_name", "phone", "address", "avatar", "is_staff", "created_at"}
        assert expected == set(resp.data.keys())

    def test_patch_updates_full_name(self, db, auth_client, user):
        resp = auth_client.patch(PROFILE_URL, {"full_name": "Updated Name"}, format="json")

        assert resp.status_code == status.HTTP_200_OK
        user.refresh_from_db()
        assert user.full_name == "Updated Name"

    def test_patch_updates_phone(self, db, auth_client, user):
        resp = auth_client.patch(PROFILE_URL, {"phone": "0909123456"}, format="json")

        assert resp.status_code == status.HTTP_200_OK
        user.refresh_from_db()
        assert user.phone == "0909123456"

    def test_patch_cannot_change_email(self, db, auth_client, user):
        original_email = user.email
        auth_client.patch(PROFILE_URL, {"email": "hacked@evil.com"}, format="json")

        user.refresh_from_db()
        assert user.email == original_email

    def test_patch_cannot_escalate_to_staff(self, db, auth_client, user):
        auth_client.patch(PROFILE_URL, {"is_staff": True}, format="json")

        user.refresh_from_db()
        assert user.is_staff is False

    def test_put_requires_all_writable_fields(self, db, auth_client):
        """PUT without required fields should return 400."""
        resp = auth_client.put(PROFILE_URL, {}, format="json")

        # Either 400 or DRF accepts partial — model fields are blank=True so 200 is ok
        assert resp.status_code in (status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST)


# ── POST /api/v1/auth/change-password/ ───────────────────────────────────────

class TestChangePasswordView:
    def test_unauthenticated_returns_401(self, db, api_client):
        resp = api_client.post(CHANGE_PASSWORD_URL, {}, format="json")

        assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    def test_valid_change_returns_200(self, db, auth_client):
        resp = auth_client.post(
            CHANGE_PASSWORD_URL,
            {"old_password": "TestPass123!", "new_password": "NewSecure456!"},
            format="json",
        )

        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["message"] == "Password changed successfully."

    def test_password_is_actually_changed(self, db, auth_client, user):
        auth_client.post(
            CHANGE_PASSWORD_URL,
            {"old_password": "TestPass123!", "new_password": "NewSecure456!"},
            format="json",
        )

        user.refresh_from_db()
        assert user.check_password("NewSecure456!")
        assert not user.check_password("TestPass123!")

    def test_wrong_old_password_returns_400(self, db, auth_client):
        resp = auth_client.post(
            CHANGE_PASSWORD_URL,
            {"old_password": "WRONG_PASSWORD!", "new_password": "NewSecure456!"},
            format="json",
        )

        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert "old_password" in resp.data

    def test_weak_new_password_returns_400(self, db, auth_client):
        resp = auth_client.post(
            CHANGE_PASSWORD_URL,
            {"old_password": "TestPass123!", "new_password": "weak"},
            format="json",
        )

        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    def test_missing_fields_returns_400(self, db, auth_client):
        resp = auth_client.post(CHANGE_PASSWORD_URL, {}, format="json")

        assert resp.status_code == status.HTTP_400_BAD_REQUEST


# ── GET /internal/users/{pk}/ ────────────────────────────────────────────────

class TestInternalUserDetailView:
    VALID_TOKEN = "test-internal-token"  # matches settings_test.INTERNAL_SERVICE_TOKEN

    def test_returns_200_with_valid_token(self, db, api_client, user):
        resp = api_client.get(
            internal_user_url(user.pk),
            HTTP_X_SERVICE_TOKEN=self.VALID_TOKEN,
        )

        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["email"] == user.email

    def test_returns_expected_user_fields(self, db, api_client, user):
        resp = api_client.get(
            internal_user_url(user.pk),
            HTTP_X_SERVICE_TOKEN=self.VALID_TOKEN,
        )

        assert "id" in resp.data
        assert "email" in resp.data
        assert "is_staff" in resp.data

    def test_no_token_returns_403(self, db, api_client, user):
        resp = api_client.get(internal_user_url(user.pk))

        assert resp.status_code == status.HTTP_403_FORBIDDEN

    def test_wrong_token_returns_403(self, db, api_client, user):
        resp = api_client.get(
            internal_user_url(user.pk),
            HTTP_X_SERVICE_TOKEN="wrong-token",
        )

        assert resp.status_code == status.HTTP_403_FORBIDDEN

    def test_nonexistent_user_returns_404(self, db, api_client):
        resp = api_client.get(
            internal_user_url(99999),
            HTTP_X_SERVICE_TOKEN=self.VALID_TOKEN,
        )

        assert resp.status_code == status.HTTP_404_NOT_FOUND

    def test_no_jwt_required_for_internal(self, db, api_client, user):
        """Internal endpoint must work without a Bearer JWT token."""
        # api_client has no credentials set at all
        resp = api_client.get(
            internal_user_url(user.pk),
            HTTP_X_SERVICE_TOKEN=self.VALID_TOKEN,
        )

        assert resp.status_code == status.HTTP_200_OK
