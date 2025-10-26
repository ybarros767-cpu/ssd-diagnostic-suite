#!/usr/bin/env bash
set -e

echo "=== SSD Diagnostic Suite - CLI Dashboard ==="
echo ""

# Criar função de cleanup
cleanup() {
    echo ""
    echo "🛑 Encerrando processos..."
    kill $BACKEND_PID 2>/dev/null || true
    kill $PANEL_PID 2>/dev/null || true
    exit 0
}

trap cleanup SIGINT SIGTERM

# Verificar Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 não encontrado. Por favor instale primeiro."
    exit 1
fi

# Matar processos nas portas
echo "🧹 Limpando portas..."
lsof -t -i:8000 2>/dev/null | xargs kill -9 2>/dev/null || true
lsof -t -i:8080 2>/dev/null | xargs kill -9 2>/dev/null || true

# Iniciar backend se não estiver rodando
if ! curl -f http://localhost:8000/health &>/dev/null 2>&1; then
    echo "🚀 Iniciando backend..."
    cd ssd-diagnostic-suite/backend
    python3 main.py > /tmp/ssd_backend.log 2>&1 &
    BACKEND_PID=$!
    cd ../..
    
    # Aguardar inicialização
    echo "⏳ Aguardando backend..."
    for i in {1..20}; do
        if curl -f http://localhost:8000/health &>/dev/null 2>&1; then
            echo "✅ Backend pronto!"
            break
        fi
        sleep 1
    done
    
    if ! curl -f http://localhost:8000/health &>/dev/null; then
        echo "❌ Backend não inicializou corretamente"
        kill $BACKEND_PID 2>/dev/null || true
        exit 1
    fi
else
    echo "✅ Backend já está rodando"
fi

# Tornar executável e iniciar dashboard
chmod +x simple_cli_dashboard.py
echo ""
echo "🎨 Iniciando CLI Dashboard..."
echo ""

python3 simple_cli_dashboard.py

# Cleanup ao final
cleanup

