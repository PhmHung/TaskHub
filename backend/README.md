# TaskHub API

Backend API cho hệ thống quản lý công việc **TaskHub**, được xây dựng bằng **FastAPI**, **SQLAlchemy 2.0** (với AsyncIO) và **MySQL**.

## Tính năng

- Xác thực người dùng bằng JWT (Access Token & Refresh Token).
- Quản lý người dùng (đăng ký, đăng nhập, cập nhật thông tin).
- API được bảo vệ và tài liệu hóa bằng Swagger UI.
- Kiến trúc module hóa, dễ dàng mở rộng.
- SQLAlchemy 2.0 với Async Engine.
- Quản lý database migration bằng Alembic.
- Triển khai bằng Docker và Docker Compose.
- Quản lý dependency bằng **uv**.

---

# Cấu trúc Project

```text
.
├── alembic/                # Migration của Alembic
├── app/
│   ├── api/                # API routers và dependencies
│   ├── core/               # Config, JWT, Security
│   ├── db/                 # Database session và Base
│   ├── enums/
│   ├── middlewares/
│   ├── models/             # SQLAlchemy Models
│   ├── repositories/       # Repository Pattern
│   ├── schemas/            # Pydantic Schemas
│   ├── services/           # Business Logic
│   └── main.py             # Entry point
├── tests/
├── .env.example
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
├── uv.lock
└── README.md
```

---

# Yêu cầu

- Python 3.12 trở lên
- uv
- Docker & Docker Compose

---

# Chạy Local

## 1. Clone project

```bash
git clone <your-repository-url>
cd TaskHub/backend
```

---

## 2. Tạo file môi trường

```bash
cp .env.example .env
```

Cập nhật các biến môi trường nếu cần.

---

## 3. Cài đặt Dependencies

```bash
uv sync
```

Lệnh này sẽ:

- tạo virtual environment `.venv`
- cài đặt toàn bộ dependency từ `uv.lock`

---

## 4. Chạy Database Migration

Đảm bảo MySQL đã chạy và `DATABASE_URL` trong `.env` chính xác.

```bash
uv run alembic upgrade head
```

---

## 5. Chạy Ứng dụng (Development Mode)

```bash
uv run uvicorn app.main:app --reload
```

Ứng dụng sẽ chạy tại

```
http://127.0.0.1:8000
```

Swagger UI

```
http://127.0.0.1:8000/docs
```

ReDoc

```
http://127.0.0.1:8000/redoc
```

---

# Chạy với Docker Compose

## 1. Tạo file môi trường

```bash
cp .env.example .env.docker
```

---

## 2. Khởi động

```bash
docker compose --env-file .env.docker up -d --build
```

Docker sẽ tự động:

- Build image
- Khởi động MySQL
- Chờ MySQL sẵn sàng
- Chạy Alembic Migration
- Khởi động FastAPI

Ứng dụng sẽ chạy tại

```
http://localhost:8000
```

---

# Biến môi trường

| Biến                        | Mô tả                        | Ví dụ                                     |
| --------------------------- | ---------------------------- | ----------------------------------------- |
| APP_PORT                    | Port của FastAPI             | 8000                                      |
| DATABASE_URL                | Chuỗi kết nối MySQL          | mysql+asyncmy://root:1234@db:3306/taskhub |
| MYSQL_ROOT_PASSWORD         | Mật khẩu root của MySQL      | 1234                                      |
| MYSQL_DATABASE              | Tên database                 | taskhub                                   |
| MYSQL_PORT                  | Port MySQL trên host         | 3307                                      |
| SECRET_KEY                  | Secret dùng để ký JWT        | taskhub-fastapi                           |
| ALGORITHM                   | Thuật toán JWT               | HS256                                     |
| ACCESS_TOKEN_EXPIRE_MINUTES | Thời gian sống Access Token  | 30                                        |
| REFRESH_TOKEN_EXPIRE_DAYS   | Thời gian sống Refresh Token | 7                                         |

---

# Migration

Tạo migration mới

```bash
uv run alembic revision --autogenerate -m "create attachment table"
```

Áp dụng migration

```bash
uv run alembic upgrade head
```

Rollback một phiên bản

```bash
uv run alembic downgrade -1
```

Xem lịch sử migration

```bash
uv run alembic history
```

---

# Công nghệ sử dụng

- FastAPI
- SQLAlchemy 2.0
- Alembic
- MySQL 8
- Pydantic v2
- JWT Authentication
- Docker
- Docker Compose
- uv
