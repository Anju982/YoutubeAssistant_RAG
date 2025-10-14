#!/usr/bin/env bash
set -euo pipefail

# Ports
export PORT="${PORT:-7860}"
export FASTAPI_HOST="${FASTAPI_HOST:-127.0.0.1}"
export FASTAPI_PORT="${FASTAPI_PORT:-8001}"

echo "[startup] FASTAPI -> http://${FASTAPI_HOST}:${FASTAPI_PORT}"
echo "[startup] STREAMLIT -> http://0.0.0.0:${PORT}"

# Start FastAPI backend (background)
python -m uvicorn api:app --host 0.0.0.0 --port "${FASTAPI_PORT}" --log-level info &
BACKEND_PID=$!

# Simple health wait (max ~20s)
for i in {1..20}; do
  if curl -sf "http://127.0.0.1:${FASTAPI_PORT}/health" >/dev/null; then
    echo "[startup] Backend healthy."
    break
  fi
  echo "[startup] Waiting for backend... (${i})"
  sleep 1
done

# Start Streamlit frontend (foreground to keep container alive)
exec streamlit run frontend_api.py \
  --server.address 0.0.0.0 \
  --server.port "${PORT}"
