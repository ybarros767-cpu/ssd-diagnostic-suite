#!/bin/bash

# Script de Debug e Teste Completo - Disk Diagnostic Suite v2.5.0

set +e  # Não parar em caso de erro

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

PASSED=0
FAILED=0
WARNINGS=0

log_pass() {
    echo -e "${GREEN}✅ PASSO:${NC} $1"
    ((PASSED++))
}

log_fail() {
    echo -e "${RED}❌ FALHOU:${NC} $1"
    ((FAILED++))
}

log_warn() {
    echo -e "${YELLOW}⚠️  AVISO:${NC} $1"
    ((WARNINGS++))
}

log_info() {
    echo -e "${BLUE}ℹ️  INFO:${NC} $1"
}

echo "╔═══════════════════════════════════════════════════════════════════════╗"
echo "║  🔍 DEBUG E TESTE COMPLETO - Disk Diagnostic Suite v2.5.0          ║"
echo "╚═══════════════════════════════════════════════════════════════════════╝"
echo ""

# TESTE 1: Estrutura de Diretórios
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "TESTE 1: Estrutura de Diretórios"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

TEST_DIRS=(
    "ssd-diagnostic-suite"
    "ssd-diagnostic-suite/backend"
    "ssd-diagnostic-suite/src"
    "dist"
    "docs"
    "scripts"
)

for dir in "${TEST_DIRS[@]}"; do
    if [ -d "$dir" ]; then
        log_pass "$dir"
    else
        if [[ "$dir" == "dist" ]]; then
            log_warn "$dir (opcional)"
        else
            log_fail "$dir não encontrado"
        fi
    fi
done

# TESTE 2: Arquivos Backend
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "TESTE 2: Arquivos Backend"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

FILES=(
    "ssd-diagnostic-suite/backend/main.py"
    "ssd-diagnostic-suite/backend/requirements.txt"
    "ssd-diagnostic-suite/backend/Dockerfile"
    "ssd-diagnostic-suite/backend/smart_analysis.py"
    "ssd-diagnostic-suite/backend/ai_explainer.py"
)

for file in "${FILES[@]}"; do
    if [ -f "$file" ]; then
        log_pass "$(basename $file)"
    else
        log_fail "$(basename $file)"
    fi
done

# TESTE 3: Docker
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "TESTE 3: Docker e Containers"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if command -v docker &> /dev/null; then
    log_pass "Docker instalado"
    
    if sudo docker ps | grep -q ssd_backend; then
        log_pass "ssd_backend rodando"
    else
        log_fail "ssd_backend não está rodando"
    fi
    
    if sudo docker ps | grep -q ssd_nginx; then
        log_pass "ssd_nginx rodando"
    else
        log_fail "ssd_nginx não está rodando"
    fi
else
    log_fail "Docker não instalado"
fi

# TESTE 4: API Endpoints
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "TESTE 4: Endpoints API"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8080 2>/dev/null || echo "000")
[ "$response" = "200" ] && log_pass "Frontend (8080)" || log_fail "Frontend (8080)"

response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health 2>/dev/null || echo "000")
[ "$response" = "200" ] && log_pass "Backend Health" || log_warn "Backend Health"

# TESTE 5: Logs
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "TESTE 5: Logs Backend"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

backend_logs=$(sudo docker compose logs --tail=20 backend 2>&1)
if echo "$backend_logs" | grep -i "error" > /dev/null 2>&1; then
    error_count=$(echo "$backend_logs" | grep -i "error" | wc -l)
    log_warn "$error_count erros nos logs"
else
    log_pass "Sem erros críticos"
fi

# RELATÓRIO FINAL
echo ""
echo "╔═══════════════════════════════════════════════════════════════════════╗"
echo "║  📊 RELATÓRIO FINAL                                                  ║"
echo "╚═══════════════════════════════════════════════════════════════════════╝"
echo ""

total=$((PASSED + FAILED + WARNINGS))
rate=$(awk "BEGIN {printf \"%.1f\", ($PASSED/$total)*100}")

echo "✅ Passados: $PASSED"
echo "❌ Falhados: $FAILED"
echo "⚠️  Avisos: $WARNINGS"
echo "📊 Taxa de Sucesso: ${rate}%"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}🎉 SISTEMA OPERACIONAL!${NC}"
    exit 0
else
    echo -e "${RED}❌ ERROS ENCONTRADOS${NC}"
    exit 1
fi
