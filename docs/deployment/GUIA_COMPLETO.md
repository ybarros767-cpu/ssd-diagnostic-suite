# 📖 Guia Completo de Deploy - SSD Diagnostic Suite v1.0.2

## 🎯 Visão Geral

Sistema completo de diagnóstico de SSDs com interface web, análise por IA gratuita e suporte para múltiplos modos de teste.

## 🚀 Instalação

### Opção 1: Via Pacote .deb (Recomendado)

```bash
sudo dpkg -i ssd-diagnostic-suite_1.0.0-1_all.deb
sudo apt install ./ssd-diagnostic-suite_1.0.0-1_all.deb
```

### Opção 2: Deploy Manual

```bash
cd ssd-diagnostic-suite
./scripts/deploy/DEPLOY.sh
```

## ⚙️ Configuração

### Configurar IA (Opcional)

O sistema já vem com Groq AI configurado gratuitamente. Para usar sua própria chave:

```bash
sudo nano ssd-diagnostic-suite/backend/.env
```

```env
GROQ_API_KEY=sua_chave_aqui
GROQ_MODEL=mixtral-8x7b-32768
```

## 🌐 Uso

### Acessar Interface

**URL**: http://localhost:8080

### Passos

1. **Selecione o Dispositivo**: Escolha na lista (detecção automática)
2. **Configure**: Clique no ícone de engrenagem
   - **Modo Simplificado**: Testes rápidos e básicos
   - **Modo Avançado**: Análises completas e detalhadas
3. **Inicie o Diagnóstico**: Clique em "Iniciar Diagnóstico"
4. **Acompanhe**: Veja métricas em tempo real
5. **Visualize Análise**: IA analisa e fornece recomendações

## 📊 Configurações Avançadas

### Modo Avançado

Quando ativado, permite configurar:

- **Scan Profundo**: Análise mais demorada e completa
- **Teste de Performance Completo**: Testes de I/O detalhados
- **Verificação de Integridade**: Validação de dados
- **Análise de Desgaste**: Detalhada
- **Profundidade SMART**: Básico / Padrão / Profundo

## 🔧 Estrutura

```
ssd-diagnostic-suite/
├── scripts/          # Scripts organizados
│   ├── build/       # Build
│   ├── deploy/      # Deploy
│   └── utils/       # Utilitários
├── docs/            # Documentação
├── config/          # Configurações
└── ssd-diagnostic-suite/
    ├── backend/    # Python/FastAPI
    └── src/        # React
```

## 🔍 Funcionalidades

- ✅ **Detecção Automática**: SSDs e HDs (SATA/USB)
- ✅ **Análise SMART Real**: Via smartctl
- ✅ **IA Gratuita**: Groq AI (sem custos)
- ✅ **Métricas em Tempo Real**: Socket.IO
- ✅ Oct **Interface Moderna**: Material-UI
- ✅ **Dois Modos**: Simples e Avançado

## 🆘 Troubleshooting

### Porta Ocupada

```bash
sudo lsof -t -i:8080 | xargs sudo kill -9
```

### Ver Logs

```bash
sudo docker logs ssd_backend
sudo docker logs ssd_nginx
```

### Rebuild

```bash
sudo docker compose down
sudo docker compose build --no-cache
sudo docker compose up -d
```

## 📝 Notas Importantes

- **Groq AI**: Gratuito e sem limites conhecidos
- **Dados Reais**: Tudo baseado em medições reais
- **Sem Custos**: Nenhuma API paga
- **Local**: Análise fallback funciona offline

## 🎉 Status

**Versão**: 1.0.2
**Status**: Estável e Funcional
**IA**: Groq (gratuito)

