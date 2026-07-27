backend/
├── alembic/ # Thư mục chứa các file migration sinh ra bởi Alembic
├── app/ # 🚀 Toàn bộ mã nguồn của ứng dụng
│ ├── **init**.py
│ ├── main.py # Khởi tạo FastAPI app, lifespan, CORS, middleware, routers
│ ├── api/ # Tầng API (Controllers/Routers)
│ │ ├── dependencies/ # Các dependency dùng chung
│ │ │ ├── auth.py # get_current_user, check token
│ │ │ └── permissions.py # RBAC logic (check role ADMIN, OWNER, EDITOR)
│ │ └── v1/
│ │ ├── router.py # File tổng hợp tất cả các router v1
│ │ └── endpoints/ # Các endpoints thực tế theo tài liệu
│ │ ├── auth.py # Register, Login, Refresh, Logout
│ │ ├── users.py # Get/Update profile
│ │ ├── workspaces.py # CRUD workspaces, members
│ │ ├── projects.py # CRUD projects
│ │ └── tasks.py # CRUD tasks, comments, labels
│ │
│ ├── core/ # Cấu hình cốt lõi
│ │ ├── config.py # Load cấu hình từ .env bằng pydantic-settings
│ │ ├── security.py # Hashing password (passlib/bcrypt), gen JWT
│ │ ├── exceptions.py # Custom HTTP Exceptions & Exception Handlers
│ │ ├── logger.py # Cấu hình logging hệ thống
│ │ └── redis.py # Cấu hình kết nối và dependency cho Redis cache
│ │
│ ├── models/ # SQLAlchemy 2.x Models (Database Schema)
│ │ ├── base.py # DeclarativeBase của SQLAlchemy
│ │ ├── user.py # users
│ │ ├── workspace.py # workspaces, workspace_members
│ │ ├── project.py # projects
│ │ └── task.py # tasks, labels, task_labels, comments
│ │
│ ├── schemas/ # Pydantic v2 Models (Data Validation)
│ │ ├── user.py # UserCreate, UserResponse, ...
│ │ ├── workspace.py
│ │ ├── project.py
│ │ ├── task.py
│ │ ├── auth.py # TokenRequest, TokenResponse
│ │ └── common.py # PaginatedResponse (cho phân trang)
│ │
│ ├── repositories/ # Tầng truy xuất dữ liệu (Data Access Layer)
│ │ ├── base.py # BaseRepository[T] (Async CRUD, Pagination)
│ │ ├── user_repo.py # Kế thừa BaseRepository, thêm các query riêng
│ │ ├── workspace_repo.py
│ │ ├── project_repo.py
│ │ └── task_repo.py
│ │
│ ├── services/ # Tầng nghiệp vụ (Business Logic)
│ │ ├── auth_service.py # Logic đăng nhập, cấp/thu hồi token
│ │ ├── workspace_service.py# Logic mời member, phân quyền, check ownership
│ │ ├── task_service.py # Logic gán task, chuyển status, assign label
│ │ └── cache_service.py # Các hàm tiện ích thao tác với Redis cache
│ │
│ ├── db/ # Quản lý kết nối Database
│ │ └── session.py # SQLAlchemy async_engine, async_sessionmaker
│ │
│ └── background/ # Background tasks / Queue worker (Tùy chọn)
│ └── email_worker.py # Hàm gửi email thông báo khi được assign task
│
├── tests/ # Thư mục Unit Test và Integration Test
│ ├── conftest.py # Fixtures cho DB test, client test
│ ├── api/ # Test các API endpoints
│ └── services/ # Test business logic độc lập với DB
│
├── .env # Chứa các biến môi trường thực tế (Bảo mật, không commit)
├── .env.example # Template biến môi trường
├── alembic.ini # Cấu hình đường dẫn DB cho Alembic
├── docker-compose.yml # Setup App + MySQL/PostgreSQL + Redis
├── Dockerfile # Multi-stage build cho FastAPI
├── pyproject.toml # Quản lý thư viện (hoặc requirements.txt), config cho Ruff, Mypy
└── README.md # Hướng dẫn setup, env vars, run docker
