# Lean serving image: python:3.11-slim + requirements-serve.txt only (no MLflow, pytest, Jupyter).
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PORT=8000

WORKDIR /app

# Install dependencies first so this layer is cached between code changes.
COPY requirements-serve.txt .
RUN pip install --no-cache-dir -r requirements-serve.txt

# Only what the API needs at runtime.
COPY app.py features.py ./
COPY model/ model/
COPY static/ static/

# Run as a non-root user; logs/ holds the prediction log for drift checks.
RUN useradd --create-home appuser && mkdir -p logs && chown -R appuser /app
USER appuser

EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request,os; urllib.request.urlopen(f'http://localhost:{os.environ.get(\"PORT\",\"8000\")}/health')" || exit 1

# PORT defaults to 8000; hosts like Render/Railway inject their own.
CMD ["sh", "-c", "uvicorn app:app --host 0.0.0.0 --port ${PORT}"]
