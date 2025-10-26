#!/usr/bin/env bash
set -e

echo "╔═══════════════════════════════════════════════════════════════════════╗"
echo "║              ✅ CORREÇÃO FINAL - SSD DIAGNOSTIC SUITE                  ║"
echo "╚═══════════════════════════════════════════════════════════════════════╝"
echo ""

# Limpar tudo
echo "🛑 Parando tudo..."
sudo docker compose down --remove-orphans 2>/dev/null || true
sudo lsof -t -i:8000 | xargs sudo kill -9 2>/dev/null || true
sudo lsof -t -i:8080 | xargs sudo kill -9 2>/dev/null || true

# Rebuild
echo "🔧 Rebuild backend..."
sudo docker compose build --no-cache backend

echo "🚀 Subindo containers..."
sudo docker compose up -d

echo ""
echo "⏳ Aguardando 20 segundos..."
sleep 20

echo ""
echo "✅ PRONTO!"
echo ""
echo "📊 Status:"
sudo docker ps | grep ssd

echo ""
echo "🌐 Acesse:"
echo "   http://localhost:8080"
echo "   http://localhost:8000/docs"

