"""Seed admin user

Revision ID: seed_admin
Revises: a085d6475648
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = 'seed_admin'
down_revision = 'a085d6475648'
branch_labels = None
depends_on = None


def upgrade() -> None:
    hashed_password = '$2b$12$59IdSXGDlNSE4iBJpKboR.WUGSzUOYfD5oEiYJSdNIG.eyBSmM/Ne'
    
    op.execute(
        "INSERT INTO users (email, hashed_password, role) "
        "VALUES ('admin@example.com', '{hashed_password}', 'admin') "
        "ON CONFLICT (email) DO NOTHING".format(hashed_password=hashed_password)
    )


def downgrade() -> None:
    op.execute("DELETE FROM users WHERE email = 'admin@example.com'")
