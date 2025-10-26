# 🚀 Quick Start - CLI Dashboard

## Instalação em 30 Segundos

```bash
# 1. Instalar dependência (se não tiver)
pip3 install requests

# 2. Executar
./start_cli.sh
```

Pronto! O dashboard CLI está rodando.

---

## 📝 Instruções Detalhadas

### Opção 1: Automática (Recomendado)

```bash
chmod +x start_cli.sh
./start_cli.sh
```

O script irá:
1. ✅ Matar processos nas portas 8000 e 8080
2. ✅ Verificar se backend está rodando
3. ✅ Iniciar backend se necessário
4. ✅ Iniciar o CLI Dashboard

### Opção 2: Manual

#### Terminal 1: Backend
```bash
cd ssd-diagnostic-suite/backend
python3 main.py
```

#### Terminal 2: CLI Dashboard
```bash
python3 simple_cli_dashboard.py
```

---

## 🎮 Comandos

| Tecla | Ação | Descrição |
|-------|------|-----------|
| `I` | Iniciar | Inicia diagnóstico completo do SSD |
| `R` | Relatório | Mostra relatório em JSON |
| `S` | Status | Verifica se backend está OK |
| `D` | Dispositivos | Lista SSDs disponíveis |
| `Q` | Quit | Sair do dashboard |

---

## 🖼️ Exemplo de Saída

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

Escolha uma opção: i
✓ Diagnóstico iniciado!
```

---

## 🔧 Troubleshooting

### Erro: Backend não inicia

```bash
# Verificar logs
tail -f /tmp/ssd_backend.log

# Iniciar manualmente
cd ssd-diagnostic-suite/backend
python3 main.py
```

### Erro: Porta já em uso

```bash
# Matar processo manualmente
lsof -t -i:8000 | xargs kill -9

# Ou usar script de fix
./fix-install.sh
```

### Backend fora do ar

```bash
# Verificar se está rodando
curl http://localhost:8000/health

# Reiniciar
cd ssd-diagnostic-suite/backend
python3 main.py &
```

---

## 📊 Recursos

- ✅ Status em tempo real
- ✅ Progresso visual
- ✅ Temperatura
- ✅ Velocidades de leitura/escrita  
- ✅ Relatórios detalhados
- ✅ Listagem de dispositivos

---

## 🎯 Dicas

1. **Use SSH**: Dashboard funciona perfeitamente via SSH
2. **Monitoramento**: Veja progresso em tempo real
3. **Relatórios**: Exporte dados quando necessário
4. **Dispositivos**: Liste todos os SSDs disponíveis

---

**Pronto para começar? Execute:**
```bash
./start_cli.sh
```

