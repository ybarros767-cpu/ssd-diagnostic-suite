#!/usr/bin/env bash
set -e

echo "╔═══════════════════════════════════════════════════════════════════════╗"
echo "║         🚀 DEPLOY COMPLETO - SSD DIAGNOSTIC SUITE v2.5.1              ║"
echo "╚═══════════════════════════════════════════════════════════════════════╝"
echo ""

# Verificar se Docker está rodando
if ! docker info >/dev/null 2>&1 && ! sudo docker info >/dev/null 2>&1; then
    echo "❌ Docker não está rodando. Por favor, inicie o Docker primeiro."
    exit 1
fi

# Verificar se tem permissão docker ou precisa sudo
USE_SUDO=""
if ! docker info >/dev/null 2>&1; then
    USE_SUDO="sudo"
    echo "⚠️  Usando sudo para comandos Docker"
fi

DOCKER_CMD="${USE_SUDO} docker"
COMPOSE_CMD="${USE_SUDO} docker compose"

# 1. Limpar containers antigos
echo "🧹 Limpando containers antigos..."
$COMPOSE_CMD down --remove-orphans 2>/dev/null || true

# 2. Verificar e rebuild frontend se necessário
echo ""
echo "🔧 Verificando frontend..."
if [ ! -d "dist" ] || [ "dist/assets/index.html" -ot "ssd-diagnostic-suite/src/App.tsx" ] 2>/dev/null; then
    echo "   Reconstruindo frontend..."
    cd ssd-diagnostic-suite
    npm run build
    cd ..
    
    # Copiar build para dist
    mkdir -p dist
    cp -r ssd-diagnostic-suite/build-output/* dist/ 2>/dev/null || cp -r ssd-diagnostic-suite/dist/* dist/ 2>/dev/null || true
    echo "✅ Frontend atualizado"
else
    echo "✅ Frontend já está atualizado"
fi

# 3. Verificar arquivo .env
if [ ! -f ".env" ]; then
    if [ -f "ssd-diagnostic-suite/backend/.env.template" ]; then
        echo "📝 Criando .env a partir do template..."
        cp ssd-diagnostic-suite/backend/.env.template .env
        echo "⚠️  Por favor, configure a variável GROQ_API_KEY no arquivo .env"
    else
        echo "⚠️  Arquivo .env não encontrado. Criando um básico..."
        echo "# Groq API Key (opcional)" > .env
        echo "GROQ_API_KEY=your_api_key_here" >> .env
        echo "APP_ENV=production" >> .env
    fi
fi

# 4. Build das imagens Docker
echo ""
echo "🏗️ Construindo imagens Docker..."
$COMPOSE_CMD build --no-cache

# 5. Subir containers
echo ""
echo "🚀 Iniciando containers..."
$COMPOSE_CMD up -d

# 6. Aguardar inicialização
echo ""
echo "⏳ Aguardando inicialização do backend (30 segundos)..."
sleep 30

# 7. Verificar status
echo ""
echo "📊 Verificando status dos serviços..."
echo ""

# Backend
if curl -f http://localhost:8000/health >/dev/null 2>&1; then
    echo "✅ Backend: FUNCIONANDO (http://localhost:8000/health)"
else
    echo "⚠️  Backend: Aguardando... (pode levar mais alguns segundos)"
    echo "   Ver logs com: ${DOCKER_CMD} logs ssd_backend"
fi

# Frontend
if curl -f http://localhost:8080 >/dev/null 2>&1; then
    echo "✅ Frontend: FUNCIONANDO (http://localhost:8080)"
else
    echo "⚠️  Frontend: Verificando..."
fi

# Containers
echo ""
echo "📦 Containers em execução:"
$DOCKER_CMD ps --filter "name=ssd_" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo ""
echo "╔═══════════════════════════════════════════════════════════════════════╗"
echo "║                    ✅ DEPLOY COMPLETO!                                ║"
echo "╚═══════════════════════════════════════════════════════════════════════╝"
echo ""
echo "🌐 URLs:"
echo "   👉 Dashboard: http://localhost:8080"
echo "   👉 API Docs:  http://localhost:8000/docs"
echo "   👉 Health:    http://localhost:8000/health"
echo ""
echo "📝 Comandos úteis:"
echo "   Ver logs backend:  ${DOCKER_CMD} logs -f ssd_backend"
echo "   Ver logs nginx:    ${DOCKER_CMD} logs -f ssd_nginx"
echo "   Parar serviços:    ${COMPOSE_CMD} down"
echo "   Reiniciar:         ${COMPOSE_CMD} restart"
echo ""

