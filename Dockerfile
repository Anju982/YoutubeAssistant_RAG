# Hugging Face Space (SDK: Docker) for YouTube Assistant RAG
# Runs FastAPI backend and Streamlit frontend in one container

FROM python:3.11-slim

# Prevent Python from buffering stdout/stderr
ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    FASTAPI_HOST=127.0.0.1 \
    FASTAPI_PORT=8001

WORKDIR /app

# System deps (minimal)
RUN apt-get update -y && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency file and install first for better caching
COPY requirements.txt ./
RUN python -m pip install --upgrade pip && \
    pip install -r requirements.txt

# Copy application code
COPY . .

# Expose the frontend port (HF will set $PORT; default to 7860)
EXPOSE 7860

# Make start script executable
RUN chmod +x ./start_space.sh || true

# Default command starts both backend (uvicorn) and frontend (Streamlit)
CMD ["./start_space.sh"]
