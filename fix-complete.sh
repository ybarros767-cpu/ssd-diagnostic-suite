#!/usr/bin/env bash
set -e

echo "╔═══════════════════════════════════════════════════════════════════════╗"
echo "║           🔧 CORREÇÃO COMPLETA DO SSD DIAGNOSTIC SUITE                ║"
echo "╚═══════════════════════════════════════════════════════════════════════╝"
echo ""

# 1. Parar tudo
echo "🛑 Parando containers e processos..."
sudo docker compose down --remove-orphans 2>/dev/null || true
sudo pkill -f "python.*main.py" 2>/dev/null || true

# 2. Limpar portas
echo "🧹 Limpando portas 8000 e 8080..."
sudo lsof -t -i:8000 | xargs sudo kill -9 2>/dev/null || true
sudo lsof -t -i:8080 | xargs sudo kill -9 2>/dev/null || true
sudo docker stop ssd_backend ssd_nginx 2>/dev/null || true
sudo docker rm ssd_backend ssd_nginx 2>/dev/null || true

# 3. Verificar build
echo "🔍 Verificando build do frontend..."
if [ ! -d "dist" ] || [ ! -f "dist/index.html" ]; then
    echo "📦 Reconstruindo frontend..."
    cd ssd-diagnostic-suite
    npm run build
    cd ..
    rm -rf dist
    cp -r ssd-diagnostic-suite/dist ./dist
fi

# 4. Ajustar permissões
echo "🔐 Ajustando permissões..."
sudo chown -R $USER:$USER dist/

# 5. Subir containers
echo "🚀 Subindo containers..."
sudo docker compose up -d --build

echo ""
echo "⏳ Aguardando inicialização..."
sleep 5

# 6. Verificar status
echo ""
echo "📊 Status dos containers:"
sudo docker ps | grep ssd || echo "⚠️ Containers não encontrados"

echo ""
echo "✅ PRONTO! Acesse:"
echo "   🌐 Frontend: http://localhost:8080"
echo "   📡 Backend:  http://localhost:8000/docs"
echo "   💚 Health:   http://localhost:8000/health"
echo ""

