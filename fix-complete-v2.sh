#!/usr/bin/env bash
set -e

echo "╔═══════════════════════════════════════════════════════════════════════╗"
echo "║        🔧 CORREÇÃO COMPLETA V2 - SSD DIAGNOSTIC SUITE                ║"
echo "╚═══════════════════════════════════════════════════════════════════════╝"
echo ""

# 1. Parar tudo
echo "🛑 Parando containers..."
sudo docker compose down --remove-orphans 2>/dev/null || true

# 2. Limpar portas
echo "🧹 Limpando portas..."
sudo lsof -t -i:8000 | xargs sudo kill -9 2>/dev/null || true
sudo lsof -t -i:8080 | xargs sudo kill -9 2>/dev/null || true
sudo docker stop ssd_backend ssd_nginx 2>/dev/null || true
sudo docker rm ssd_backend ssd_nginx 2>/dev/null || true

# 3. Rebuild frontend
echo "🔧 Reconstruindo frontend com animações..."
cd ssd-diagnostic-suite
npm run build
cd ..
rm -rf dist
cp -r ssd-diagnostic-suite/dist ./dist

# 4. Ajustar permissões
echo "🔐 Ajustando permissões..."
sudo chown -R $USER:$USER dist/

# 5. Subir containers
echo "🚀 Subindo containers..."
sudo docker compose up -d --build

echo ""
echo "⏳ Aguardando inicialização (15 segundos)..."
sleep 15

# 6. Status
echo ""
echo "📊 Status:"
sudo docker ps | grep ssd || echo "⚠️ Containers não rodando"

echo ""
echo "✅ COMPLETO!"
echo ""
echo "🌐 Acesse:"
echo "   Dashboard:  http://localhost:8080"
echo "   API Docs:   http://localhost:8000/docs"
echo "   Health:     http://localhost:8000/health"
echo ""
echo "💡 Se ainda ver página do Nginx, aguarde 30 segundos e recarregue a página"

