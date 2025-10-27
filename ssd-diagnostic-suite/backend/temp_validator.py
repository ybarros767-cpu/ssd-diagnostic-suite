"""
Validador de Temperatura com Detecção de Bridge e Fallback
Implementa leitura precisa de temperatura com validação
"""
import subprocess
import re
import logging
from typing import Dict, Tuple, Optional

logger = logging.getLogger(__name__)

class TemperatureValidator:
    """Valida e corrige leituras de temperatura"""
    
    def __init__(self):
        # Bridges USB conhecidos que não reportam temperatura confiável
        self.unreliable_bridges = [
            'JMicron', 'ASMedia', 'VIA Labs', 'Genesys Logic', 
            'Alcor Micro', 'Renesas', 'Fresco Logic'
        ]
    
    def get_bridge_info(self, device_path: str) -> Dict:
        """Identifica bridge USB do dispositivo"""
        try:
            # Extrair nome do device (ex: /dev/sdb -> sdb)
            device_name = device_path.split('/')[-1]
            
            # Usar lsusb para identificar interface
            result = subprocess.run(
                ['lsusb'], capture_output=True, text=True, timeout=5
            )
            
            bridge_info = {
                'manufacturer': 'Unknown',
                'is_unreliable': False,
                'detected': False
            }
            
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    for bridge in self.unreliable_bridges:
                        if bridge.lower() in line.lower():
                            bridge_info['manufacturer'] = bridge
                            bridge_info['is_unreliable'] = True
                            bridge_info['detected'] = True
                            logger.info(f"Bridge USB detectada: {bridge} (temperatura não confiável)")
                            break
            
            return bridge_info
        except Exception as e:
            logger.error(f"Error getting bridge info: {e}")
            return {'manufacturer': 'Unknown', 'is_unreliable': False, 'detected': False}
    
    def validate_temperature(self, temp: float, device_path: str, bus: str) -> Dict:
        """
        Valida leitura de temperatura
        Returns: {
            'value': float,
            'is_valid': bool,
            'confidence': float,
            'warning': str,
            'source': str
        }
        """
        result = {
            'value': temp,
            'is_valid': True,
            'confidence': 1.0,
            'warning': None,
            'source': 'SMART'
        }
        
        # USB precisa validação especial
        if bus == 'USB':
            bridge_info = self.get_bridge_info(device_path)
            
            if bridge_info['is_unreliable']:
                result['confidence'] = 0.3
                result['warning'] = f"⚠️ Temperatura não confiável (bridge USB {bridge_info['manufacturer']} sem suporte SMART térmico)"
                result['is_valid'] = False
                
                # Tentar fallback: ler do hwmon do sistema
                system_temp = self._read_system_temp(device_path)
                if system_temp:
                    result['value'] = system_temp
                    result['source'] = 'System HWMON'
                    result['confidence'] = 0.6
                else:
                    result['value'] = None
                    result['warning'] = "⚠️ Temperatura não disponível para dispositivos USB"
        
        # Validações de faixa esperada
        elif temp < 0 or temp > 125:
            result['is_valid'] = False
            result['confidence'] = 0.1
            result['warning'] = f"⚠️ Temperatura fora da faixa esperada: {temp}°C"
            
            # Tentar ler raw value e senseu Sem
            corrected = self._read_raw_temperature(device_path)
            if corrected:
                result['value'] = corrected
                result['source'] = 'Raw SMART'
                result['confidence'] = 0.7
        
        elif temp < 20:
            # Temperaturas muito baixas podem ser valores não convertidos
            result['warning'] = "⚠️ Temperatura anormalmente baixa - pode ser valor não convertido"
            result['confidence'] = 0.7
        
        return result
    
    def _read_system_temp(self, device_path: str) -> Optional[float]:
        """Tenta ler temperatura do sistema hwmon"""
        try:
            device_name = device_path.split('/')[-1]
            
            # Tentar caminhos comuns de hwmon
            temp_paths = [
                f'/sys/block/{device_name}/<｜place▁holder▁no▁450｜>/hwmon/hwmon*/temp1_input',
                f'/sys/block/{device_name}/queue/hw_sector_size',  # Indiretamente
            ]
            
            # Usar find para localizar arquivos temp
            result = subprocess.run(
                ['find', f'/sys/block/{device_name}', '-name', 'temp1_input', '2>/dev/null'],
                capture_output=True, text=True, timeout=5
            )
            
            if result.returncode == 0 and result.stdout.strip():
                temp_file = result.stdout.strip().split('\n')[0]
                with open(temp_file, 'r') as f:
                    temp_millic = int(f.read().strip())
                    temp_celsius = temp_millic / 1000.0
                    logger.info(f"Leitura do sistema hwmon: {temp_celsius}°C")
                    return temp_celsius
            
            return None
        except Exception as e:
            logger.debug(f"Could not read system temp: {e}")
            return None
    
    def _read_raw_temperature(self, device_path: str) -> Optional[float]:
        """Lê temperatura diretamente de smartctl sem JSON"""
        try:
            result = subprocess.run(
                ['smartctl', '-A', device_path],
                capture_output=True, text=True, timeout=10
            )
            
            if result.returncode == 0:
                # Procurar linha de temperatura
                for line in result.stdout.split('\n'):
                    if 'Temperature' in line or 'Airflow' in line:
                        # Extrair número
                        match = re.search(r'(\d+)\s*(?:degree|°|Celsius)', line, re.IGNORECASE)
                        if match:
                            temp = float(match.group(1))
                            logger.info(f"Raw temperature: {temp}°C from line")
                            return temp
                        
                        # Alternativa: procurar padrão de valor
                        match = re.search(r'\b(1[0-9]{2}|[2-9][0-9])\b', line)
                        if match and 20 <= int(match.group(1)) <= 100:
                            return float(match.group(1))
            
            return None
        except Exception as e:
            logger.debug(f"Could not read raw temp: {e}")
            return None

def validate_and_correct_temperature(temp: float, device_path: str, bus: str) -> Dict:
    """Função helper"""
    validator = TemperatureValidator()
    return validator.validate_temperature(temp, device_path, bus)

