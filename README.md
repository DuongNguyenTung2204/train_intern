# Blog API

FastAPI + PostgreSQL REST API cho blog với authentication và authorization.

## Yêu cầu

- Docker
- Docker Compose

## Chạy project

```bash
# 1. Khởi động container
docker-compose up -d

# 2. Chạy migration và tạo dữ liệu mẫu
docker-compose run --rm web alembic upgrade head
```

Sau khi chạy xong, API có sẵn tại `http://localhost:8000`

## Tài khoản mặc định

- **Email:** admin@example.com
- **Password:** admin123

## API Endpoints

### Authentication

| Method | Endpoint | Mô tả |
|--------|----------|-------|
| POST | `/auth/register` | Đăng ký user |
| POST | `/auth/login` | Đăng nhập |
| POST | `/auth/change-password` | Đổi mật khẩu (cần login) |

### Users (Admin only)

| Method | Endpoint | Mô tả |
|--------|----------|-------|
| GET | `/auth/users` | Danh sách users |
| GET | `/auth/users/{user_id}` | Chi tiết user |
| DELETE | `/auth/users/{user_id}` | Xóa user theo id |
| DELETE | `/auth/users/email/{email}` | Xóa user theo email |

### Posts

| Method | Endpoint | Mô tả |
|--------|----------|-------|
| GET | `/posts/` | Danh sách posts |
| GET | `/posts/user/{user_id}` | Posts của user |
| GET | `/posts/{post_id}` | Chi tiết post |
| POST | `/posts/` | Tạo post (cần login) |
| PUT | `/posts/{post_id}` | Sửa post (chủ post hoặc admin) |
| DELETE | `/posts/{post_id}` | Xóa post (admin only) |

### Comments

| Method | Endpoint | Mô tả |
|--------|----------|-------|
| GET | `/posts/{post_id}/comments/` | Comments của post |
| POST | `/posts/{post_id}/comments/` | Tạo comment (cần login) |
| PUT | `/posts/{post_id}/comments/{comment_id}` | Sửa comment |
| DELETE | `/posts/{post_id}/comments/{comment_id}` | Xóa comment |

## Roles

- **user**: User thường
- **admin**: Quản trị viên

## API Documentation

Swagger UI: `http://localhost:8000/docs`

## Dừng container

```bash
docker-compose down
```
