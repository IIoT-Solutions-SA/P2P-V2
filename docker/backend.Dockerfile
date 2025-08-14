# --- Stage 1: Base Image ---
    FROM python:3.11-slim AS base
    ENV PYTHONUNBUFFERED=1 \
        PYTHONDONTWRITEBYTECODE=1 \
        PIP_NO_CACHE_DIR=1 \
        PIP_DISABLE_PIP_VERSION_CHECK=1
    RUN groupadd -r appuser && useradd --no-log-init -r -g appuser appuser
    WORKDIR /app
    
    # --- Stage 2: Development Image ---
    FROM base AS development
    # 'netcat-openbsd' is no longer needed
    RUN apt-get update && apt-get install -y gcc curl && rm -rf /var/lib/apt/lists/*
    # The 'wait-for-it.sh' script is no longer needed
    COPY ./p2p-backend-app/requirements.txt ./
    RUN pip install -r requirements.txt
    COPY ./p2p-backend-app/ .
    RUN mkdir -p logs && chown appuser:appuser logs
    USER appuser
    EXPOSE 8000
    CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
    
    # --- Stage 3: Production Image ---
    FROM base AS production
    # The 'wait-for-it.sh' script and its dependencies are no longer needed
    COPY ./p2p-backend-app/requirements.txt ./
    RUN pip install -r requirements.txt
    COPY ./p2p-backend-app/ .
    RUN mkdir -p logs && chown appuser:appuser logs
    USER appuser
    EXPOSE 8000
    CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]