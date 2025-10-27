"""
Base de Dados de Benchmarks por Modelo
Compara performance atual com benchmarks de referência
"""
import json
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)

class BenchmarkDatabase:
    """Base de dados de benchmarks por modelo de SSD/HD"""
    
    def __init__(self):
        self.benchmarks = {
            # SSDs SATA
            'kingston sa400': {
                'model': 'Kingston SA400',
                'type': 'SSD',
                'interface': 'SATA III',
                'benchmarks': {
                    'read_speed': {'avg': 450, 'max': 550},
                    'write_speed': {'avg': 320, 'max': 450},
                    'iops_read': {'avg': 75000, 'max': 95000},
                    'iops_write': {'avg': 55000, 'max': 80000},
                    'latency': {'avg': 0.1, 'max': 0.3}
                }
            },
            'samsung 870 evo': {
                'model': 'Samsung 870 EVO',
                'type': 'SSD',
                'interface': 'SATA III',
                'benchmarks': {
                    'read_speed': {'avg': 560, 'max': 600},
                    'write_speed': {'avg': 530, 'max': 580},
                    'iops_read': {'avg': 100000, 'max': 120000},
                    'iops_write': {'avg': 90000, 'max': 110000},
                    'latency': {'avg': 0.08, 'max': 0.2}
                }
            },
            # SSDs NVMe
            'samsung 980 pro': {
                'model': 'Samsung 980 PRO',
                'type': 'SSD',
                'interface': 'NVMe PCIe 4.0',
                'benchmarks': {
                    'read_speed': {'avg': 6900, 'max': 7500},
                    'write_speed': {'avg': 5000, 'max': 5500},
                    'iops_read': {'avg': 1000000, 'max': 1200000},
                    'iops_write': {'avg': 800000, 'max': 1000000},
                    'latency': {'avg': 0.02, 'max': 0.05}
                }
            },
            # HDs
            'generic hdd': {
                'model': 'Generic HDD',
                'type': 'HDD',
                'interface': 'SATA III',
                'benchmarks': {
                    'read_speed': {'avg': 180, 'max': 220},
                    'write_speed': {'avg': 160, 'max': 200},
                    'iops_read': {'avg': 150, 'max': 200},
                    'iops_write': {'avg': 120, 'max': 180},
                    'latency': {'avg': 12, 'max': 20}
                }
            }
        }
    
    def find_benchmark(self, model_name: str) -> Optional[Dict]:
        """Encontra benchmark para modelo específico"""
        model_lower = model_name.lower()
        
        # Busca exata
        if model_lower in self.benchmarks:
            return self.benchmarks[model_lower]
        
        # Busca parcial
        for key, benchmark in self.benchmarks.items():
            if key in model_lower or model_lower in key:
                return benchmark
        
        return None
    
    def compare_performance(self, model_name: str, current_metrics: Dict) -> Dict:
        """Compara performance atual com benchmark"""
        benchmark = self.find_benchmark(model_name)
        
        if not benchmark:
            return {
                'available': False,
                'message': f'Nenhum benchmark disponível para {model_name}'
            }
        
        bench = benchmark['benchmarks']
        comparison = {
            'available': True,
            'model': benchmark['model'],
            'type': benchmark['type'],
            'interface': benchmark['interface'],
            'read_speed': {
                'current': current_metrics.get('read_speed', 0),
                'benchmark_avg': bench['read_speed']['avg'],
                'benchmark_max': bench['read_speed']['max'],
                'percent_of_max': round((current_metrics.get('read_speed', 0) / bench['read_speed']['max']) * 100, 1)
            },
            'write_speed': {
                'current': current_metrics.get('write_speed', 0),
                'benchmark_avg': bench['write_speed']['avg'],
                'benchmark_max': bench['write_speed']['max'],
                'percent_of_max': round((current_metrics.get('write_speed', 0) / bench['write_speed']['max']) * 100, 1)
            },
            'iops': {
                'current': current_metrics.get('iops', 0),
                'benchmark_avg': bench['iops_read']['avg'],
                'benchmark_max': bench['iops_read']['max'],
                'percent_of_max': round((current_metrics.get('iops', 0) / bench['iops_read']['max']) * 100, 1)
            }
        }
        
        # Avaliação geral
        avg_percent = (comparison['read_speed']['percent_of_max'] + comparison['write_speed']['percent_of_max']) / 2
        
        if avg_percent >= 95:
            comparison['assessment'] = 'Excelente - Operando no máximo esperado'
        elif avg_percent >= 80:
            comparison['assessment'] = 'Bom - Performance adequada'
        elif avg_percent >= 60:
            comparison['assessment'] = 'Moderado - Abaixo do esperado'
        else:
            comparison['assessment'] = 'Ruim - Performance comprometida'
        
        return comparison

benchmark_db = BenchmarkDatabase()

