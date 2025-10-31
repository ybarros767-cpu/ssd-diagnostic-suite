#!/bin/bash
set -e

echo "╔═══════════════════════════════════════════════════════════════════════╗"
echo "║     🚀 DEPLOY - SSD DIAGNOSTIC SUITE v2.5.1                           ║"
echo "╚═══════════════════════════════════════════════════════════════════════╝"
echo ""

# Limpeza
echo "🧹 Limpeza completa..."
sudo docker ps -a --filter "name=ssd_" --format "{{.ID}}" | xargs sudo docker rm -f 2>/dev/null || true
sudo docker container prune -af >/dev/null 2>&1 || true
sudo fuser -k 8000/tcp 8080/tcp 2>/dev/null || sudo lsof -ti:8000,8080 | xargs sudo kill -9 2>/dev/null || true
sudo docker compose down --remove-orphans >/dev/null 2>&1 || true
sleep 2
echo "✅ Limpeza completa!"

# Frontend
echo ""
echo "🔧 Build frontend..."
cd ssd-diagnostic-suite
npm run build
cd ..
sudo mkdir -p dist
sudo cp -r ssd-diagnostic-suite/build-output/* dist/
echo "✅ Frontend buildado!"

# Docker
echo ""
echo "🐳 Build e deploy Docker..."
sudo docker compose build --no-cache
sudo docker compose up -d
echo "✅ Containers iniciados!"

# Aguardar
echo ""
echo "⏳ Aguardando 40 segundos..."
sleep 40

# Verificar
echo ""
echo "📊 Verificando status..."
if curl -f http://localhost:8000/health >/dev/null 2>&1; then
    echo "✅ Backend: OK - http://localhost:8000/health"
else
    echo "⚠️  Backend: Verificar logs com: sudo docker logs ssd_backend"
fi

if curl -f http://localhost:8080 >/dev/null 2>&1; then
    echo "✅ Frontend: OK - http://localhost:8080"
else
    echo "⚠️  Frontend: Verificar logs com: sudo docker logs ssd_nginx"
fi

echo ""
echo "╔═══════════════════════════════════════════════════════════════════════╗"
echo "║                  ✅ DEPLOY COMPLETO!                                  ║"
echo "╚═══════════════════════════════════════════════════════════════════════╝"
echo ""
echo "🌐 URLs:"
echo "   Dashboard: http://localhost:8080"
echo "   API Docs:  http://localhost:8000/docs"
echo "   Health:    http://localhost:8000/health"
echo ""
echo "📝 Comandos úteis:"
echo "   sudo docker logs -f ssd_backend"
echo "   sudo docker logs -f ssd_nginx"
echo "   sudo docker ps"
echo ""

