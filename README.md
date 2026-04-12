# EShop — Microservices Backend

Kiến trúc Microservices cho mini project E-commerce (Day 8–12).  
Mỗi service là một **Django project độc lập** với database riêng, giao tiếp qua HTTP nội bộ.

---

## Kiến trúc tổng quan

```
                    ┌──────────────────────────────────────────────────┐
                    │             Nginx API Gateway  :8000             │
                    │                                                  │
                    │   /api/v1/auth/*      →  auth_service    :8001   │
                    │   /api/v1/products/*  →  product_service :8002   │
                    │   /api/v1/cart/*      →  cart_service    :8003   │
                    │   /api/v1/orders/*    →  order_service   :8004   │
                    │   /internal/*         →  403 BLOCKED             │
                    └────────────────────┬─────────────────────────────┘
                                         │  Docker network: ecommerce_net
          ┌──────────────────────────────┼───────────────────────────────┐
          │                              │                               │
  ┌───────▼───────┐             ┌────────▼───────┐              ┌────────▼───────┐
  │  auth_service │             │product_service │              │  cart_service  │
  │    :8001      │             │    :8002       │              │    :8003       │
  │   auth_db     │             │   product_db   │              │   cart_db      │
  └───────────────┘             └───────┬────────┘              └───────┬────────┘
                                        │ /internal/products/           │ /internal/cart/
                                        └──────────────┬────────────────┘
                                                       │
                                              ┌────────▼────────┐
                                              │  order_service  │
                                              │    :8004        │
                                              │   order_db      │
                                              │  celery worker  │
                                              └────────┬────────┘
                                                       │
                                                  ┌────▼────┐
                                                  │  Redis  │
                                                  └─────────┘
```

---

## Cấu trúc thư mục

```
ecommerce/
├── gateway/
│   └── nginx.conf                    # API Gateway — routing & /internal/ block
├── services/
│   ├── auth_service/                 # Port 8001 | DB: auth_db
│   │   ├── config/
│   │   │   ├── settings.py
│   │   │   └── settings_test.py      # SQLite in-memory cho test
│   │   ├── apps/accounts/            # User model, JWT, register, profile
│   │   │   ├── models.py             # CustomUser + UserManager
│   │   │   ├── serializers.py        # Register, Profile, ChangePassword, JWT
│   │   │   ├── views.py              # Public & authenticated endpoints
│   │   │   └── internal_views.py     # GET /internal/users/{id}/
│   │   ├── tests/
│   │   │   ├── conftest.py           # Fixtures: api_client, user, auth_client
│   │   │   ├── test_models.py        # 20 tests — UserManager & User model
│   │   │   ├── test_serializers.py   # 22 tests — tất cả serializers
│   │   │   └── test_views.py         # 37 tests — tất cả HTTP endpoints
│   │   ├── pytest.ini                # pytest + coverage config
│   │   └── ruff.toml                 # Linter: PEP8, isort, bugbear, naming
│   │
│   ├── product_service/              # Port 8002 | DB: product_db
│   │   ├── utils/authentication.py   # JWT verify via shared signing key
│   │   └── apps/products/            # Category, Product, filter, search
│   │       └── internal_views.py     # GET & POST decrement-stock
│   │
│   ├── cart_service/                 # Port 8003 | DB: cart_db
│   │   ├── utils/
│   │   │   ├── authentication.py     # JWT verify
│   │   │   └── service_client.py     # HTTP client → product_service
│   │   └── apps/cart/                # Cart, CartItem
│   │       └── internal_views.py     # GET & DELETE /internal/cart/{user_id}/
│   │
│   └── order_service/                # Port 8004 | DB: order_db
│       ├── config/celery.py          # Celery app config
│       ├── utils/
│       │   ├── authentication.py     # JWT verify
│       │   └── service_client.py     # HTTP client → cart + product services
│       └── apps/orders/              # Order, OrderItem
│           ├── tasks.py              # Async email (Celery)
│           └── signals.py            # post_save → trigger email task
│
├── docker-compose.yml                # 11 containers: 4 Django + 4 Postgres + Redis + Celery + Nginx
├── .env.example
└── README.md
```

---

## Nguyên tắc thiết kế

| Nguyên tắc | Cách áp dụng |
|---|---|
| **Database per service** | auth_db, product_db, cart_db, order_db — hoàn toàn tách biệt |
| **JWT stateless** | Mỗi service tự verify token bằng shared `JWT_SIGNING_KEY`, không gọi auth_service mỗi request |
| **Internal API** | `/internal/*` bị nginx block từ ngoài; service-to-service dùng `X-Service-Token` header |
| **Data snapshot** | OrderItem lưu name/price tại thời điểm checkout — miễn nhiễm khi sản phẩm đổi giá |
| **Async email** | order_service dùng Celery + Redis, không block HTTP response |
| **Soft FK** | cart_service.product_id & order_service.product_id là integer thuần — không CASCADE cross-service |

