"""Shared fixtures for all test modules."""

import pytest
from unittest.mock import AsyncMock, MagicMock


@pytest.fixture
def mock_db():
    """Return a fully-mocked AsyncSession."""
    db = AsyncMock()
    db.add = MagicMock()  # add() is synchronous in SQLAlchemy
    db.commit = AsyncMock()
    db.refresh = AsyncMock()
    db.delete = AsyncMock()
    db.get = AsyncMock()
    db.execute = AsyncMock()
    return db


def make_scalars_result(items):
    """Helper: build the mock returned by db.execute() for list queries."""
    scalars = MagicMock()
    scalars.all.return_value = items
    scalars.first.return_value = items[0] if items else None

    result = MagicMock()
    result.scalars.return_value = scalars
    return result
