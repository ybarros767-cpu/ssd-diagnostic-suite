# 📘 Instruções de Produção - SSD Diagnostic Suite v1.0.2

## 🎯 Sistema de Diagnóstico de SSDs

Sistema completo com interface web moderna, análise por IA gratuita e detecção automática de dispositivos.

## 🚀 Instalação Rápida

### Método 1: Pacote .deb (Recomendado)

```bash
sudo dpkg -i ssd-diagnostic-suite_1.0.0-1_all.deb
```

Se houver dependências faltando:
```bash
sudo apt install ./ssd-diagnostic-suite_1.0.0-1_all.deb
```

### Método 2: Deploy Manual

```bash
./scripts/deploy/DEPLOY.sh
```

## 🔧 Configuração

### IA (Opcional - Já Configurado)

O sistema já vem com Groq AI configurado. Para trocar a chave:

```bash
nano ssd-diagnostic-suite/backend/.env
```

Edite:
```env
GROQ_API_KEY=sua_chave_aqui
```

Depois reinicie:
```bash
sudo docker compose restart backend
```

## 🌐 Uso do Sistema

1. **Acesse**: http://localhost:8080
2. **Escolha**: Dispositivo na lista
3. **Configure**: Clique na engrenagem ⚙️
4. **Escolha Modo**:
   - **Simplificado**: Rápido e básico
   - **Avançado**: Completo e detalhado
5. **Inicie**: Clique em well-child"Iniciar Diagnóstico"
6. **Acompanhe**: Veja métricas em tempo real

## ⚙️ Configurações Avançadas

### Modo Avançado

Disponível ao selecionar "Modo Avançado":

- ✅ **Scan Profundo**: Análise completa (mais lento)
- ✅ **Teste de Performance**: Testes de I/O detalhados
- ✅ **Integridade de Dados**: Verificação completa
- ✅ **Análise de Desgaste**: Detalhada
- ✅ **SMART**: Escolha profundidade (básico/standard/profundo)

## 📊 Funcionalidades

### Detecção e Análise
- Detecção automática de SSDs e HDs
- Identificação de SATA vs USB
- Análise SMART em tempo real
- Métricas precisas via smartctl

### Análise por IA
- **Groq AI**: Gratuito e sem limites
- Análise inteligente em português
- Recomendações técnicas
- Fallback para análise local

### Interface
- Material-UI moderno
- Atualizações em tempo real
- Socket.IO para métricas
- Responsivo e intuitivo

## 🔍 Troubleshooting

### Porta Ocupada
```bash
sudo lsof -t -i:8080 | xargs sudo kill -9
sudo docker compose up -d
```

### Ver Logs
```bash
sudo docker logs ssd_backend
sudo docker logs ssd_nginx
```

### Rebuild Completo
```bash
sudo docker compose down
sudo docker compose build --no-cache
sudo docker compose up -d
```

### Reiniciar Sistema
```bash
sudo docker compose restart
```

## 📁 Estrutura

```
ssd-diagnostic-suite/
├── scripts/              # Scripts de build e deploy
├── docs/                 # Documentação completa
├── config/               # Configurações
├── ssd-diagnostic-suite/ # Código fonte
│   ├── backend/         # Python/FastAPI
│   └── src/             # React/TypeScript
├── docker-compose.yml    # Orquestração
└── nginx.conf           # Proxy reverso
```

## 📦 Versão

- **Versão**: 1.0.2
- **Status**: Produção
- **IA**: Groq (gratuito)
- **Plataforma**: Docker

## ✨ Recursos Principais

✅ Detecção automática de dispositivos
✅ Análise SMART real e precisa
✅ Groq AI gratuito para insights
✅ Modos Simples e Avançado
✅ Métricas em tempo real
✅ Interface moderna e responsiva
✅ 100% open source

## 🎉 Sistema Pronto!

Tudo funcionando e testado. Disponível para uso em produção.
