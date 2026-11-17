FROM python:3.11-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    BLENDER_EXECUTABLE=/usr/bin/blender \
    HOME=/tmp

RUN apt-get update && apt-get install -y --no-install-recommends \
    blender libgl1 libxi6 libxrender1 libxkbcommon0 libsm6 libxext6 ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt ./
RUN python -m pip install --no-cache-dir -r requirements.txt
COPY . ./
RUN mkdir -p /app/results /app/renders /var/lib/q3 \
    && chown -R 10001:10001 /app/results /app/renders /var/lib/q3
USER 10001:10001
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/api/v1/health', timeout=4)" || exit 1
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
