#!/usr/bin/env bash
set -e

echo "╔═══════════════════════════════════════════════════════════════════════╗"
echo "║         🚀 DEPLOY FINAL - SSD DIAGNOSTIC SUITE                        ║"
echo "╚═══════════════════════════════════════════════════════════════════════╝"
echo ""

cd "$(dirname "$0")"

# 1. Verificar se .env existe
if [ ! -f ssd-diagnostic-suite/backend/.env ]; then
    echo "⚠️  Arquivo .env não encontrado!"
    echo "📝 Criando .env a partir do template..."
    cp ssd-diagnostic-suite/backend/.env.template ssd-diagnostic-suite/backend/.env
    echo "✅ Arquivo .env criado. Configure sua API key da OpenAI!"
fi

# 2. Parar containers existentes
echo "🛑 Parando containers existentes..."
sudo docker compose -f config/docker/docker-compose.yml down 2>/dev/null || true

# 3. Rebuild frontend
echo "🔧 Reconstruindo frontend..."
cd ssd-diagnostic-suite && npm run build && cd ..

# 4. Copiar build para dist
echo "📦 Copiando build para dist..."
mkdir -p dist
cp -r ssd-diagnostic-suite/build-output/* dist/

# 5. Ajustar configurações
echo "⚙️  Ajustando configurações..."
cp config/docker/docker-compose.yml docker-compose.yml
cp config/nginx/nginx.conf nginx.conf

# 6. Build e deploy
echo "🏗️  Construindo containers..."
sudo docker compose build --no-cache backend
sudo docker compose up -d

# 7. Aguardar inicialização
echo "⏳ Aguardando inicialização..."
sleep 10

# 8. Verificar status
echo "📊 Verificando status..."
sudo docker ps

echo ""
echo "✅ Deploy concluído!"
echo ""
echo "🌐 Acesse: http://localhost:8080"
echo ""

