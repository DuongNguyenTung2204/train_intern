"""
Unit tests for apps/accounts/serializers.py

Tests cover:
  - RegisterSerializer        — validation, password hashing, write_only fields
  - UserSerializer            — read-only fields, field coverage
  - ChangePasswordSerializer  — old password check, save() changes password
  - CustomTokenObtainPairSerializer — extra JWT claims

Mocking strategy:
  - ChangePasswordSerializer requires a request-like context object; we use
    unittest.mock.MagicMock to supply it without a real HTTP request.
"""
from unittest.mock import MagicMock

from django.contrib.auth import get_user_model

from apps.accounts.serializers import (
    ChangePasswordSerializer,
    CustomTokenObtainPairSerializer,
    RegisterSerializer,
    UserSerializer,
)

User = get_user_model()


# ── RegisterSerializer ────────────────────────────────────────────────────────

class TestRegisterSerializer:
    VALID_PAYLOAD = {
        "email": "new@example.com",
        "full_name": "New User",
        "password": "StrongPass1!",
        "password_confirm": "StrongPass1!",
    }

    def test_valid_data_is_accepted(self, db):
        s = RegisterSerializer(data=self.VALID_PAYLOAD)

        assert s.is_valid(), s.errors

    def test_creates_user_on_save(self, db):
        s = RegisterSerializer(data=self.VALID_PAYLOAD)
        s.is_valid(raise_exception=True)
        user = s.save()

        assert User.objects.filter(pk=user.pk).exists()
        assert user.email == "new@example.com"

    def test_passwords_must_match(self, db):
        payload = {**self.VALID_PAYLOAD, "password_confirm": "WrongPass9!"}
        s = RegisterSerializer(data=payload)

        assert not s.is_valid()
        assert "password" in s.errors

    def test_password_confirm_not_in_validated_data(self, db):
        """password_confirm must be popped before create() receives it."""
        s = RegisterSerializer(data=self.VALID_PAYLOAD)
        s.is_valid(raise_exception=True)

        assert "password_confirm" not in s.validated_data

    def test_password_is_write_only(self, db):
        """Password must not appear in serialized output."""
        s = RegisterSerializer(data=self.VALID_PAYLOAD)
        s.is_valid(raise_exception=True)
        user = s.save()

        output = RegisterSerializer(user)
        assert "password" not in output.data

    def test_password_is_hashed(self, db):
        s = RegisterSerializer(data=self.VALID_PAYLOAD)
        s.is_valid(raise_exception=True)
        user = s.save()

        assert user.check_password("StrongPass1!")
        assert user.password != "StrongPass1!"

    def test_email_is_required(self, db):
        payload = {**self.VALID_PAYLOAD, "email": ""}
        s = RegisterSerializer(data=payload)

        assert not s.is_valid()
        assert "email" in s.errors

    def test_weak_password_is_rejected(self, db):
        """Django's MinimumLengthValidator must fire."""
        payload = {**self.VALID_PAYLOAD, "password": "short", "password_confirm": "short"}
        s = RegisterSerializer(data=payload)

        assert not s.is_valid()
        assert "password" in s.errors

    def test_duplicate_email_fails_at_db(self, db, user):
        """Uniqueness is enforced; serializer surfaces the DB error."""
        payload = {**self.VALID_PAYLOAD, "email": user.email}
        s = RegisterSerializer(data=payload)

        assert not s.is_valid()
        assert "email" in s.errors


# ── UserSerializer ────────────────────────────────────────────────────────────

class TestUserSerializer:
    def test_serializes_expected_fields(self, user):
        data = UserSerializer(user).data

        expected = {"id", "email", "full_name", "phone", "address", "avatar", "is_staff", "created_at"}
        assert expected == set(data.keys())

    def test_email_is_read_only(self, user):
        """email must not be updatable through the serializer."""
        s = UserSerializer(user, data={"email": "hacked@example.com"}, partial=True)
        s.is_valid(raise_exception=True)
        updated = s.save()

        assert updated.email == user.email  # unchanged

    def test_is_staff_is_read_only(self, user):
        s = UserSerializer(user, data={"is_staff": True}, partial=True)
        s.is_valid(raise_exception=True)
        updated = s.save()

        assert updated.is_staff is False  # unchanged

    def test_full_name_can_be_updated(self, user):
        s = UserSerializer(user, data={"full_name": "Updated"}, partial=True)
        s.is_valid(raise_exception=True)
        updated = s.save()

        assert updated.full_name == "Updated"


# ── ChangePasswordSerializer ──────────────────────────────────────────────────

class TestChangePasswordSerializer:
    def _make_request(self, user):
        """Return a minimal mock request carrying `user`."""
        req = MagicMock()
        req.user = user
        return req

    def test_valid_old_password_passes(self, user):
        req = self._make_request(user)
        s = ChangePasswordSerializer(
            data={"old_password": "TestPass123!", "new_password": "NewPass456!"},
            context={"request": req},
        )

        assert s.is_valid(), s.errors

    def test_wrong_old_password_rejected(self, user):
        req = self._make_request(user)
        s = ChangePasswordSerializer(
            data={"old_password": "WrongPassword!", "new_password": "NewPass456!"},
            context={"request": req},
        )

        assert not s.is_valid()
        assert "old_password" in s.errors

    def test_save_changes_password(self, db, user):
        req = self._make_request(user)
        s = ChangePasswordSerializer(
            data={"old_password": "TestPass123!", "new_password": "NewPass456!"},
            context={"request": req},
        )
        s.is_valid(raise_exception=True)
        s.save()

        user.refresh_from_db()
        assert user.check_password("NewPass456!")

    def test_weak_new_password_rejected(self, user):
        req = self._make_request(user)
        s = ChangePasswordSerializer(
            data={"old_password": "TestPass123!", "new_password": "weak"},
            context={"request": req},
        )

        assert not s.is_valid()
        assert "new_password" in s.errors

    def test_new_password_is_write_only(self, user):
        """new_password must never appear in output."""
        req = self._make_request(user)
        s = ChangePasswordSerializer(
            data={"old_password": "TestPass123!", "new_password": "NewPass456!"},
            context={"request": req},
        )
        s.is_valid(raise_exception=True)

        assert "new_password" not in s.data


# ── CustomTokenObtainPairSerializer ──────────────────────────────────────────

class TestCustomTokenObtainPairSerializer:
    def test_token_contains_email_claim(self, db, user):
        token = CustomTokenObtainPairSerializer.get_token(user)

        assert token["email"] == user.email

    def test_token_contains_is_staff_claim(self, db, user):
        token = CustomTokenObtainPairSerializer.get_token(user)

        assert token["is_staff"] == user.is_staff

    def test_token_contains_full_name_claim(self, db, user):
        token = CustomTokenObtainPairSerializer.get_token(user)

        assert token["full_name"] == user.full_name

    def test_admin_token_has_is_staff_true(self, db, admin_user):
        token = CustomTokenObtainPairSerializer.get_token(admin_user)

        assert token["is_staff"] is True

    def test_token_contains_user_id(self, db, user):
        """Standard simplejwt claim 'user_id' must still be present."""
        token = CustomTokenObtainPairSerializer.get_token(user)

        assert token["user_id"] == user.pk
