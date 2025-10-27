# 📊 Configuração do Dashboard Grafana

## 🚀 Setup Rápido

### 1. Configurar Prometheus

Adicionar ao `prometheus.yml`:

```yaml
scrape_configs:
  - job_name: 'ssd-diagnostic'
    scrape_interval: 30s
    static_configs:
      - targets: ['localhost:9090']
```

### 2. Importar Dashboard no Grafana

1. Abrir Grafana (normalmente http://localhost:3000)
2. Ir para **Dashboards > Import**
3. Selecionar arquivo: `docs/grafana/dashboard.json`
4. Configurar Prometheus como data source
5. Salvar dashboard

### 3. Visualizações Disponíveis

- **Saúde do Disco** (%) - Gauge
- **Temperatura** (°C) - Graph com alertas
- **Nível de Desgaste** (%) - Graph crescente
- **Throughput** (MB/s) - Graph leitura/escrita
- **IOPS** - Graph de operações
- **Bad Blocks** - Stat panel
- **Power On Hours** - Stat panel

## 🎯 Métricas Disponíveis

- `disk_health_score`
- `disk_temperature_celsius`
- `disk_wear_level_percent`
- `disk_read_speed_mbps`
- `disk_write_speed_mbps`
- `disk_iops`
- `disk_bad_blocks`
- `disk_power_on_hours`

## 🚨 Alertas Sugeridos

- Temperatura > 70°C
- Saúde < 70%
- Desgaste > 80%
- Bad Blocks > 10

