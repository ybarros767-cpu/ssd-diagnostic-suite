# 🖥️ CLI Dashboard - SSD Diagnostic Suite

Painel de linha de comando integrado e completo para diagnóstico de SSD.

## ✨ Características

- 🎨 **Interface Terminal Rica** - Cores e formatação ANSI
- 📊 **Status em Tempo Real** - Atualização automática
- 🔄 **Monitoramento Contínuo** - Thread dedicada para polling
- 🚀 **Sem Dependências Pesadas** - Apenas Python padrão + requests
- 💻 **Totalmente Interativo** - Menu com opções claras
- 🎯 **Auto-Detecta Backend** - Inicia backend se necessário

## 📋 Pré-requisitos

```bash
# Python 3.7+
python3 --version

# Instalar requests
pip3 install requests
```

## 🚀 Uso Rápido

### Opção 1: Script Automático (Recomendado)

```bash
./start_cli.sh
```

O script irá:
1. Limpar portas 8000 e 8080
2. Verificar/Iniciar backend
3. Iniciar o dashboard CLI

### Opção 2: Manual

```bash
# 1. Verificar se backend está rodando
curl http://localhost:8000/health

# 2. Se não estiver, iniciar backend
cd ssd-diagnostic-suite/backend
python3 main.py &

# 3. Iniciar dashboard
python3 simple_cli_dashboard.py
```

## 🎮 Comandos Disponíveis

| Tecla | Ação |
|-------|------|
| **I** | Iniciar Diagnóstico |
| **R** | Ver Relatório |
| **S** | Status do Backend |
| **D** | Listar Dispositivos |
| **Q** | Sair |

## 📸 Capturas de Tela

### Tela Principal

```
================================================================================
   SSD DIAGNOSTIC SUITE - CLI DASHBOARD
================================================================================

Fase Atual:      SMART
Mensagem:        Coletando dados SMART...
Progresso:       45.0%
Temperatura:     42.3°C
Velocidade:      Leitura: 1234.56 MB/s | Escrita: 987.65 MB/s

███████████████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ 45.0%

--------------------------------------------------------------------------------
COMANDOS DISPONÍVEIS:
--------------------------------------------------------------------------------
  [I] - Iniciar Diagnóstico
  [R] - Ver Relatório
  [S] - Status do Backend
  [D] - Listar Dispositivos
  [Q] - Sair

Escolha uma opção: 
```

## 🔧 Funcionalidades

### 1. Iniciar Diagnóstico

- Inicia diagnóstico completo do SSD
- Monitora progresso em tempo real
- Atualiza status automaticamente
- Mostra fase atual, temperatura, velocidades

### 2. Ver Relatório

- Exibe relatório completo em JSON
- Status de cada fase
- Métricas coletadas
- Histórico de execuções

### 3. Status do Backend

- Verifica se backend está rodando
- Mostra status de saúde
- Verifica conectividade

### 4. Listar Dispositivos

- Lista todos os SSDs disponíveis
- Mostra modelo, serial, bus
- Exibe tamanho do dispositivo

## 🎨 Códigos de Cor

- 🔵 **Azul** - Cabeçalho
- 🟢 **Verde** - Sucesso, ações positivas
- 🔴 **Vermelho** - Erros, problemas
- 🟡 **Amarelo** - Avisos, em andamento
- 🔵 **Ciano** - Informação
- ⚪ **Branco** - Normal

## 🔄 Atualização Automática

O dashboard usa polling a cada 1 segundo para:
- Verificar progresso do diagnóstico
- Atualizar fase atual
- Atualizar métricas (temperatura, velocidades)
- Mostrar mensagens de status

## 🛠️ Troubleshooting

### Backend não inicia

```bash
# Verificar logs
cat /tmp/ssd_backend.log

# Verificar porta
netstat -tulpn | grep 8000

# Reiniciar manualmente
cd ssd-diagnostic-suite/backend
python3 main.py
```

### Erro de conexão

```bash
# Verificar se backend está rodando
curl http://localhost:8000/health

# Se não estiver, iniciar
./start_cli.sh
```

### Porta já em uso

```bash
# Matar processo na porta 8000
lsof -t -i:8000 | xargs kill -9

# Ou usar o script de fix
./fix-install.sh
```

## 📊 Comparação: Web vs CLI

| Característica | Web Dashboard | CLI Dashboard |
|----------------|---------------|---------------|
| Interface | Browser | Terminal |
| Dependências | Node.js + NPM | Python apenas |
| Instalação | Complexa | Simples |
| Portabilidade | ❌ | ✅ |
| Recursos Visuais | ✅ | ✅ (ASCII Art) |
| Tempo Real | ✅ | ✅ |
| Gráficos | Plotly.js | Barra ASCII |

## 🎯 Casos de Uso

### Servidor SSH
```bash
ssh usuario@servidor
./start_cli.sh
```

### Ambiente Headless
```bash
# Sem interface gráfica, CLI é ideal
python3 simple_cli_dashboard.py
```

### Automação
```bash
# Integrar em scripts
echo "I" | timeout 60 python3 simple_cli_dashboard.py
```

## 🚀 Próximas Melhorias

- [ ] Gráficos ASCII mais elaborados
- [ ] Histórico de execuções
- [ ] Exportar relatório em vários formatos
- [ ] Configuração via arquivo
- [ ] Logs detalhados

## 📝 Notas

- O dashboard se conecta ao backend via HTTP REST API
- Não usa WebSocket, apenas polling HTTP
- Compatível com qualquer terminal ANSI
- Funciona bem em SSH e telnet

---

**Versão:** 1.0.0  
**Autor:** Yuri Barros  
**Licença:** MIT

