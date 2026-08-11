# --- Stage 1: Base Image ---
    FROM python:3.11-slim-trixie AS base
    RUN apt-get update \
        && apt-get upgrade -y \
        && rm -rf /var/lib/apt/lists/*
    ENV PYTHONUNBUFFERED=1 \
        PYTHONDONTWRITEBYTECODE=1 \
        PIP_NO_CACHE_DIR=1 \
        PIP_DISABLE_PIP_VERSION_CHECK=1
    RUN groupadd -r appuser \
        && useradd --no-log-init -r -m -d /home/appuser -g appuser appuser
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
    # Keep the production runtime minimal. Health checks use Python's standard
    # library, so no compiler or curl packages are installed in this stage.
    # The 'wait-for-it.sh' script and its dependencies are no longer needed
    COPY ./p2p-backend-app/requirements.txt ./
    RUN pip install -r requirements.txt \
        && python -m pip uninstall -y pip setuptools wheel
    COPY ./p2p-backend-app/ .
    RUN mkdir -p logs && chown appuser:appuser logs
    USER appuser
    EXPOSE 8000
    CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]