"""
Unit tests for apps/accounts/models.py

Tests cover:
  - UserManager.create_user()       — happy path, missing email, password hashing
  - UserManager.create_superuser()  — flags set correctly
  - User.__str__()                  — string representation
  - User.Meta.ordering              — default queryset order
  - User field constraints          — unique email
"""
import pytest
from django.contrib.auth import get_user_model
from django.db import IntegrityError

User = get_user_model()


# ── UserManager.create_user ───────────────────────────────────────────────────

class TestCreateUser:
    def test_creates_user_with_email_and_password(self, db):
        user = User.objects.create_user(email="alice@example.com", password="Secret123!")

        assert user.pk is not None
        assert user.email == "alice@example.com"

    def test_email_is_normalised(self, db):
        """Domain part of email should be lowercased."""
        user = User.objects.create_user(email="Bob@EXAMPLE.COM", password="Secret123!")

        assert user.email == "Bob@example.com"

    def test_password_is_hashed(self, db):
        """Raw password must never be stored in plain text."""
        user = User.objects.create_user(email="alice@example.com", password="Secret123!")

        assert user.password != "Secret123!"
        assert user.check_password("Secret123!") is True

    def test_raises_if_email_is_empty(self, db):
        with pytest.raises(ValueError, match="Email is required"):
            User.objects.create_user(email="", password="Secret123!")

    def test_raises_if_email_is_none(self, db):
        with pytest.raises(ValueError, match="Email is required"):
            User.objects.create_user(email=None, password="Secret123!")

    def test_user_is_active_by_default(self, db):
        user = User.objects.create_user(email="alice@example.com", password="pass")

        assert user.is_active is True

    def test_user_is_not_staff_by_default(self, db):
        user = User.objects.create_user(email="alice@example.com", password="pass")

        assert user.is_staff is False

    def test_user_is_not_superuser_by_default(self, db):
        user = User.objects.create_user(email="alice@example.com", password="pass")

        assert user.is_superuser is False

    def test_extra_fields_are_saved(self, db):
        user = User.objects.create_user(
            email="alice@example.com",
            password="pass",
            full_name="Alice",
            phone="0901234567",
        )

        assert user.full_name == "Alice"
        assert user.phone == "0901234567"

    def test_password_none_creates_unusable_password(self, db):
        """create_user with password=None → unusable password (can't log in)."""
        user = User.objects.create_user(email="alice@example.com", password=None)

        assert not user.has_usable_password()


# ── UserManager.create_superuser ─────────────────────────────────────────────

class TestCreateSuperuser:
    def test_creates_superuser(self, db):
        su = User.objects.create_superuser(email="su@example.com", password="pass")

        assert su.is_staff is True
        assert su.is_superuser is True

    def test_superuser_is_saved_to_db(self, db):
        su = User.objects.create_superuser(email="su@example.com", password="pass")

        assert User.objects.filter(pk=su.pk).exists()

    def test_superuser_extra_fields(self, db):
        su = User.objects.create_superuser(
            email="su@example.com", password="pass", full_name="Super"
        )

        assert su.full_name == "Super"


# ── User model ────────────────────────────────────────────────────────────────

class TestUserModel:
    def test_str_returns_email(self, user):
        assert str(user) == user.email

    def test_username_field_is_email(self):
        assert User.USERNAME_FIELD == "email"

    def test_required_fields_contains_full_name(self):
        assert "full_name" in User.REQUIRED_FIELDS

    def test_email_must_be_unique(self, db, user):
        with pytest.raises(IntegrityError):
            User.objects.create_user(email=user.email, password="OtherPass!")

    def test_default_ordering_newest_first(self, db):
        """Users should be returned newest first (ordering = ['-created_at'])."""
        u1 = User.objects.create_user(email="first@example.com", password="pass")
        u2 = User.objects.create_user(email="second@example.com", password="pass")

        qs = list(User.objects.all())
        # u2 was created after u1 → u2 should appear first
        assert qs[0].pk == u2.pk
        assert qs[1].pk == u1.pk

    def test_blank_fields_have_defaults(self, db):
        user = User.objects.create_user(email="minimal@example.com", password="pass")

        assert user.full_name == ""
        assert user.phone == ""
        assert user.address == ""
        assert user.avatar.name is None

    def test_auto_timestamps(self, user):
        assert user.created_at is not None
        assert user.updated_at is not None

    def test_updated_at_changes_on_save(self, user):
        original_updated = user.updated_at
        user.full_name = "New Name"
        user.save()

        user.refresh_from_db()
        assert user.updated_at >= original_updated
