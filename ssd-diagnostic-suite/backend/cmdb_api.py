"""
API REST para integração com CMDB (Configuration Management Database)
Expõe dados de dispositivos em formato padronizado para CMDB
"""
import logging
from typing import Dict, List, Optional
from datetime import datetime
from fastapi import APIRouter, HTTPException

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/cmdb", tags=["CMDB"])

class CMDBAPI:
    """API para integração com CMDB"""
    
    def __init__(self):
        self.device_registry = {}
    
    def format_device_for_cmdb(self, device: Dict, metrics: Dict) -> Dict:
        """Formata device no formato CMDB padrão"""
        return {
            'ci_type': 'storage_device',
            'ci_id': device.get('path', '').replace('/', '_'),
            'attributes': {
                'model': device.get('model', 'Unknown'),
                'path': device.get('path', ''),
                'bus': device.get('bus', 'Unknown'),
                'size': device.get('size', ''),
                'type': device.get('type', ''),
                'health_percent': metrics.get('health', 0),
                'temperature_celsius': metrics.get('temperature', 0),
                'wear_level_percent': metrics.get('wear_level', 0),
                'power_on_hours': metrics.get('power_on_hours', 0),
                'bad_blocks': metrics.get('bad_blocks', 0),
                'last_scan': datetime.now().isoformat(),
                'status': self._determine_status(metrics)
            },
            'relationships': [],
            'tags': ['ssd-diagnostic-suite', device.get('bus', '').lower()]
        }
    
    def _determine_status(self, metrics: Dict) -> str:
        """Determina status do dispositivo"""
        health = metrics.get('health', 0)
        if health >= 95:
            return 'operational'
        elif health >= 80:
            return 'degraded'
        elif health >= 60:
            return 'warning'
        else:
            return 'critical'
    
    def get_devices_as_ci(self, devices: List[Dict], metrics: Dict) -> List[Dict]:
        """Retorna todos devices no formato CMDB"""
        return [
            self.format_device_for_cmdb(device, metrics) 
            for device in devices
        ]
    
    def get_device_ci(self, device_path: str, metrics: Dict) -> Optional[Dict]:
        """Retorna device específico no formato CMDB"""
        device = {
            'path': device_path,
            'model': metrics.get('model', 'Unknown'),
            'bus': metrics.get('bus', 'Unknown'),
            'size': metrics.get('size', ''),
            'type': metrics.get('type', '')
        }
        return self.format_device_for_cmdb(device, metrics)

cmdb_api = CMDBAPI()

@router.get("/devices")
async def get_devices_cmdb_format():
    """Retorna todos dispositivos no formato CMDB"""
    # Implementar com dados reais do sistema
    return {"devices": [], "format": "CMDB v1.0"}

@router.get("/device/{device_path}")
async def get_device_cmdb(device_path: str):
    """Retorna dispositivo específico no formato CMDB"""
    return {"error": "Not implemented", "device_path": device_path}

@router.post("/sync")
async def sync_to_cmdb():
    """Sincroniza dados com CMDB externo"""
    return {"status": "sync_initiated", "message": "CMDB sync not implemented yet"}

