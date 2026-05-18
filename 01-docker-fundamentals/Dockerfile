# syntax=docker/dockerfile:1

# ── Stage 1: dependency installer ──────────────────────────────────────────
FROM python:3.12-slim AS builder

WORKDIR /install

COPY app/requirements.txt .

# install into a prefix so we can COPY just the libs in the next stage
RUN pip install --prefix=/deps --no-cache-dir -r requirements.txt


# ── Stage 2: final runtime image ───────────────────────────────────────────
FROM python:3.12-slim AS runtime

# don't run as root inside the container
RUN useradd --create-home appuser
USER appuser

WORKDIR /app

# bring in only the installed packages from builder
COPY --from=builder /deps /usr/local

# copy application source
COPY app/ .

# logs will be persisted via a Docker volume
RUN mkdir -p /app/logs

# env vars — real values supplied at runtime via .env or docker run -e
ENV APP_NAME=devops-portfolio-app \
    APP_ENV=production \
    APP_PORT=5000 \
    PYTHONUNBUFFERED=1

EXPOSE 5000

# gunicorn for production; swap to `python main.py` for quick local dev
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--access-logfile", "-", "main:app"]