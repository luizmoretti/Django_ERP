#!/bin/sh
set -e

# Fix ownership of the entire /app directory to prevent permission issues
# This covers static, media, logs, celerybeat-schedule, and any other files
chown -R appuser:appuser /app || true

# Ensure proper permissions for directories and files
find /app -type d -exec chmod 755 {} \; 2>/dev/null || true
find /app -type f -exec chmod 644 {} \; 2>/dev/null || true

# Make sure manage.py remains executable
if [ -f "/app/manage.py" ]; then
  chmod 755 /app/manage.py || true
fi

# Drop privileges and run the provided command as appuser
exec gosu appuser "$@"


