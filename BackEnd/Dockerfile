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
    gosu \
    && rm -rf /var/lib/apt/lists/*

# Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Non-root user (will be used at runtime via entrypoint)
RUN useradd -m appuser && chown -R appuser:appuser /app

# App code
COPY . .

# Runtime dirs
RUN mkdir -p /app/media /app/static /app/celery_data /app/celery_beat_data /app/logs

# Entrypoint com gosu para dropar privilégios sem senha
COPY entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

# Necessário root para ajustar permissões em runtime antes de dropar privilégios
USER root

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "core.asgi:application"]
