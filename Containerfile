# ─────────────────────────────────────────────
# Containerfile
#
# Build : podman build -t geo-api .
# Run   : podman run -p 8000:8000 geo-api
# ─────────────────────────────────────────────

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy dependencies first (layer caching)
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy project code
COPY . .

# Expose FastAPI port
EXPOSE 8000

# Start the API
CMD ["python", "api.py"]
