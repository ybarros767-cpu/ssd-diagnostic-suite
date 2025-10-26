FROM python:3.12-slim

WORKDIR /app

# Install system deps required to build some Python packages (kept minimal)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    python3-dev \
    python3-distutils \
    gfortran \
    libatlas-base-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt ./
# Make sure pip, setuptools and wheel are recent to satisfy build backends
RUN pip install --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# Copy app source
COPY . /app

ENV PYTHONUNBUFFERED=1
ENV PORT=8000

EXPOSE 8000

# Use uvicorn to run the FastAPI app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
