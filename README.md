# 🎯 SSD Diagnostic Suite

Sistema completo de diagnóstico de SSD com dois painéis: **CLI** (Terminal) e **Web** (Browser).

## 📋 Índice

- [Início Rápido](#-início-rápido)
- [Dois Painéis Disponíveis](#-dois-painéis-disponíveis)
- [Instalação](#-instalação)
- [Documentação](#-documentação)
- [Estrutura](#-estrutura)
- [Endpoints API](#-endpoints-api)
- [Licença](#-licença)

## 🚀 Início Rápido

### CLI Dashboard (Recomendado para produção)

```bash
./scripts/start_cli.sh
```

### Web Dashboard

```bash
./scripts/install.sh
# Acesse: http://localhost:8080
```

## 🎯 Dois Painéis Disponíveis

### 🖥️ CLI Dashboard ⭐

- **Interface**: Terminal com cores ANSI
- **Dependências**: Apenas Python + requests
- **Uso**: SSH, servidores, headless
- **Comando**: `./scripts/start_cli.sh`

### 🌐 Web Dashboard

- **Interface**: Browser moderno
- **Tecnologia**: React + TypeScript + Material UI
- **Gráficos**: Plotly.js interativo
- **Uso**: Desktop com interface gráfica
- **Comando**: `./scripts/install.sh`

## 📦 Instalação

### Pré-requisitos

```bash
# Python 3.7+ (obrigatório)
python3 --version

# Node.js 18+ (apenas para Web Dashboard)
node --version

# Docker (opcional, para Web Dashboard)
docker --version
```

### CLI Dashboard

```bash
# 1. Instalar dependência
pip3 install requests

# 2. Executar
./scripts/start_cli.sh
```

### Web Dashboard

```bash
# 1. Build do frontend
cd ssd-diagnostic-suite
npm install
npm run build
cd ..

# 2. Subir containers
docker compose up -d
```

## 🎮 CLI Dashboard - Comandos

| Tecla | Ação |
|-------|------|
| `I` | Iniciar Diagnóstico |
| `R` | Ver Relatório |
| `S` | Status do Backend |
| `D` | Listar Dispositivos |
| `Q` | Sair |

## 📖 Documentação

- **[CLI Dashboard](docs/CLI_DASHBOARD_README.md)** - Guia completo do CLI
- **[Quick Start](docs/QUICKSTART_CLI.md)** - Início rápido
- **[Changelog](docs/CHANGELOG.md)** - Histórico de alterações

## 🏗️ Estrutura

```
ssd-diagnostic-suite/
├── docs/                           # 📚 Documentação
│   ├── CLI_DASHBOARD_README.md
│   ├── QUICKSTART_CLI.md
│   ├── CHANGELOG.md
│   └── README.md
│
├── scripts/                        # 🛠️ Scripts
│   ├── start_cli.sh               # CLI Dashboard
│   ├── install.sh                 # Web Dashboard
│   ├── simple_cli_dashboard.py   # Dashboard CLI
│   └── cli_panel.py              # Dashboard avançado
│
├── ssd-diagnostic-suite/          # 🌐 Frontend + Backend
│   ├── src/                       # React components
│   ├── backend/                   # FastAPI
│   │   ├── main.py
│   ├── electron/                 # Desktop app
│   └── dist/                     # Build (gerado)
│
├── docker-compose.yml             # 🐳 Orquestração
├── Dockerfile                     # 📦 Container backend
└── requirements.txt              # 🐍 Python deps
```

## 📡 Endpoints API

- `GET /` - Info da API
- `GET /health` - Healthcheck
- `POST /run` - Inicia diagnóstico
- `GET /report` - Retorna relatório
- `GET /devices` - Lista dispositivos
- `GET /device/{path}/smart` - Dados SMART

## 🔧 Desenvolvimento

### CLI Dashboard (Dev)

```bash
cd scripts
python3 simple_cli_dashboard.py
```

### Web Dashboard (Dev)

```bash
cd ssd-diagnostic-suite
npm run dev    # Frontend
python3 backend/main.py  # Backend
```

### Docker

```bash
docker compose up -d
docker logs -f ssd_backend
```

## 📝 Licença

MIT License

## 👤 Autor

**Yuri Barros** - [@ybarros767](https://github.com/ybarros767)

---

⭐ **Contribuições são bem-vindas!**
