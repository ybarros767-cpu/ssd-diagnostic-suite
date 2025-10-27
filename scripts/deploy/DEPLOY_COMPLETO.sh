#!/usr/bin/env bash
set -e

echo "╔═══════════════════════════════════════════════════════════════════════╗"
echo "║           🚀 DEPLOY COMPLETO COM DADOS REAIS - v1.0.0                ║"
echo "╚═══════════════════════════════════════════════════════════════════════╝"
echo ""

cd "$(dirname "$0")"

# 1. Limpar e rebuild frontend
echo "🔧 Reconstruindo frontend..."
cd ssd-diagnostic-suite && npm run build && cd ..

# 2. Copiar build
echo "📦 Copiando build..."
mkdir -p dist ssd-diagnostic-suite/dist
cp -r ssd-diagnostic-suite/build-output/* dist/
cp -r ssd-diagnostic-suite/build-output/* ssd-diagnostic-suite/dist/

# 3. Configurar .env
if [ ! -f ssd-diagnostic-suite/backend/.env ]; then
    echo "📝 Criando .env..."
    cp ssd-diagnostic-suite/backend/.env.template ssd-diagnostic-suite/backend/.env
fi

# 4. Preparar configurações
cp config/docker/docker-compose.yml docker-compose.yml
cp config/nginx/nginx.conf nginx.conf

# 5. Matar processo na porta 8080
echo "🛑 Liberando porta 8080..."
sudo lsof -i :8080 | grep LISTEN | awk '{print $2}' | xargs sudo kill 2>/dev/null || true
sleep 2

# 6. Build e deploy
echo "🐳 Construindo containers..."
sudo docker compose down 2>/dev/null || true
sudo docker compose build backend
sudo docker compose up -d

# 7. Aguardar
echo "⏳ Aguardando inicialização..."
sleep 10

# 8. Verificar
echo ""
echo "📊 Status:"
sudo docker ps --filter "name=ssd_"

echo ""
echo "✅ Deploy completo!"
echo ""
echo "🌐 Frontend: http://localhost:8080"
echo "🔧 Backend: http://localhost:8000"
echo ""
echo "📦 Para criar pacote .deb: ./scripts/build/CRIAR_PACOTE_DEB.sh"

