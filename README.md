# Project 1 — Dockerize a Simple App

> **Goal:** containerize a Python Flask API the right way — multi-stage build,
> non-root user, env vars, port mapping, and persisted logs via a Docker volume.

---

## What I built

A small REST API with three endpoints:

| Endpoint  | What it returns                                  |
|-----------|--------------------------------------------------|
| `GET /`   | App name, env, greeting, UTC timestamp           |
| `GET /health` | Status + uptime (used by Docker healthcheck) |
| `GET /info`   | App metadata + container hostname           |

Nothing fancy by design — the point is **how** it's packaged, not what it does.

---

## Key concepts demonstrated

### Multi-stage Dockerfile
```
Stage 1 (builder)  →  installs dependencies into /deps
Stage 2 (runtime)  →  copies only /deps + source, no pip, no cache
```
Result: the final image is lean (~130 MB vs ~400 MB single-stage).

### Non-root user
The container runs as `appuser`, not `root`. Standard security baseline.

### Environment variables
Config lives in `.env` (gitignored). `.env.example` documents what's needed.
At runtime: `docker compose` picks up `.env` automatically.

### Port mapping
```
host:5000  →  container:5000
```
Controlled via `APP_PORT` in `.env` — change the host port without touching the image.

### Persisted logs (Docker volume)
```
app-logs volume  →  mounted at /app/logs inside the container
```
Logs survive `docker compose down` and restarts. Inspect with:
```bash
docker compose logs -f app
# or read the file directly:
docker exec portfolio-app cat /app/logs/app.log
```

### Health check
Docker polls `GET /health` every 30s. If it fails 3× the container is marked
`unhealthy` — visible in `docker ps` and usable by orchestrators (Compose,
Swarm, etc.).

---

## How to run

```bash
# 1. clone & enter
git clone https://github.com/<your-username>/devops-portfolio.git
cd devops-portfolio/01-docker-fundamentals

# 2. set up env
cp .env.example .env          # edit APP_ENV=development if you want

# 3. build & start
docker compose up --build

# 4. test the endpoints
curl http://localhost:5000/
curl http://localhost:5000/health
curl http://localhost:5000/info

# 5. check container health status
docker ps                     # look for (healthy) in STATUS column

# 6. tail logs
docker compose logs -f app

# 7. stop & clean up
docker compose down           # keeps the volume (logs preserved)
docker compose down -v        # removes volume too
```

### Without Compose (raw Docker)
```bash
docker build -t portfolio-app .
docker run -d \
  --name portfolio-app \
  -p 5000:5000 \
  -e APP_ENV=development \
  -v app-logs:/app/logs \
  portfolio-app
```

---

## Project structure

```
01-docker-fundamentals/
├── app/
│   ├── main.py              # Flask application
│   └── requirements.txt     # pinned dependencies
├── Dockerfile               # multi-stage build
├── docker-compose.yml       # volume + env_file + healthcheck
├── .env.example             # template — copy to .env
├── .gitignore
└── README.md
```

---

## What I learned

- Multi-stage builds keep images small and avoid shipping build tools to prod
- Running as non-root is a free security win that every container should do
- Docker volumes outlive containers — critical for anything stateful (logs, DBs)
- Health checks turn Docker from "run and forget" into "run and monitor"
- `.env.example` in git + `.env` in `.gitignore` is the right pattern for secrets

## 👤 Author

**[Agung Perdana]**
QA Engineer | Manual & Automation Testing

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-0077B5?style=flat-square&logo=linkedin)](https://linkedin.com/in/agung-perdana-it)
[![GitHub](https://img.shields.io/badge/GitHub-Follow-181717?style=flat-square&logo=github)](https://github.com/AgungPerdana-IT)

---