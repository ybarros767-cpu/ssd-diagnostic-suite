# 🎯 Disk Diagnostic Suite v2.6.0

**Ferramenta Profissional Corporativa de Análise de Discos (SSD + HD)**

Sistema completo, profissional e corporate-ready para análise de discos com interface web moderna, IA explicativa com raciocínio detalhado, e suporte completo para SSDs e HDs via USB e SATA.

## ✨ Características Principais

### 🔍 Diagnóstico Completo
- **Detecção Automática** de SSDs e HDs (SATA/USB/NVMe)
- **Análise SMART Profunda** - Todos os 30+ atributos analisados em tempo real
- **IA Explicativa** - Groq AI com raciocínio detalhado, evidence-based e confidence scores
- **Temperatura Precisa** - Validação de bridge USB, fallback automático e detecção de valores incorretos

### 📊 Performance & Métricas
- **Testes Completos** de performance (leitura/escrita sequencial e aleatória)
- **Métricas Avançadas** (IOPS, latência, error rate, wear level, health score)
- **Modos Diferentes** - Simplificado (~30s) vs Avançado (~90s) com funcionalidades reais

### 🎨 Interface & UX
- **Interface Web Moderna** com React, TypeScript e Material-UI
- **Feedback Visual** - Toast notifications, auto-fechamento de modais, indicadores de modo
- **Relatórios Multi-formato** - Export em JSON, HTML com layout profissional

### 🚀 Infraestrutura
- **Docker & Nginx** - Deploy containerizado com reverse proxy
- **Observabilidade** - `/metrics/prometheus` (HTTP) e Exporter dedicado (porta 9090)
- **Autenticação JWT (toggleável)** - `ENABLE_AUTH=true`, RBAC básico (admin/viewer)
- **Histórico Persistente** - SQLite ativável (`ENABLE_DB=true`) com endpoints `/diagnostics`
- **Pronto para Produção** - Health checks, CORS configurável, API REST completa

## 🚀 Instalação Rápida

### Via Pacote .deb
```bash
sudo dpkg -i ssd-diagnostic-suite_1.0.0-1_all.deb
sudo apt install ./ssd-diagnostic-suite_1.0.0-1_all.deb
```

### Via Docker Compose
```bash
docker compose build backend
docker compose up -d
```

Ports:
- Backend API: `8000`
- Prometheus Exporter: `9090`
- Nginx (frontend): `8080`

## 🌐 Uso

Acesse: **http://localhost:8080**

1. Selecione um dispositivo (SSD ou HD) na lista
2. Configure no ícone de Configurações:
   - **Modo Simplificado**: Testes rápidos (~30s)
   - **Modo Avançado**: Análise completa e profunda (~90s)
3. Clique em "Iniciar Diagnóstico"
4. Baixe o relatório completo (botão de download)

## 📁 Estrutura do Projeto

```
ssd-diagnostic-suite/
├── config/              # Configurações (Docker, Nginx)
├── scripts/             # Scripts organizados
│   ├── build/          # Scripts de build
│   ├── deploy/         # Scripts de deploy
│   └── utils/          # Utilitários
├── docs/               # Documentação
│   ├── deployment/     # Guias de deploy
│   ├── dev/           # Docs de desenvolvimento
│   └── user/          # Docs para usuários
├── ssd-diagnostic-suite/
│   ├── backend/       # Backend Python/FastAPI (metrics, JWT, SQLite)
│   └── src/           # Frontend React
└── README.md          # Este arquivo
```

## 🔧 Tecnologias

- **Backend**: Python 3.12, FastAPI, Socket.IO, SQLAlchemy
- **Frontend**: React, TypeScript, Material-UI, Vite
- **IA**: Groq AI (gratuito, sem limites)
- **Infra**: Docker, Docker Compose, Nginx

## 📋 Requisitos

- Docker & Docker Compose
- smartctl (smartmontools) e `nvme-cli` (no host ou container)
- Ubuntu/Debian (para .deb)

## 🆘 Suporte

Documentação completa em: `docs/`

### Novidades v2.6.0
- Settings centralizados (`backend/settings.py`)
- Auth JWT com `/auth/login` e proteção por token (toggle `ENABLE_AUTH`)
- Persistência SQLite (toggle `ENABLE_DB`) e rotas `/diagnostics`
- Métricas HTTP em `/metrics/prometheus` e exporter na 9090
- Subprocessos não bloqueantes e melhorias de robustez

## 📄 Licença

MIT License - Veja LICENSE