---

## Khởi chạy (Docker — khuyến nghị)

### Bước 1 — Cấu hình môi trường

```bash
cd ecommerce
cp .env.example .env
# Chỉnh sửa .env: đổi JWT_SIGNING_KEY và INTERNAL_SERVICE_TOKEN
```

### Bước 2 — Build & khởi động toàn bộ stack

```bash
docker compose up -d --build
```

> Lần đầu build mất ~2 phút. Dùng `-d` để chạy nền (detached mode).

### Bước 3 — Kiểm tra trạng thái containers

```bash
docker compose ps
# Tất cả container phải ở trạng thái "Up"

docker compose logs -f          # xem log realtime tất cả service
docker compose logs auth_service  # xem log 1 service cụ thể
```

### Bước 4 — Tạo superuser (tuỳ chọn)

```bash
# Auth service — bắt buộc nếu muốn dùng Django Admin
docker compose exec auth_service python manage.py createsuperuser

# Product service — để quản lý sản phẩm qua admin
docker compose exec product_service python manage.py createsuperuser
```

### Các địa chỉ quan trọng

| Địa chỉ | Mô tả |
|---|---|
| `http://localhost:8000` | **API Gateway** — endpoint duy nhất cho client |
| `http://localhost:8001/admin/` | Django Admin — Auth service |
| `http://localhost:8002/admin/` | Django Admin — Product service |
| `http://localhost:8003/admin/` | Django Admin — Cart service |
| `http://localhost:8004/admin/` | Django Admin — Order service |

---

## Khởi chạy từng service riêng lẻ (local dev)

```bash
cd services/auth_service

# Tạo và kích hoạt virtual environment
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # macOS/Linux

pip install -r requirements.txt

# Đặt biến môi trường
set DJANGO_SETTINGS_MODULE=config.settings
set JWT_SIGNING_KEY=dev-secret
set DB_HOST=localhost            # cần PostgreSQL chạy local

python manage.py migrate
python manage.py runserver 8001
```

Lặp lại cho các service còn lại với port 8002, 8003, 8004.

---

## Unit Tests (auth_service)

Bộ test được viết bằng **pytest + pytest-django** với SQLite in-memory — **không cần PostgreSQL hay Docker** để chạy test.

### Cấu trúc test

```
services/auth_service/tests/
├── conftest.py           # Fixtures dùng chung: api_client, user, auth_client, admin_user
├── test_models.py        # 20 tests — CustomUser model & UserManager
├── test_serializers.py   # 22 tests — Serializers (Register, Profile, ChangePassword, JWT)
└── test_views.py         # 37 tests — HTTP endpoints (Register, Token, Profile, ChangePassword, Internal)
```

### Cài đặt dependencies

```bash
cd services/auth_service
pip install -r requirements.txt
```

### Chạy toàn bộ test suite

```bash
cd services/auth_service
pytest
```

### Chạy từng file test riêng

```bash
pytest tests/test_models.py       # chỉ test models
pytest tests/test_serializers.py  # chỉ test serializers
pytest tests/test_views.py        # chỉ test views/endpoints
```

### Chạy một test class hoặc test cụ thể

```bash
pytest tests/test_views.py::TestRegisterView              # cả class
pytest tests/test_views.py::TestRegisterView::test_register_returns_201  # 1 test
```

### Xem báo cáo coverage

```bash
pytest                      # in ra terminal với --cov-report=term-missing
# Sau khi chạy, mở htmlcov/index.html để xem báo cáo chi tiết
```

### Kết quả mong đợi

```
78 passed in ~4s

Name                                    Stmts   Miss  Cover
-----------------------------------------------------------
apps/accounts/__init__.py                   0      0   100%
apps/accounts/admin.py                     11      0   100%
apps/accounts/internal_views.py            23      0   100%
apps/accounts/models.py                    31      0   100%
apps/accounts/serializers.py               41      0   100%
apps/accounts/views.py                     30      0   100%
-----------------------------------------------------------
TOTAL                                     152      0   100%

Required test coverage of 80% reached. Total coverage: 100.00%
```

### Kiểm tra code style với Ruff

```bash
ruff check .            # kiểm tra lỗi
ruff check --fix .      # tự động sửa các lỗi có thể fix
ruff format .           # format code
```

Ruff được cấu hình kiểm tra: PEP8 errors/warnings, imports (isort), bugbear, pyupgrade, pep8-naming.

---

## API Reference

Base URL qua Gateway: `http://localhost:8000`

### Auth Service

