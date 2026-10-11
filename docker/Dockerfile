# Multi-stage Docker build for Z.Dip Sovereign Engine
FROM python:3.12-slim-bookworm

LABEL maintainer="mayankreseracher"
LABEL description="Z.Dip: Video extraction from torrents and 200+ platforms directly to cloud storage"

ENV PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive \
    ZDIP_HOST="0.0.0.0" \
    ZDIP_PORT=8088

# Install system dependencies (ffmpeg, aria2, tor, curl, ca-certificates)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    aria2 \
    tor \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy Z.Dip package and source
COPY zdip/ /app/zdip/
COPY pyproject.toml .
RUN pip install --no-cache-dir -e .

# Create persistent mount points
RUN mkdir -p /app/downloads /app/config /app/bin

EXPOSE 8088 9050

# Default launcher starts Z.Dip Web Dashboard & REST API
CMD ["zdip", "serve", "--host", "0.0.0.0", "--port", "8088"]
