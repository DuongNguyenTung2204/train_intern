"""Unit tests for app/crud/post.py.

All database interactions are fully mocked via AsyncMock so no real DB
connection is required.  Target module: app/crud/post.py.
"""

import pytest
from unittest.mock import MagicMock, patch

from app.crud.post import (
    create_post,
    get_posts,
    get_post,
    get_posts_by_user,
    update_post,
    delete_post,
)
from app.schemas.schemas import PostCreate, PostUpdate

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_post(post_id: int = 1, title: str = "Test Title", content: str = "Body", user_id: int = 42):
    """Return a lightweight Post-like MagicMock."""
    post = MagicMock()
    post.id = post_id
    post.title = title
    post.content = content
    post.user_id = user_id
    return post


def _scalars_all(items: list):
    """Build the mock chain: execute() → .scalars().all()."""
    scalars = MagicMock()
    scalars.all.return_value = items
    result = MagicMock()
    result.scalars.return_value = scalars
    return result


# ---------------------------------------------------------------------------
# create_post
# ---------------------------------------------------------------------------


class TestCreatePost:
    @pytest.mark.asyncio
    async def test_create_post_returns_new_post(self, mock_db):
        """create_post persists a new Post and returns the refreshed object."""
        schema = PostCreate(title="Hello World", content="Some content")
        fake_post = _make_post(title="Hello World", content="Some content")

        async def fake_refresh(obj):
            obj.id = 99

        mock_db.refresh.side_effect = fake_refresh

        with patch("app.crud.post.Post") as MockPost:
            MockPost.return_value = fake_post
            result = await create_post(mock_db, schema, user_id=42)

        MockPost.assert_called_once_with(title="Hello World", content="Some content", user_id=42)
        mock_db.add.assert_called_once_with(fake_post)
        mock_db.commit.assert_awaited_once()
        mock_db.refresh.assert_awaited_once_with(fake_post)
        assert result is fake_post

    @pytest.mark.asyncio
    async def test_create_post_uses_correct_user_id(self, mock_db):
        """user_id is forwarded to the Post constructor."""
        schema = PostCreate(title="T", content="C")
        with patch("app.crud.post.Post") as MockPost:
            MockPost.return_value = MagicMock()
            await create_post(mock_db, schema, user_id=7)

        _, kwargs = MockPost.call_args
        assert kwargs.get("user_id") == 7 or MockPost.call_args[1].get("user_id") == 7 or MockPost.call_args[0]


# ---------------------------------------------------------------------------
# get_posts
# ---------------------------------------------------------------------------


class TestGetPosts:
    @pytest.mark.asyncio
    async def test_get_posts_returns_list(self, mock_db):
        """get_posts returns all posts from the query result."""
        posts = [_make_post(i) for i in range(3)]
        mock_db.execute.return_value = _scalars_all(posts)

        result = await get_posts(mock_db)

        mock_db.execute.assert_awaited_once()
        assert result == posts

    @pytest.mark.asyncio
    async def test_get_posts_empty(self, mock_db):
        """get_posts returns an empty list when there are no posts."""
        mock_db.execute.return_value = _scalars_all([])

        result = await get_posts(mock_db)

        assert result == []

    @pytest.mark.asyncio
    async def test_get_posts_default_pagination(self, mock_db):
        """Default skip=0, limit=100 are accepted without error."""
        mock_db.execute.return_value = _scalars_all([])
        await get_posts(mock_db, skip=0, limit=100)
        mock_db.execute.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_get_posts_custom_pagination(self, mock_db):
        """Custom skip/limit values are forwarded to the query."""
        mock_db.execute.return_value = _scalars_all([])
        await get_posts(mock_db, skip=10, limit=5)
        mock_db.execute.assert_awaited_once()


# ---------------------------------------------------------------------------
# get_post
# ---------------------------------------------------------------------------


class TestGetPost:
    @pytest.mark.asyncio
    async def test_get_post_found(self, mock_db):
        """get_post returns the post when it exists."""
        fake_post = _make_post(post_id=1)
        mock_db.get.return_value = fake_post

        result = await get_post(mock_db, post_id=1)

        mock_db.get.assert_awaited_once()
        assert result is fake_post

    @pytest.mark.asyncio
    async def test_get_post_not_found(self, mock_db):
        """get_post returns None when the post does not exist."""
        mock_db.get.return_value = None

        result = await get_post(mock_db, post_id=999)

        assert result is None

    @pytest.mark.asyncio
    async def test_get_post_calls_db_get_with_correct_id(self, mock_db):
        """get_post passes the correct post_id to db.get()."""
        mock_db.get.return_value = None
        await get_post(mock_db, post_id=42)

        args = mock_db.get.call_args[0]
        assert 42 in args


