"""
Prometheus Exporter - Integração com Prometheus/Grafana
Expõe métricas no formato Prometheus
"""
import logging
from typing import Dict
from prometheus_client import Counter, Gauge, start_http_server

logger = logging.getLogger(__name__)

class PrometheusExporter:
    """Exporta métricas para Prometheus"""
    
    def __init__(self):
        self.metrics = {
            'health_score': Gauge('disk_health_score', 'Saúde do disco (%)', ['device']),
            'temperature': Gauge('disk_temperature_celsius', 'Temperatura do disco (°C)', ['device']),
            'wear_level': Gauge('disk_wear_level_percent', 'Nível de desgaste (%)', ['device']),
            'read_speed': Gauge('disk_read_speed_mbps', 'Velocidade de leitura (MB/s)', ['device']),
            'write_speed': Gauge('disk_write_speed_mbps', 'Velocidade de escrita (MB/s)', ['device']),
            'iops': Gauge('disk_iops', 'IOPS', ['device']),
            'bad_blocks': Gauge('disk_bad_blocks', 'Bad blocks', ['device']),
            'power_on_hours': Gauge('disk_power_on_hours', 'Horas ligado', ['device'])
        }
        
        self.servidor_started = False
    
    def start(self, port: int = 9090):
        """Inicia servidor Prometheus"""
        if not self.servidor_started:
            start_http_server(port)
            self.servidor_started = True
            logger.info(f"Prometheus exporter iniciado na porta {port}")
    
    def update_metrics(self, device: str, metrics: Dict):
        """Atualiza métricas"""
        device_label = device.replace('/', '_')
        
        for key, gauge in self.metrics.items():
            value = metrics.get(key, 0)
            if isinstance(value, (int, float)):
                gauge.labels(device=device_label).set(value)

prometheus_exporter = PrometheusExporter()

