# Sentinel Docker Container - Engineer #4 Security
# Multi-stage build for minimal footprint

# Stage 1: Builder
FROM python:3.11-slim as builder

WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    wget \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python packages
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim

# Security: Non-root user
RUN useradd -m -u 1000 -s /bin/bash sentinel

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    curl \
    jq \
    && rm -rf /var/lib/apt/lists/*

# Copy Python packages from builder
COPY --from=builder /root/.local /home/sentinel/.local

# Set up Sentinel workspace
WORKDIR /home/sentinel/sentinel

# Copy Sentinel files
COPY --chown=sentinel:sentinel skills/ ./skills/
COPY --chown=sentinel:sentinel config/ ./config/
COPY --chown=sentinel:sentinel workflows/ ./workflows/
COPY --chown=sentinel:sentinel scripts/ ./scripts/

# Create necessary directories
RUN mkdir -p /data/captures /data/logs /data/models \
    && chown -R sentinel:sentinel /data

# Environment variables
ENV PATH="/home/sentinel/.local/bin:$PATH" \
    PYTHONPATH="/home/sentinel/sentinel" \
    SENTINEL_HOME="/home/sentinel/sentinel"

# Security: Drop privileges
USER sentinel

# Health check
HEALTHCHECK --interval=60s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:11434/api/tags || exit 1

# Expose ports (none needed for local operation)
# EXPOSE 8080

# Run Sentinel
CMD ["/home/sentinel/sentinel/scripts/run_sentinel.sh"]
