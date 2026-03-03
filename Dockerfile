# Dockerfile for Promtior RAG Backend

FROM python:3.10 AS backend
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set Python env variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

# Copy backend
COPY backend/pyproject.toml .

# 1. Actualizar pip
RUN pip install --upgrade pip

# 2. Instalar la versión CPU de PyTorch (reduce el peso de 4GB a ~200MB)
RUN pip install torch --index-url https://download.pytorch.org/whl/cpu

# 3. Instalar las dependencias de la aplicación
RUN pip install -e .

# Copy application code
COPY backend/src ./src
COPY backend/data ./data

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/health || exit 1

# Start backend API
CMD ["python", "-m", "uvicorn", "src.api.app:app", "--host", "0.0.0.0", "--port", "8000"]
