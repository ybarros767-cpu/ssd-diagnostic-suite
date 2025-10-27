#!/usr/bin/env bash
set -e

echo "╔═══════════════════════════════════════════════════════════════════════╗"
echo "║       🚀 PRODUÇÃO FINAL - SSD DIAGNOSTIC SUITE v1.0.0                ║"
echo "╚═══════════════════════════════════════════════════════════════════════╝"
echo ""

cd "$(dirname "$0")"

# 1. Verificar e criar .env se necessário
if [ ! -f ssd-diagnostic-suite/backend/.env ]; then
    echo "📝 Criando .env a partir do template..."
    cp ssd-diagnostic-suite/backend/.env.template ssd-diagnostic-suite/backend/.env
    echo "⚠️  Configure sua API key da OpenAI em ssd-diagnostic-suite/backend/.env"
fi

# 2. Rebuild frontend
echo "🔧 Reconstruindo frontend..."
cd ssd-diagnostic-suite
npm run build
cd ..

# 3. Copiar build
echo "📦 Copiando build..."
mkdir -p dist ssd-diagnostic-suite/dist
cp -r ssd-diagnostic-suite/build-output/* dist/
cp -r ssd-diagnostic-suite/build-output/* ssd-diagnostic-suite/dist/

# 4. Preparar configurações
echo "⚙️  Preparando configurações..."
cp config/docker/docker-compose.yml docker-compose.yml
cp config/nginx/nginx.conf nginx.conf

# 5. Build Docker
echo "🐳 Construindo containers Docker..."
sudo docker compose down 2>/dev/null || true
sudo docker compose build backend

# 6. Criar pacote .deb
echo "📦 Criando pacote .deb..."
./scripts/build/CRIAR_PACOTE_DEB.sh

# 7. Deploy
echo "🚀 Fazendo deploy..."
sudo docker compose up -d

# 8. Verificar
echo "⏳ Aguardando inicialização..."
sleep 10

echo ""
echo "📊 Status dos containers:"
sudo docker ps --filter "name=ssd_"

echo ""
echo "✅ Produção final concluída!"
echo ""
echo "📋 Resumo:"
echo "   • Frontend: http://localhost:8080"
echo "   • Backend: http://localhost:8000"
echo "   • Pacote .deb: ssd-diagnostic-suite_1.0.0-1_all.deb"
echo ""
echo "🎉 Sistema pronto para uso!"
echo ""

