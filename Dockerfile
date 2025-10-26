FROM python:3.12-slim

WORKDIR /app

# Dependências do sistema para compilar numpy e libs Python
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    python3-dev \
    python3-setuptools \
    python3-pip \
    gfortran \
    libopenblas-dev \
    liblapack-dev \
    libblas-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiar dependências Python
COPY requirements.txt ./
RUN pip install --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# Copiar código-fonte
COPY . .

# Variáveis de ambiente padrão
ENV APP_ENV=production
ENV HOST=0.0.0.0
ENV PORT=8000

EXPOSE 8000

# Iniciar o backend
CMD ["uvicorn", "ssd-diagnostic-suite.backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
