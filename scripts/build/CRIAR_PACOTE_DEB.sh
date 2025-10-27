#!/usr/bin/env bash
set -e

echo "╔═══════════════════════════════════════════════════════════════════════╗"
echo "║          📦 CRIANDO PACOTE .DEB - SSD DIAGNOSTIC SUITE                ║"
echo "╚═══════════════════════════════════════════════════════════════════════╝"
echo ""

cd "$(dirname "$0")/../.."

# Limpar builds anteriores
sudo rm -rf .build
sudo rm -f ssd-diagnostic-suite*.deb

# 1. Criar estrutura
echo "📁 Criando estrutura..."
mkdir -p .build/opt/ssd-diagnostic-suite
mkdir -p .build/usr/local/bin
mkdir -p .build/usr/share/applications
mkdir -p .build/DEBIAN

# 2. Copiar arquivos essenciais
echo "📦 Copiando arquivos..."

# Copiar todo o projeto
cp -r ssd-diagnostic-suite .build/opt/ssd-diagnostic-suite/
cp -r scripts .build/opt/ssd-diagnostic-suite/
cp -r docs .build/opt/ssd-diagnostic-suite/
cp README.md LICENSE .build/opt/ssd-diagnostic-suite/
cp docker-compose.yml nginx.conf .build/opt/ssd-diagnostic-suite/
cp *.sh .build/opt/ssd-diagnostic-suite/ 2>/dev/null || true

# Copiar dist (build do frontend)
if [ -d "dist" ]; then
    cp -r dist .build/opt/ssd-diagnostic-suite/
fi

# 3. Criar script executável global
cat > .build/usr/local/bin/ssd-diagnostic-suite << 'EOF'
#!/bin/bash
cd /opt/ssd-diagnostic-suite
exec "$@"
EOF
chmod +x .build/usr/local/bin/ssd-diagnostic-suite

# Criar shortcuts
cat > .build/usr/local/bin/ssd-diagnostic << 'EOF'
#!/bin/bash
cd /opt/ssd-diagnostic-suite && sudo ./DEPLOY.sh
EOF
chmod +x .build/usr/local/bin/ssd-diagnostic

# 4. Criar desktop entry
cat > .build/usr/share/applications/ssd-diagnostic-suite.desktop << EOF
[Desktop Entry]
Name=SSD Diagnostic Suite
Comment=Diagnostic tool for SSDs with AI analysis
Exec=xdg-open http://localhost:8080
Icon=utilities-system-monitor
Terminal=false
Type=Application
Categories=System;Monitor;Utility;
EOF

# 5. Criar arquivo control
cat > .build/DEBIAN/control << 'EOF'
Package: ssd-diagnostic-suite
Version: 1.0.0-1
Section: utils
Priority: optional
Architecture: all
Depends: docker.io, docker-compose, curl
Recommends: smartmontools
Maintainer: Yuri Barros <yuri@example.com>
Description: SSD Diagnostic Suite - Complete diagnostic tool with AI analysis
 Modern web-based SSD diagnostic tool with:
 - Real-time SMART data collection
 - Performance testing (sequential/random read/write)
 - Latency analysis
 - Health monitoring
 - AI-powered insights (OpenAI GPT)
 - Beautiful web interface
 .
 Features:
 * Real-time metrics display
 * Deep technical analysis
 * AI-generated recommendations
 * Comprehensive reporting
 * Multi-device support (USB/SATA)

EOF

# 6. Criar postinst
cat > .build/DEBIAN/postinst << 'EOF'
#!/bin/bash
set -e

echo ""
echo "╔═══════════════════════════════════════════════════════════════════════╗"
echo "║       🚀 SSD DIAGNOSTIC SUITE - INSTALAÇÃO CONCLUÍDA                  ║"
echo "╚═══════════════════════════════════════════════════════════════════════╝"
echo ""
echo "✅ Instalado em: /opt/ssd-diagnostic-suite"
echo ""
echo "📋 Comandos disponíveis:"
echo ""
echo "  Iniciar aplicação:"
echo "    ssd-diagnostic"
echo "    cd /opt/ssd-diagnostic-suite && sudo ./DEPLOY.sh"
echo ""
echo "  Parar aplicação:"
echo "    cd /opt/ssd-diagnostic-suite && sudo docker compose down"
echo ""
echo "  Acessar interface:"
echo "    http://localhost:8080"
echo ""
echo "  Ver logs:"
echo "    cd /opt/ssd-diagnostic-suite && sudo docker compose logs -f"
echo ""
echo "📚 Documentação completa em:"
echo "    /opt/ssd-diagnostic-suite/docs/"
echo ""
echo "🔧 Dependências:"
echo "    - Docker (instalado)"
echo "    - Docker Compose (instalado)"
echo ""

# Adicionar usuário ao grupo docker se necessário
if ! groups | grep -q docker; then
    echo "⚠️  Nota: Você precisa adicionar seu usuário ao grupo docker:"
    echo "    sudo usermod -aG docker $USER"
    echo "    (Faça logout e login novamente)"
fi

exit 0
EOF

chmod +x .build/DEBIAN/postinst

# 7. Criar prerm (antes de remover)
cat > .build/DEBIAN/prerm << 'EOF'
#!/bin/bash
set -e

# Parar containers se estiverem rodando
if [ -d /opt/ssd-diagnostic-suite ]; then
    cd /opt/ssd-diagnostic-suite
    sudo docker compose down 2>/dev/null || true
fi

exit 0
EOF
chmod +x .build/DEBIAN/prerm

# 8. Criar postrm (depois de remover)
cat > .build/DEBIAN/postrm << 'EOF'
#!/bin/bash
set -e

# Limpar imagens Docker opcionalmente
# sudo docker rmi ssd-diagnostic-suite-backend 2>/dev/null || true

exit 0
EOF
chmod +x .build/DEBIAN/postrm

# 9. Calcular tamanho
DU_SIZE=$(du -sk .build | awk '{print $1}')
INSTALLED_SIZE=$((DU_SIZE + 1))

# 10. Atualizar control com tamanho
sed -i "s/^Architecture: all$/Architecture: all\nInstalled-Size: $INSTALLED_SIZE/" .build/DEBIAN/control

# 11. Build do pacote
echo "🏗️ Construindo pacote .deb..."
dpkg-deb --build .build ssd-diagnostic-suite_1.0.0-1_all.deb

# 12. Verificar conteúdo
echo ""
echo "📋 Conteúdo do pacote:"
dpkg-deb -c ssd-diagnostic-suite_1.0.0-1_all.deb | head -20

# 13. Verificar informações
echo ""
echo "📦 Informações do pacote:"
dpkg-deb -I ssd-diagnostic-suite_1.0.0-1_all.deb | grep -E "(Package|Version|Architecture|Installed-Size|Depends)"

# 14. Calcular hash
echo ""
echo "🔐 Checksums:"
md5sum ssd-diagnostic-suite_1.0.0-1_all.deb
sha256sum ssd-diagnostic-suite_1.0.0-1_all.deb

echo ""
echo "✅ Pacote criado com sucesso: ssd-diagnostic-suite_1.0.0-1_all.deb"
echo ""
echo "📥 Para instalar:"
echo "   sudo dpkg -i ssd-diagnostic-suite_1.0.0-1_all.deb"
echo ""
echo "📥 Ou com resolução automática de dependências:"
echo "   sudo apt install ./ssd-diagnostic-suite_1.0.0-1_all.deb"
echo ""
echo "🗑️ Para remover:"
echo "   sudo apt remove ssd-diagnostic-suite"
echo ""
echo ""