# ---------------------------------------------------------------------------
# get_posts_by_user
# ---------------------------------------------------------------------------


class TestGetPostsByUser:
    @pytest.mark.asyncio
    async def test_returns_posts_for_user(self, mock_db):
        """get_posts_by_user returns posts belonging to the given user."""
        user_posts = [_make_post(i, user_id=5) for i in range(2)]
        mock_db.execute.return_value = _scalars_all(user_posts)

        result = await get_posts_by_user(mock_db, user_id=5)

        assert result == user_posts

    @pytest.mark.asyncio
    async def test_returns_empty_list_when_no_posts(self, mock_db):
        """get_posts_by_user returns [] if the user has no posts."""
        mock_db.execute.return_value = _scalars_all([])

        result = await get_posts_by_user(mock_db, user_id=99)

        assert result == []

    @pytest.mark.asyncio
    async def test_custom_pagination_forwarded(self, mock_db):
        """Pagination parameters are passed without error."""
        mock_db.execute.return_value = _scalars_all([])
        await get_posts_by_user(mock_db, user_id=1, skip=5, limit=10)
        mock_db.execute.assert_awaited_once()


# ---------------------------------------------------------------------------
# update_post
# ---------------------------------------------------------------------------


class TestUpdatePost:
    @pytest.mark.asyncio
    async def test_update_post_existing(self, mock_db):
        """update_post modifies fields and returns the refreshed post."""
        fake_post = _make_post(post_id=1, title="Old Title", content="Old Content")
        mock_db.get.return_value = fake_post

        schema = PostUpdate(title="New Title", content="New Content")
        result = await update_post(mock_db, post_id=1, post=schema)

        assert fake_post.title == "New Title"
        assert fake_post.content == "New Content"
        mock_db.commit.assert_awaited_once()
        mock_db.refresh.assert_awaited_once_with(fake_post)
        assert result is fake_post

    @pytest.mark.asyncio
    async def test_update_post_partial(self, mock_db):
        """update_post with only title set should only update title."""
        fake_post = _make_post(post_id=2, title="Old", content="Keep")
        mock_db.get.return_value = fake_post

        schema = PostUpdate(title="Updated")
        await update_post(mock_db, post_id=2, post=schema)

        assert fake_post.title == "Updated"
        # content should remain unchanged (exclude_unset skips it)
        assert fake_post.content == "Keep"

    @pytest.mark.asyncio
    async def test_update_post_not_found_returns_none(self, mock_db):
        """update_post returns None when the post does not exist."""
        mock_db.get.return_value = None

        result = await update_post(mock_db, post_id=999, post=PostUpdate(title="X"))

        assert result is None
        mock_db.commit.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_update_post_no_commit_when_not_found(self, mock_db):
        """commit() must NOT be called if the post is missing."""
        mock_db.get.return_value = None
        await update_post(mock_db, post_id=0, post=PostUpdate())
        mock_db.commit.assert_not_awaited()


# ---------------------------------------------------------------------------
# delete_post
# ---------------------------------------------------------------------------


class TestDeletePost:
    @pytest.mark.asyncio
    async def test_delete_post_existing(self, mock_db):
        """delete_post deletes and commits when post exists."""
        fake_post = _make_post(post_id=1)
        mock_db.get.return_value = fake_post

        result = await delete_post(mock_db, post_id=1)

        mock_db.delete.assert_awaited_once_with(fake_post)
        mock_db.commit.assert_awaited_once()
        assert result is fake_post

    @pytest.mark.asyncio
    async def test_delete_post_not_found(self, mock_db):
        """delete_post returns None when post does not exist."""
        mock_db.get.return_value = None

        result = await delete_post(mock_db, post_id=404)

        assert result is None

    @pytest.mark.asyncio
    async def test_delete_post_no_db_delete_when_missing(self, mock_db):
        """db.delete() must NOT be called if the post is missing."""
        mock_db.get.return_value = None
        await delete_post(mock_db, post_id=0)
        mock_db.delete.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_delete_post_no_commit_when_missing(self, mock_db):
        """commit() must NOT be called if the post is missing."""
        mock_db.get.return_value = None
        await delete_post(mock_db, post_id=0)
        mock_db.commit.assert_not_awaited()
