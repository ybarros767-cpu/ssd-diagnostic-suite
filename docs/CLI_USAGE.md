# 💻 Uso do CLI Tool

## Instalação

```bash
chmod +x cli/cli_tool.py
sudo cp cli/cli_tool.py /usr/local/bin/disk-diagnostic
```

## Uso Básico

### Análise de um dispositivo

```bash
disk-diagnostic /dev/sda
```

### Salvar relatório JSON

```bash
disk-diagnostic /dev/sda -o report.json
```

### Formato de saída

```bash
# Resumo (padrão)
disk-diagnostic /dev/sda

# JSON completo
disk-diagnostic /dev/sda --format json
```

## Exemplos

```bash
# Analisar SSD
disk-diagnostic /dev/nvme0n1 -o ssd_report.json

# Analisar USB
disk-diagnostic /dev/sdb

# Análise completa em JSON
disk-diagnostic /dev/sda --format json > full_report.json
```

## Integração com Scripts

```bash
#!/bin/bash
DEVICE="/dev/sda"
REPORT_DIR="/var/reports/disk"

# Rodar diagnóstico
disk-diagnostic "$DEVICE" -o "$REPORT_DIR/$(date +%Y%m%d_%H%M%S).json"

# Verificar saúde
HEALTH=$(disk-diagnostic "$DEVICE" --format json | jq '.health')

if [ "$HEALTH" -lt 80 ]; then
    echo "ALERTA: Disco com saúde $HEALTH%"
    # Enviar notificação
fi
```