| Method | Endpoint | Auth | Mô tả |
|---|---|---|---|
| POST | `/api/v1/auth/register/` | Public | Đăng ký tài khoản mới |
| POST | `/api/v1/auth/token/` | Public | Đăng nhập → trả về access + refresh token |
| POST | `/api/v1/auth/token/refresh/` | Public | Làm mới access token |
| POST | `/api/v1/auth/token/blacklist/` | Bearer | Đăng xuất (blacklist refresh token) |
| GET/PATCH | `/api/v1/auth/profile/` | Bearer | Xem và cập nhật thông tin cá nhân |
| POST | `/api/v1/auth/change-password/` | Bearer | Đổi mật khẩu |

### Product Service

| Method | Endpoint | Auth | Mô tả |
|---|---|---|---|
| GET | `/api/v1/products/` | Public | Danh sách sản phẩm (filter, search, phân trang) |
| GET | `/api/v1/products/{slug}/` | Public | Chi tiết sản phẩm |
| POST / PATCH / DELETE | `/api/v1/products/` | Admin | CRUD sản phẩm |
| GET | `/api/v1/products/categories/` | Public | Cây danh mục |
| GET | `/api/v1/products/low-stock/` | Admin | Sản phẩm sắp hết hàng |

**Query params:** `min_price`, `max_price`, `category`, `in_stock`, `search`, `ordering`

### Cart Service

| Method | Endpoint | Auth | Mô tả |
|---|---|---|---|
| GET | `/api/v1/cart/` | Bearer | Xem giỏ hàng (kèm thông tin sản phẩm từ product_service) |
| POST | `/api/v1/cart/items/` | Bearer | Thêm sản phẩm vào giỏ |
| PATCH | `/api/v1/cart/items/{id}/` | Bearer | Cập nhật số lượng |
| DELETE | `/api/v1/cart/items/{id}/` | Bearer | Xoá một item khỏi giỏ |
| DELETE | `/api/v1/cart/clear/` | Bearer | Xoá toàn bộ giỏ hàng |

### Order Service

| Method | Endpoint | Auth | Mô tả |
|---|---|---|---|
| GET | `/api/v1/orders/` | Bearer | Danh sách đơn hàng của tôi |
| POST | `/api/v1/orders/` | Bearer | Checkout — tạo đơn hàng từ giỏ |
| GET | `/api/v1/orders/{id}/` | Bearer | Chi tiết một đơn hàng |
| PATCH | `/api/v1/orders/{id}/cancel/` | Bearer | Huỷ đơn hàng |
| GET | `/api/v1/orders/admin/` | Admin | Tất cả đơn hàng (quản trị) |
| PATCH | `/api/v1/orders/admin/{id}/status/` | Admin | Cập nhật trạng thái đơn hàng |

---

## Luồng Checkout (cross-service)

```
Client
  │
  └─► POST /api/v1/orders/
            │
            │  order_service nhận request
            │
            ├─► 1. GET  /internal/cart/{user_id}/             ──► cart_service
            │          Lấy danh sách items trong giỏ
            │
            ├─► 2. GET  /internal/products/{id}/  (x N items) ──► product_service
            │          Xác minh giá và tồn kho từng sản phẩm
            │
            ├─► 3. Tạo Order + OrderItems trong order_db
            │          (snapshot name/price tại thời điểm checkout)
            │
            ├─► 4. POST /internal/products/{id}/decrement-stock/ (x N) ──► product_service
            │          Trừ số lượng tồn kho
            │
            ├─► 5. DELETE /internal/cart/{user_id}/clear/     ──► cart_service
            │          Xoá giỏ hàng sau khi checkout
            │
            └─► 6. Signal post_save → Celery task → gửi email xác nhận đơn hàng
```

---

## Ví dụ curl — Checkout hoàn chỉnh

```bash
# 1. Đăng ký
curl -s -X POST http://localhost:8000/api/v1/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"email":"user@test.com","full_name":"Test User","password":"Test@1234","password_confirm":"Test@1234"}'

# 2. Đăng nhập — lấy token
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"email":"user@test.com","password":"Test@1234"}' \
  | python -c "import sys,json; print(json.load(sys.stdin)['access'])")

echo "Token: $TOKEN"

# 3. Thêm sản phẩm vào giỏ
curl -s -X POST http://localhost:8000/api/v1/cart/items/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"product_id":1,"quantity":2}'

# 4. Xem giỏ hàng
curl -s http://localhost:8000/api/v1/cart/ \
  -H "Authorization: Bearer $TOKEN"

# 5. Checkout — tạo đơn hàng
curl -s -X POST http://localhost:8000/api/v1/orders/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"shipping_name":"Test User","shipping_phone":"0901234567","shipping_address":"123 Main St"}'

# 6. Xem danh sách đơn hàng
curl -s http://localhost:8000/api/v1/orders/ \
  -H "Authorization: Bearer $TOKEN"
```
