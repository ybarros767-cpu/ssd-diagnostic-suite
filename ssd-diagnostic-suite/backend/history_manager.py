"""
Sistema de Histórico de Execuções com Comparativo de Saúde
Armazena histórico de diagnósticos para análise temporal
"""
import json
import os
import logging
from typing import Dict, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class HistoryManager:
    """Gerencia histórico de execuções de diagnóstico"""
    
    def __init__(self, history_file: str = 'diagnostic_history.json'):
        self.history_file = history_file
        self.history_dir = '/app/history'
        os.makedirs(self.history_dir, exist_ok=True)
        
    def save_execution(self, device_path: str, results: Dict) -> str:
        """Salva execução no histórico"""
        timestamp = datetime.now().isoformat()
        entry = {
            'timestamp': timestamp,
            'device': device_path,
            'model': results.get('device', {}).get('model', 'Unknown'),
            'health': results.get('metrics', {}).get('health', 0),
            'wear_level': results.get('metrics', {}).get('wear_level', 0),
            'temperature': results.get('metrics', {}).get('temperature', 0),
            'read_speed': results.get('metrics', {}).get('read_speed', 0),
            'write_speed': results.get('metrics', {}).get('write_speed', 0),
            'power_on_hours': results.get('metrics', {}).get('power_on_hours', 0),
            'bad_blocks': results.get('metrics', {}).get('bad_blocks', 0),
            'full_results': results
        }
        
        file_path = os.path.join(self.history_dir, f"{device_path.replace('/', '_')}_{timestamp}.json")
        
        try:
            with open(file_path, 'w') as f:
                json.dump(entry, f, indent=2)
            logger.info(f"Execução salva: {file_path}")
            return file_path
        except Exception as e:
            logger.error(f"Erro ao salvar histórico: {e}")
            return ""
    
    def get_history(self, device_path: Optional[str] = None) -> List[Dict]:
        """Recupera histórico de execuções"""
        history = []
        
        try:
            for filename in os.listdir(self.history_dir):
                if filename.endswith('.json'):
                    file_path = os.path.join(self.history_dir, filename)
                    with open(file_path, 'r') as f:
                        entry = json.load(f)
                        if not device_path or entry.get('device') == device_path:
                            history.append(entry)
            
            # Ordenar por timestamp
            history.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
            return history
        except Exception as e:
            logger.error(f"Erro ao ler histórico: {e}")
            return []
    
    def get_comparative_analysis(self, device_path: str) -> Dict:
        """Gera análise comparativa do histórico"""
        history = self.get_history(device_path)
        
        if len(history) < 2:
            return {
                'available': False,
                'message': 'Histórico insuficiente para comparação (mínimo 2 execuções)'
            }
        
        # Última execução vs penúltima
        latest = history[0]
        previous = history[1]
        
        health_trend = latest['health'] - previous['health']
        wear_trend = latest['wear_level'] - previous['wear_level']
        temp_trend = latest['temperature'] - previous['temperature']
        
        return {
            'available': True,
            'total_executions': len(history),
            'latest_date': latest['timestamp'],
            'previous_date': previous['timestamp'],
            'health_trend': health_trend,
            'wear_trend': wear_trend,
            'temperature_trend': temp_trend,
            'power_on_hours_increase': latest['power_on_hours'] - previous['power_on_hours'],
            'bad_blocks_increase': latest['bad_blocks'] - previous['bad_blocks'],
            'assessment': self._assess_trend(health_trend, wear_trend)
        }
    
    def _assess_trend(self, health_trend: float, wear_trend: float) -> str:
        """Avalia tendências de saúde"""
        if health_trend < -5 or wear_trend > 5:
            return "⚠️ Degradação detectada - Monitoramento urgente recomendado"
        elif health_trend < -2 or wear_trend > 2:
            return "⚠️ Degradação leve detectada - Continue monitorando"
        else:
            return "✅ Estável - Sem degradação significativa detectada"

history_manager = HistoryManager()

