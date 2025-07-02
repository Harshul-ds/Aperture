# -------- Backend Stage --------
FROM python:3.12-slim AS backend

# Install uv (modern pip wrapper) and project deps
RUN pip install --no-cache-dir uv
WORKDIR /app

# Copy project files
COPY pyproject.toml uv.lock ./
RUN uv pip install --system --require-virtualenv=false --no-cache-dir

# Copy source code
COPY backend ./backend
COPY backend/core ./backend/core
COPY backend/api ./backend/api
COPY backend/db ./backend/db
COPY backend/models ./backend/models
COPY chroma_db ./chroma_db

# Expose FastAPI port
EXPOSE 8000

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]


# -------- Development Convenience (optional) --------
# docker build -t aperture-backend .
# docker run -p 8000:8000 aperture-backend
