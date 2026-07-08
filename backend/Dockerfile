FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

ARG INSTALL_PADDLE=false

RUN apt-get update \
    && apt-get install -y --no-install-recommends libglib2.0-0 libgomp1 \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements-docker.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt
RUN if [ "$INSTALL_PADDLE" = "true" ]; then \
        pip install --no-cache-dir "paddlepaddle>=3.3.1"; \
    fi

COPY backend/app /app/app

ENV DATABASE_URL=sqlite:////app/data/faceshield.db
ENV DEMO_USERNAME=demo
ENV DEMO_PASSWORD=demo123456
ENV DEMO_DISPLAY_NAME="Demo User"
ENV ACCESS_TOKEN_EXPIRE_SECONDS=604800
ENV CORS_ORIGINS=*
ENV FACESHIELD_ALGORITHM_BACKEND=mock
ENV FACESHIELD_MODEL_NAME=FaceShield-FusionV2
ENV FACESHIELD_MODEL_VERSION=fusion_v2-202607

RUN mkdir -p /app/data /app/storage/uploads /app/storage/reports /app/storage/heatmaps /app/storage/crops

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=5 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/api/mobile/bootstrap', timeout=5).read()"

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
