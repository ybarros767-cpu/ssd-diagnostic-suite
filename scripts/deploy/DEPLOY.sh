#!/usr/bin/env bash
set -e

echo "╔═══════════════════════════════════════════════════════════════════════╗"
echo "║         🚀 DEPLOY FINAL - SSD DIAGNOSTIC SUITE                        ║"
echo "╚═══════════════════════════════════════════════════════════════════════╝"
echo ""

# FUNÇÃO: Matar processos nas portas
kill_ports() {
    echo "🛑 Liberando portas 8000 e 8080..."
    
    # Tentar fuser primeiro
    sudo fuser -k 8000/tcp 8080/tcp 2>/dev/null || true
    
    # Matar processos via lsof
    for port in 8000 8080; do
        pids=$(sudo lsof -t -i:$port 2>/dev/null || true)
        if [ -n "$pids" ]; then
            echo "   Matando processos na porta $port..."
            echo $pids | xargs sudo kill -9 2>/dev/null || true
        fi
    done
    
    sleep 2
    
    # Verificar se ainda há processos
    remaining=$(sudo lsof -t -i:8000,8080 2>/dev/null | wc -l)
    if [ "$remaining" -gt 0 ]; then
        echo "⚠️  Ainda há processos. Tentando remover containers..."
        sudo docker stop $(sudo docker ps -q) 2>/dev/null || true
        sudo docker rm $(sudo docker ps -aq) 2>/dev/null || true
    fi
    
    echo "✅ Portas liberadas"
}

# 1. Limpar tudo
echo "🧹 Limpeza completa..."
sudo docker compose down --remove-orphans 2>/dev/null || true
sudo docker system prune -f 2>/dev/null || true
kill_ports

# 2. Rebuild frontend
echo ""
echo "🔧 Reconstruindo frontend com animações..."
cd ssd-diagnostic-suite
npm run build
cd ..

# 3. Copiar dist
rm -rf dist
cp -r ssd-diagnostic-suite/dist ./dist

# 4. Ajustar permissões
echo "🔐 Ajustando permissões..."
sudo chown -R $USER:$USER dist/ 2>/dev/null || true

# 5. Build e subir
echo ""
echo "🏗️ Building e subindo containers..."
docker compose build --no-cache
docker compose up -d

echo ""
echo "⏳ Aguardando 30 segundos para backend inicializar..."
sleep 30

# 6. Verificação final
echo ""
echo "📊 Status Final:"
echo ""

if curl -f http://localhost:8000/health &>/dev/null 2>&1; then
    echo "✅ Backend: FUNCIONANDO"
else
    echo "❌ Backend: Aguardando... (pode levar mais 30 segundos)"
fi

if curl -f http://localhost:8080 &>/dev/null 2>&1; then
    echo "✅ Frontend: FUNCIONANDO"
else
    echo "⚠️  Frontend: Aguardando..."
fi

echo ""
echo "═══════════════════════════════════════════════════════════════════════════"
echo "✅ DEPLOY COMPLETO!"
echo "═══════════════════════════════════════════════════════════════════════════"
echo ""
echo "🌐 URLs:"
echo "   👉 Dashboard: http://localhost:8080"
echo "   👉 API Docs:  http://localhost:8000/docs"
echo "   👉 Health:    http://localhost:8000/health"
echo ""
echo "📦 Containers:"
docker ps | grep ssd
echo ""

echo ""
echo "💡 Se backend não iniciar, execute:"
echo "   docker logs ssd_backend"
echo ""

