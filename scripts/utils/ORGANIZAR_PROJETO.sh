#!/usr/bin/env bash
set -e

echo "╔═══════════════════════════════════════════════════════════════════════╗"
echo "║           🗂️  ORGANIZANDO PROJETO PROFISSIONALMENTE                   ║"
echo "╚═══════════════════════════════════════════════════════════════════════╝"
echo ""

cd "$(dirname "$0")"

# 1. Backup dos arquivos .env
echo "🔐 Backup de arquivos sensíveis..."
if [ -f ssd-diagnostic-suite/backend/.env ]; then
    cp ssd-diagnostic-suite/backend/.env ssd-diagnostic-suite/backend/.env.backup
    echo "✅ .env backup criado"
fi

# 2. Remover arquivos .env do controle de versão
echo "🗑️  Removendo arquivos sensíveis..."
rm -f ssd-diagnostic-suite/backend/.env
echo "✅ Arquivos sensíveis removidos (use .env.template)"

# 3. Criar estrutura profissional
echo "📁 Criando estrutura profissional..."

# Limpar arquivos antigos duplicados
rm -f MELHORIAS_FINAIS.md RELATORIO_PROGRESSO.md RECURSOS_IMPLEMENTADOS.md
rm -f Criar_package_deb.sh "C riar_package_deb.sh"
rm -f ssd_diag_auto_enhanced.sh SOLUCAO_DEFINITIVA.sh EXECUTAR_FINAL.sh
rm -f LIMPAR_DIST.sh LIMPAR_E_ORGANIZAR.sh
rm -f COMANDOS_FINAIS.txt RESUMO_FINAL_PRODUCAO.md
rm -f nginx.conf docker-compose.yml  # serão copiados depois
rm -f START.sh PRODUCAO_FINAL.sh

# Mover scripts para pastas corretas
echo "📦 Organizando scripts..."
mkdir -p scripts/{build,deploy,dev,utils}
[ -f CRIAR_PACOTE_DEB.sh ] && mv CRIAR_PACOTE_DEB.sh scripts/build/
[ -f DEPLOY.sh ] && mv DEPLOY.sh scripts/deploy/
[ -f START.sh ] && mv START.sh scripts/deploy/ 2>/dev/null || true

# Organizar documentação
echo "📚 Organizando documentação..."
mkdir -p docs/{user,dev,deployment,changelog}
mkdir -p docs/dev/RELATORIO_PROGRESSO.md 2>/dev/null || true
mkdir -p docs/user/RECURSOS_IMPLEMENTADOS.md 2>/dev/null || true

# Criar .gitignore apropriado
echo "🔒 Criando .gitignore..."
cat > .gitignore << 'EOF'
# Environment files
.env
*.env
*.env.local
.env.backup

# Node
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# Build outputs
dist/
build-output/
.build/
*.deb

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python

# Docker
.docker/

# IDE
.vscode/
.idea/
*.swp
*.swo

# Logs
*.log
logs/

# OS
.DS_Store
Thumbs.db

# Temporary files
*.tmp
*.bak
*.backup

# Sensitive data
.env
*.key
*.pem
EOF

echo "✅ .gitignore criado"

# 4. Criar estrutura de config
echo "⚙️  Organizando configurações..."
mkdir -p config/{docker,nginx}
[ -f docker-compose.yml ] && mv docker-compose.yml config/docker/
[ -f nginx.conf ] && mv nginx.conf config/nginx/

# 5. Criar README profissional
echo "📝 Criando README.md principal..."

# 6. Copiar .env.template se não existir
if [ ! -f ssd-diagnostic-suite/backend/.env.template ]; then
    cat > ssd-diagnostic-suite/backend/.env.template << 'EOF'
# SSD Diagnostic Suite - Environment Variables Template
# Copy this file to .env and configure your values

APP_ENV=production
PORT=8000

# Comma-separated list of allowed origins for CORS
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8080

# OpenAI API Configuration
# Get your API key from: https://platform.openai.com/api-keys
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-3.5-turbo
OPENAI_TEMPERATURE=0.1

# Backend Configuration
HOST=0.0.0.0
DEBUG=1
EOF
    echo "✅ .env.template criado"
fi

echo ""
echo "✅ Organização completa!"
echo ""
echo "📂 Estrutura criada:"
echo "   scripts/        - Scripts organizados por categoria"
echo "   docs/           - Documentação categorizada"
echo "   config/         - Configurações do sistema"
echo "   .gitignore      - Arquivos sensíveis ignorados"
echo ""

