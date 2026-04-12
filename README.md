# Personal Blog API

REST API cho ứng dụng blog cá nhân, xây dựng bằng **FastAPI** + **PostgreSQL** với đầy đủ authentication, authorization theo vai trò (role-based), và bộ unit test tự động.

---

## Mục lục

- [Tổng quan kiến trúc](#tổng-quan-kiến-trúc)
- [Tech Stack](#tech-stack)
- [Cấu trúc project](#cấu-trúc-project)
- [Cài đặt & Chạy project](#cài-đặt--chạy-project)
- [Biến môi trường](#biến-môi-trường)
- [API Endpoints](#api-endpoints)
- [Phân quyền](#phân-quyền)
- [Unit Testing](#unit-testing)
- [Tài khoản mặc định](#tài-khoản-mặc-định)

---

## Tổng quan kiến trúc

```
Client
  │
  ▼
FastAPI App (app/main.py)
  ├── /auth      ─── Xác thực & quản lý user
  ├── /posts     ─── CRUD bài viết
  └── /posts/{id}/comments  ─── CRUD bình luận
        │
        ▼
   CRUD Layer (app/crud/)
        │
        ▼
   SQLAlchemy Async ORM
        │
        ▼
   PostgreSQL (qua asyncpg)
```

**Luồng xác thực:**
1. Client đăng nhập tại `POST /auth/login` → nhận JWT access token
2. Gắn token vào header `Authorization: Bearer <token>` cho các request cần xác thực
3. `get_current_user` dependency decode token, tra cứu user trong DB
4. `require_role(role)` dependency kiểm tra vai trò trước khi cho phép thực thi

---

## Tech Stack

| Thành phần | Công nghệ |
|---|---|
| Web framework | FastAPI 0.135 |
| Async ORM | SQLAlchemy 2.0 (asyncio) |
| Database | PostgreSQL 16 (asyncpg driver) |
| Migration | Alembic |
| Auth | JWT (python-jose) + bcrypt (passlib) |
| Validation | Pydantic v2 + pydantic-settings |
| Containerization | Docker + Docker Compose |
| Testing | pytest + pytest-asyncio + pytest-cov |
| Linting | Ruff (PEP8) |

---

## Cấu trúc project

```
day4-7/
├── app/
│   ├── main.py              # Khởi tạo FastAPI, đăng ký routers
│   ├── config.py            # Cấu hình qua biến môi trường (pydantic-settings)
│   ├── database.py          # Engine, session, Base declarative
│   ├── dependencies.py      # get_current_user, require_role
│   ├── utils.py             # Tiện ích (vd: gửi notification nền)
│   ├── auth/
│   │   └── auth.py          # hash password, verify, tạo JWT
│   ├── models/
│   │   └── models.py        # SQLAlchemy models: User, Post, Comment
│   ├── schemas/
│   │   └── schemas.py       # Pydantic schemas (request/response)
│   ├── crud/
│   │   ├── user.py          # CRUD operations cho User
│   │   ├── post.py          # CRUD operations cho Post
│   │   └── comment.py       # CRUD operations cho Comment
│   └── routers/
│       ├── auth.py          # Endpoints /auth/*
│       ├── posts.py         # Endpoints /posts/*
│       └── comments.py      # Endpoints /posts/{id}/comments/*
├── tests/
│   ├── conftest.py          # Shared fixtures (mock_db, helpers)
│   └── test_crud_post.py    # 20 unit tests cho app/crud/post.py
├── alembic/
│   ├── env.py
│   └── versions/            # Migration scripts
├── pytest.ini               # Cấu hình pytest-asyncio & coverage
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── .env.example             # Template biến môi trường
```

---

## Cài đặt & Chạy project

### Yêu cầu

- Docker & Docker Compose

### Chạy bằng Docker (khuyến nghị)

```bash
# 1. Sao chép và điền biến môi trường
cp .env.example .env

# 2. Khởi động containers (DB + Web)
docker-compose up -d

# 3. Chạy migration & seed dữ liệu mẫu
docker-compose run --rm web alembic upgrade head

# API sẵn sàng tại http://localhost:8000
# Swagger UI: http://localhost:8000/docs
```

```bash
# Dừng containers
docker-compose down

# Dừng và xóa toàn bộ dữ liệu (volumes)
docker-compose down -v
```

### Chạy local (không Docker)

```bash
# 1. Tạo và kích hoạt virtual environment
python -m venv .venv
source .venv/bin/activate   # Linux/macOS
.venv\Scripts\activate      # Windows

# 2. Cài dependencies
pip install -r requirements.txt
pip install pytest pytest-asyncio pytest-cov ruff

# 3. Cấu hình .env (trỏ DATABASE_URL đến PostgreSQL đang chạy)
cp .env.example .env

# 4. Chạy migration
alembic upgrade head

# 5. Khởi động server
uvicorn app.main:app --reload
```

---

## Biến môi trường

Tạo file `.env` từ template `.env.example`:

| Biến | Mô tả | Ví dụ |
|---|---|---|
| `DATABASE_URL` | Chuỗi kết nối PostgreSQL async | `postgresql+asyncpg://user:pass@localhost:5432/blogdb` |
| `SECRET_KEY` | Khóa bí mật ký JWT | chuỗi random dài ≥ 32 ký tự |
| `ALGORITHM` | Thuật toán JWT | `HS256` (mặc định) |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Thời hạn token (phút) | `60` (mặc định) |

---

## API Endpoints

### Authentication (`/auth`)

| Method | Endpoint | Xác thực | Mô tả |
|--------|----------|----------|-------|
| POST | `/auth/register` | Không | Đăng ký user mới |
| POST | `/auth/login` | Không | Đăng nhập, trả về JWT |
| POST | `/auth/change-password` | User | Đổi mật khẩu |
| GET | `/auth/users` | Admin | Danh sách tất cả users |
| GET | `/auth/users/{user_id}` | Admin | Chi tiết user |
| DELETE | `/auth/users/{user_id}` | Admin | Xóa user theo ID |
| DELETE | `/auth/users/email/{email}` | Admin | Xóa user theo email |

### Posts (`/posts`)

| Method | Endpoint | Xác thực | Mô tả |
|--------|----------|----------|-------|
| GET | `/posts/` | Không | Danh sách posts (có phân trang) |
| GET | `/posts/{post_id}` | Không | Chi tiết một post |
| GET | `/posts/user/{user_id}` | Không | Posts của một user |
| POST | `/posts/` | User | Tạo post mới |
| PUT | `/posts/{post_id}` | Chủ post / Admin | Cập nhật post |
| DELETE | `/posts/{post_id}` | Admin | Xóa post |

### Comments (`/posts/{post_id}/comments`)

| Method | Endpoint | Xác thực | Mô tả |
|--------|----------|----------|-------|
| GET | `/posts/{post_id}/comments/` | Không | Danh sách comments của post |
| POST | `/posts/{post_id}/comments/` | User | Thêm comment |
| PUT | `/posts/{post_id}/comments/{comment_id}` | Chủ comment / Admin | Sửa comment |
| DELETE | `/posts/{post_id}/comments/{comment_id}` | Chủ comment / Admin | Xóa comment |

---

## Phân quyền

| Role | Mô tả |
|---|---|
| `user` | Người dùng thường — tạo/sửa post & comment của mình |
| `admin` | Quản trị viên — toàn quyền trên tất cả tài nguyên |

> Admin có thể thực hiện mọi thao tác của `user`, cộng thêm: xóa post/comment của bất kỳ ai, quản lý danh sách user.

---

## Unit Testing

### Module được test

**`app/crud/post.py`** — toàn bộ 6 hàm CRUD bất đồng bộ cho Post.

### Chiến lược

- **Không cần database thật** — `AsyncSession` được mock hoàn toàn bằng `unittest.mock.AsyncMock`
- **Không cần server chạy** — test chỉ gọi thẳng các hàm CRUD
- **pytest-asyncio** (`asyncio_mode = auto`) — chạy các coroutine trong test mà không cần boilerplate
- **Ruff** — kiểm tra PEP8 trước khi merge

### Chạy tests

```bash
# Chạy toàn bộ test suite
pytest

# Chạy kèm báo cáo coverage (terminal)
pytest --cov=app.crud.post --cov-report=term-missing

# Xuất báo cáo HTML (mở htmlcov/index.html)
pytest --cov=app.crud.post --cov-report=html

# Kiểm tra style với Ruff
ruff check tests/
```

### Kết quả

```
tests/test_crud_post.py  20 passed in 4s

Name               Stmts   Miss  Cover   Missing
------------------------------------------------
app\crud\post.py      32      0   100%
------------------------------------------------
TOTAL                 32      0   100%
```

### Danh sách test cases

| Class | Test | Mô tả |
|---|---|---|
| `TestCreatePost` | `test_create_post_returns_new_post` | Tạo post thành công, gọi đúng add/commit/refresh |
| | `test_create_post_uses_correct_user_id` | `user_id` được truyền đúng vào model |
| `TestGetPosts` | `test_get_posts_returns_list` | Trả về danh sách posts |
| | `test_get_posts_empty` | Trả về list rỗng khi không có post |
| | `test_get_posts_default_pagination` | Chấp nhận skip=0, limit=100 mặc định |
| | `test_get_posts_custom_pagination` | Truyền skip/limit tùy chỉnh |
| `TestGetPost` | `test_get_post_found` | Trả về post khi tìm thấy |
| | `test_get_post_not_found` | Trả về `None` khi không có |
| | `test_get_post_calls_db_get_with_correct_id` | `db.get()` nhận đúng post_id |
| `TestGetPostsByUser` | `test_returns_posts_for_user` | Lọc đúng posts theo user |
| | `test_returns_empty_list_when_no_posts` | Trả về `[]` khi user chưa có post |
| | `test_custom_pagination_forwarded` | Pagination được forward xuống query |
| `TestUpdatePost` | `test_update_post_existing` | Cập nhật đầy đủ fields, commit & refresh |
| | `test_update_post_partial` | Partial update — chỉ field được truyền mới thay đổi |
| | `test_update_post_not_found_returns_none` | Trả về `None` khi post không tồn tại |
| | `test_update_post_no_commit_when_not_found` | `commit()` KHÔNG được gọi nếu không có post |
| `TestDeletePost` | `test_delete_post_existing` | Xóa thành công, trả về post đã xóa |
| | `test_delete_post_not_found` | Trả về `None` nếu post không tồn tại |
| | `test_delete_post_no_db_delete_when_missing` | `db.delete()` KHÔNG được gọi nếu không có post |
| | `test_delete_post_no_commit_when_missing` | `commit()` KHÔNG được gọi nếu không có post |

---

## Tài khoản mặc định

Được tạo tự động sau khi chạy `alembic upgrade head`:

| Field | Giá trị |
|---|---|
| Email | `admin@example.com` |
| Password | `admin123` |
| Role | `admin` |
