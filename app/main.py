import os
import sys
import logging
import time
from datetime import datetime, timezone
from flask import Flask, jsonify, request

# --- logging setup ---
log_dir = "/app/logs"
os.makedirs(log_dir, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),                          # stdout (docker logs)
        logging.FileHandler(f"{log_dir}/app.log"),        # persisted volume
    ],
)
logger = logging.getLogger(__name__)

# --- config: zero trust, no defaults, crash early ---
_REQUIRED = ["APP_NAME", "APP_ENV", "APP_PORT"]
_missing  = [key for key in _REQUIRED if not os.getenv(key)]

if _missing:
    logger.critical(f"Missing required env vars: {', '.join(_missing)}")
    logger.critical("Set them in .env — see .env.example")
    sys.exit(1)

APP_NAME = os.environ["APP_NAME"]
APP_ENV  = os.environ["APP_ENV"]

try:
    APP_PORT = int(os.environ["APP_PORT"])
except ValueError:
    logger.critical(f"APP_PORT must be an integer, got: '{os.environ['APP_PORT']}'")
    sys.exit(1)

# --- app setup ---
app = Flask(__name__)

START_TIME = time.time()


@app.before_request
def log_request():
    logger.info(f"{request.method} {request.path} — from {request.remote_addr}")


@app.route("/")
def index():
    return jsonify({
        "app":     APP_NAME,
        "env":     APP_ENV,
        "message": "Hello from Docker 🐳",
        "time":    datetime.now(timezone.utc).isoformat(),
    })


@app.route("/health")
def health():
    uptime_seconds = round(time.time() - START_TIME)
    return jsonify({
        "status":  "ok",
        "uptime":  f"{uptime_seconds}s",
        "env":     APP_ENV,
    })


@app.route("/info")
def info():
    return jsonify({
        "app":     APP_NAME,
        "env":     APP_ENV,
        "port":    APP_PORT,
        "python":  os.popen("python --version").read().strip(),
        "host":    os.uname().nodename,        # container hostname
    })


if __name__ == "__main__":
    logger.info(f"Starting {APP_NAME} on port {APP_PORT} [{APP_ENV}]")
    app.run(host="0.0.0.0", port=APP_PORT)