FROM node:20-slim AS builder
WORKDIR /build/frontend
COPY frontend/ .
RUN npm ci && npm run build

FROM python:3.12-slim
WORKDIR /app
COPY pyproject.toml .
RUN pip install --no-cache-dir -e .
COPY backend/ backend/
COPY alembic/ alembic/
COPY alembic.ini .
COPY --from=builder /build/frontend/dist frontend/dist
EXPOSE 8000
CMD ["uvicorn", "backend.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
