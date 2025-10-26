#!/usr/bin/env bash
set -e

echo "=== SSD Diagnostic Suite - Instalação Completa ==="

# Verificar se .env existe
if [ ! -f .env ]; then
  echo "📝 Criando .env padrão..."
  cat > .env <<EOT
APP_ENV=production
ALLOWED_ORIGINS=http://localhost:8080,http://localhost:3000
HOST=0.0.0.0
PORT=8000
APP_VERSION=1.0.0
EOT
fi

# Build do frontend (React/Vite)
if [ -d ssd-diagnostic-suite/src ]; then
  echo "🔧 Construindo o frontend..."
  cd ssd-diagnostic-suite
  
  # Instalar dependências se node_modules não existir
  if [ ! -d node_modules ]; then
    echo "📦 Instalando dependências do frontend..."
    npm install
  fi
  
  # Build
  npm run build
  
  cd ..
  
  echo "📦 Copiando dist/ para o nginx..."
  rm -rf dist
  mv ssd-diagnostic-suite/dist ./dist
fi

# Docker backend + nginx
echo "🐳 Construindo containers..."
docker compose down --remove-orphans || true
docker compose build

echo "🚀 Subindo stack..."
docker compose up -d

echo ""
echo "✅ Instalação concluída!"
echo "📍 Backend API: http://localhost:8000/docs"
echo "📍 Healthcheck: http://localhost:8000/health"
echo "📍 Frontend (painel): http://localhost:8080"
echo ""
echo "Para ver os logs:"
echo "  docker logs -f ssd_backend"
echo "  docker logs -f ssd_nginx"

