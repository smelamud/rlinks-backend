# syntax=docker/dockerfile:1
FROM python:3.13-slim

# Environment
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    VIRTUAL_ENV=/opt/venv \
    PATH="/opt/venv/bin:$PATH"

# Create and prepare virtual environment
RUN python -m venv $VIRTUAL_ENV && \
    pip install --upgrade pip setuptools wheel

# Workdir
WORKDIR /app

# Install project dependencies from pyproject.toml
COPY pyproject.toml ./
RUN pip install --no-build-isolation .

# Copy application source
COPY . .

# Use an unprivileged user
RUN useradd -m -u 10001 appuser && chown -R appuser:appuser /app
USER appuser

# Expose HTTP port
EXPOSE 8000

# Basic healthcheck against the root endpoint
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/').read()" || exit 1

# Start the server
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
