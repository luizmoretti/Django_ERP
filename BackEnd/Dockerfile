FROM python:3.12-slim

# Environment
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Workdir
WORKDIR /app

# System deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Non-root user
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

# App code
COPY --chown=appuser:appuser . .

# Runtime dirs
RUN mkdir -p /app/media /app/static

# Entrypoint
CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "core.asgi:application"]
