# SSD Diag Auto — Guia Rápido

Script único, seguro (somente leitura) e automático para diagnóstico de SSD SATA/NVMe/USB em Ubuntu/Debian.

## Uso
```bash
chmod +x ssd_diag_auto.sh
sudo ./ssd_diag_auto.sh
```

## Opções
- `QUICK=1` — pula badblocks e reduz dmesg (mais rápido)
- `NO_BADBLOCKS=1` — desativa varredura de leitura
- `NO_SELFTEST=1` — não dispara autoteste curto
- `RUN_LONG=1` — executa autoteste longo (não destrutivo; demorado)
- `TARGET=/dev/sdX` ou `/dev/nvme0n1` — define o disco manualmente

## Saída
```
report_YYYYmmdd_HHMMSS/
├── RELATORIO.pdf
├── RELATORIO.md
├── summary.json
└── logs/
```

Todas as operações são NÃO destrutivas.
