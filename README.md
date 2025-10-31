# 🎯 Disk Diagnostic Suite v2.5.0

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
- **Arquitetura Extensível** - Pronta para NVMe, ferramentas avançadas (fio), e integração corporate
- **Pronto para Produção** - Health checks, logs estruturados, API REST completa

## 🚀 Instalação Rápida

### Via Docker Compose (recomendado)
```bash
./deploy.sh
```

O script realiza o build do frontend, copia os artefatos para `dist/` e sobe os containers `ssd_backend` e `ssd_nginx` via Docker Compose.

## 💻 Instalação detalhada no Ubuntu

1. **Instale dependências do sistema:**
   ```bash
   sudo apt update
   sudo apt install -y git curl docker.io docker-compose-plugin smartmontools python3 python3-venv
   ```

2. **Instale o Node.js 18 LTS (necessário para o build do frontend):**
   ```bash
   curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
   sudo apt install -y nodejs
   ```

3. **Habilite o Docker para ser usado sem `sudo` (opcional, exige logout/login):**
   ```bash
   sudo usermod -aG docker "$USER"
   newgrp docker
   ```

4. **Clone o repositório e copie as variáveis de ambiente padrão:**
   ```bash
   git clone https://github.com/<seu-usuario>/ssd-diagnostic-suite.git
   cd ssd-diagnostic-suite
   cp .env.example .env
   ```

   Se você possui uma chave da Groq API, edite `.env` e substitua `GROQ_API_KEY` pela sua chave.

5. **Instale as dependências do frontend e faça o build:**
   ```bash
   cd ssd-diagnostic-suite
   npm ci
   npm run build
   cd ..
   ```

6. **Execute o deploy containerizado:**
   ```bash
   ./deploy.sh
   ```

7. **Verifique os serviços:**
   ```bash
   docker ps
   curl http://localhost:8000/health
   ```

   A interface web fica disponível em `http://localhost:8080` e a API em `http://localhost:8000`.

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
│   ├── backend/       # Backend Python/FastAPI
│   └── src/           # Frontend React
└── README.md          # Este arquivo
```

## 🔧 Tecnologias

- **Backend**: Python 3.12, FastAPI, Socket.IO
- **Frontend**: React, TypeScript, Material-UI, Vite
- **IA**: Groq AI (gratuito, sem limites)
- **Infra**: Docker, Docker Compose, Nginx

## 📋 Requisitos

- Docker & Docker Compose
- smartctl (smartmontools)
- Ubuntu/Debian (recomendado)

## 🆘 Suporte

Documentação completa em: `docs/`

## 📄 Licença

MIT License - Veja LICENSE
