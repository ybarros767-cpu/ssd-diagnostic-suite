"""
Suporte Completo para NVMe
Implementa nvme smart-log, nvme id-ctrl, nvme error-log
"""
import subprocess
import json
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)

class NVMESupport:
    """Suporte completo para dispositivos NVMe"""
    
    def __init__(self):
        self.nvme_available = self._check_nvme_cli()
    
    def _check_nvme_cli(self) -> bool:
        """Verifica se NVMe CLI está disponível"""
        try:
            result = subprocess.run(['nvme', '--version'], capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except:
            return False
    
    def is_nvme_device(self, device_path: str) -> bool:
        """Verifica se dispositivo é NVMe"""
        return device_path.startswith('/dev/nvme')
    
    def get_smart_log(self, device_path: str) -> Optional[Dict]:
        """Executa nvme smart-log"""
        if not self.nvme_available or not self.is_nvme_device(device_path):
            return None
        
        try:
            result = subprocess.run(
                ['nvme', 'smart-log', device_path, '--json'],
                capture_output=True, text=True, timeout=10
            )
            
            if result.returncode == 0:
                return json.loads(result.stdout)
            else:
                logger.warning(f"nvme smart-log falhou: {result.stderr}")
                return None
        except Exception as e:
            logger.error(f"Erro ao executar nvme smart-log: {e}")
            return None
    
    def get_id_ctrl(self, device_path: str) -> Optional[Dict]:
        """Executa nvme id-ctrl"""
        if not self.nvme_available or not self.is_nvme_device(device_path):
            return None
        
        try:
            result = subprocess.run(
                ['nvme', 'id-ctrl', device_path, '--json'],
                capture_output=True, text=True, timeout=10
            )
            
            if result.returncode == 0:
                return json.loads(result.stdout)
            else:
                logger.warning(f"nvme id-ctrl falhou: {result.stderr}")
                return None
        except Exception as e:
            logger.error(f"Erro ao executar nvme id-ctrl: {e}")
            return None
    
    def get_error_log(self, device_path: str) -> Optional[Dict]:
        """Executa nvme error-log"""
        if not self.nvme_available or not self.is_nvme_device(device_path):
            return None
        
        try:
            result = subprocess.run(
                ['nvme', 'error-log', device_path, '--json'],
                capture_output=True, text=True, timeout=10
            )
            
            if result.returncode == 0:
                return json.loads(result.stdout)
            else:
                logger.warning(f"nvme error-log falhou: {result.stderr}")
                return None
        except Exception as e:
            logger.error(f"Erro ao executar nvme error-log: {e}")
            return None
    
    def get_complete_nvme_info(self, device_path: str) -> Dict:
        """Obtém todas informações NVMe"""
        if not self.is_nvme_device(device_path):
            return {'nvme_device': False}
        
        return {
            'nvme_device': True,
            'smart_log': self.get_smart_log(device_path),
            'id_ctrl': self.get_id_ctrl(device_path),
            'error_log': self.get_error_log(device_path),
            'nvme_cli_available': self.nvme_available
        }

nvme_support = NVMESupport()

