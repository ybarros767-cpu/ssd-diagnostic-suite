# 📁 Estrutura do Projeto

## Organização Profissional

```
ssd-diagnostic-suite/
│
├── 📚 docs/                      # Documentação completa
│   ├── CLI_DASHBOARD_README.md  # Guia CLI
│   ├── QUICKSTART_CLI.md        # Quick Start
│   └── CHANGELOG.md             # Histórico
│
├── 🛠️  scripts/                   # Scripts executáveis
│   ├── start_cli.sh            # Inicia CLI Dashboard
│   ├── install.sh               # Instala Web Dashboard
│   └── simple_cli_dashboard.py # Dashboard CLI
│
├── 🌐 ssd-diagnostic-suite/       # Frontend + Backend
│   ├── src/                     # React components
│   │   ├── components/         # Componentes React
│   │   ├── api/                # API integration
│   │   ├── App.tsx             # App principal
│   │   ├── main.tsx           # Entry point
│   │   └── theme.ts           # Material UI theme
│   │
│   ├── backend/                # FastAPI Backend
│   │   ├── main.py           # API principal
│   │   ├── requirements.txt  # Python deps
│   │   └── Dockerfile        # Container backend
│   │
│   ├── electron/              # Desktop app config
│   ├── index.html            # HTML entry
│   └── package.json          # NPM config
│
├── 🐳 docker-compose.yml        # Orquestração de containers
├── 🚀 ssd_diag_auto_enhanced.sh # Script diagnóstico original
├── 📖 README.md                 # Documentação principal
├── 📝 LICENSE                    # Licença MIT
└── 🔒 .gitignore                # Arquivos ignorados
```

## 📦 Componentes

### CLI Dashboard
- **Localização**: `scripts/simple_cli_dashboard.py`
- **Executar**: `./scripts/start_cli.sh`
- **Dependências**: `requests` (pip)
- **Uso**: Terminal/SSH

### Web Dashboard
- **Frontend**: `ssd-diagnostic-suite/src/`
- **Backend**: `ssd-diagnostic-suite/backend/`
- **Executar**: `./scripts/install.sh`
- **Dependências**: Node.js + Docker
- **Uso**: Browser

### Backend API
- **Localização**: `ssd-diagnostic-suite/backend/main.py`
- **Framework**: FastAPI
- **Porta**: 8000
- **Endpoints**: /health, /run, /report, /devices

## 🎯 Arquivos Importantes

| Arquivo | Descrição | Localização |
|---------|-----------|-------------|
| `README.md` | Documentação principal | Raiz |
| `start_cli.sh` | Inicia CLI Dashboard | scripts/ |
| `install.sh` | Instala Web Dashboard | scripts/ |
| `docker-compose.yml` | Orquestração Docker | Raiz |
| `main.py` | API Backend | ssd-diagnostic-suite/backend/ |
| `App.tsx` | Frontend React | ssd-diagnostic-suite/src/ |

## 📝 Notas

- **Documentação**: Toda a doc está em `docs/`
- **Scripts**: Todos os scripts estão em `scripts/`
- **Código**: Frontend e backend em `ssd-diagnostic-suite/`
- **Build**: Resultado do build em `dist/` (gerado)

