#!/usr/bin/env bash
set -e

echo "╔═══════════════════════════════════════════════════════════════════════╗"
echo "║       🚀 PRODUÇÃO FINAL - SSD DIAGNOSTIC SUITE                        ║"
echo "╚═══════════════════════════════════════════════════════════════════════╝"
echo ""

# 1. Matar TODOS processos nas portas
echo "🛑 Matando processos nas portas 8000 e 8080..."
sudo fuser -k 8000/tcp 8080/tcp >/dev/null 2>&1
sudo lsof -t -i:8000 | xargs sudo kill -9 2>/dev/null || true
sudo lsof -t -i:8080 | xargs sudo kill -9 2>/dev/null || true
sleep 2

# 2. Parar e remover containers
echo "🧹 Limpando containers..."
sudo docker stop ssd_backend ssd_nginx 2>/dev/null || true
sudo docker rm ssd_backend ssd_nginx 2>/dev/null || true
sudo docker compose down --remove-orphans 2>/dev/null || true

# 3. Rebuild frontend com animações
echo "🔧 Reconstruindo frontend..."
cd ssd-diagnostic-suite
npm run build
cd ..
rm -rf dist
cp -r ssd-diagnostic-suite/dist ./dist

# 4. Ajustar permissões
echo "🔐 Ajustando permissões..."
sudo chown -R $USER:$USER dist/ 2>/dev/null || true

# 5. Build backend
echo "🏗️ Building backend..."
sudo docker compose build --no-cache backend

# 6. Subir containers
echo "🚀 Subindo containers..."
sudo docker compose up -d

# 7. Aguardar inicialização
echo ""
echo "⏳ Aguardando backend inicializar (25 segundos)..."
sleep 25

# 8. Verificar status
echo ""
echo "📊 Verificando status..."
echo ""

# Health check
if curl -f http://localhost:8000/health &>/dev/null; then
    echo "✅ Backend: OK"
else
    echo "❌ Backend: ERRO"
fi

# Containers
echo ""
echo "📦 Containers:"
sudo docker ps | grep ssd || echo "⚠️ Containers não encontrados"

echo ""
echo "═══════════════════════════════════════════════════════════════════════════"
echo "✅ PRODUÇÃO FINALIZADA!"
echo "═══════════════════════════════════════════════════════════════════════════"
echo ""
echo "🌐 Acesse no navegador:"
echo "   👉 http://localhost:8080"
echo ""
echo "📡 API:"
echo "   👉 http://localhost:8000/docs"
echo "   👉 http://localhost:8000/health"
echo ""

# 9. Testar conexão
echo "🧪 Testando conexão..."
if curl -s http://localhost:8000/health | grep -q "ok"; then
    echo "✅ Tudo funcionando perfeitamente!"
else
    echo "⚠️ Aguarde mais 20 segundos e recarregue http://localhost:8080"
fi

echo ""

