FROM python:3.12-slim

WORKDIR /app

ENV PYTHONPATH=/app

# Cài uv
RUN pip install uv

# Copy file dependency
COPY pyproject.toml uv.lock* ./

# Cài dependency
RUN uv sync --frozen

# Copy source code
COPY . .

EXPOSE 8000

# Chạy ứng dụng
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]