FROM python:3.12-slim

WORKDIR /app

# Dependências do sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    python3-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements
COPY requirements.txt ./

# Instalar dependências Python
RUN pip install --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# Copiar código-fonte
COPY main.py smart_analysis.py report_generator.py ai_explainer.py temp_validator.py history_manager.py nvme_support.py pdf_generator.py enterprise_monitor.py prometheus_exporter.py cmdb_api.py benchmark_database.py ./
COPY .env* ./

# Variáveis de ambiente
ENV APP_ENV=production
ENV HOST=0.0.0.0
ENV PORT=8000

EXPOSE 8000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Iniciar o backend com Socket.IO support
CMD ["uvicorn", "main:socket_app", "--host", "0.0.0.0", "--port", "8000"]
