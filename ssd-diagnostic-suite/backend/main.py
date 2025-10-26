from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import json
import psutil
import pyudev
from typing import Dict, List
import subprocess
import time
import logging
from datetime import datetime
import numpy as np

app = FastAPI()

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SSDMonitor:
    def __init__(self):
        self.connected_clients: List[WebSocket] = []
        self.monitoring: bool = False
        self.device_path: str = None
        self.thermal_data: List[Dict] = []
        self.performance_data: List[Dict] = []
        
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.connected_clients.append(websocket)
        
    def disconnect(self, websocket: WebSocket):
        self.connected_clients.remove(websocket)
        
    async def broadcast(self, data: Dict):
        for client in self.connected_clients:
            try:
                await client.send_json(data)
            except Exception as e:
                logger.error(f"Error broadcasting to client: {e}")
                
    def get_smart_data(self) -> Dict:
        if not self.device_path:
            return {}
        
        try:
            cmd = f"smartctl -a -j {self.device_path}"
            result = subprocess.run(cmd.split(), capture_output=True, text=True)
            return json.loads(result.stdout)
        except Exception as e:
            logger.error(f"Error getting SMART data: {e}")
            return {}
            
    def get_performance_metrics(self) -> Dict:
        if not self.device_path:
            return {}
            
        try:
            # Get disk IO statistics
            disk_io = psutil.disk_io_counters(perdisk=True)
            device_name = self.device_path.split('/')[-1]
            if device_name in disk_io:
                stats = disk_io[device_name]
                return {
                    'read_bytes': stats.read_bytes,
                    'write_bytes': stats.write_bytes,
                    'read_count': stats.read_count,
                    'write_count': stats.write_count,
                    'read_time': stats.read_time,
                    'write_time': stats.write_time,
                    'timestamp': datetime.now().isoformat()
                }
        except Exception as e:
            logger.error(f"Error getting performance metrics: {e}")
        return {}

    async def monitor_device(self):
        while self.monitoring:
            try:
                # Get SMART data
                smart_data = self.get_smart_data()
                
                # Get performance metrics
                perf_metrics = self.get_performance_metrics()
                
                # Update data history
                if smart_data:
                    self.thermal_data.append({
                        'timestamp': datetime.now().isoformat(),
                        'temperature': smart_data.get('temperature', {}).get('current', 0)
                    })
                
                if perf_metrics:
                    self.performance_data.append(perf_metrics)
                
                # Keep only last hour of data
                cutoff = len(self.thermal_data) - 3600
                if cutoff > 0:
                    self.thermal_data = self.thermal_data[cutoff:]
                    self.performance_data = self.performance_data[cutoff:]
                
                # Calculate real-time analytics
                analytics = self.calculate_analytics()
                
                # Broadcast update
                await self.broadcast({
                    'type': 'update',
                    'smart': smart_data,
                    'performance': perf_metrics,
                    'analytics': analytics,
                    'timestamp': datetime.now().isoformat()
                })
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                
            await asyncio.sleep(1)  # Update every second
            
    def calculate_analytics(self) -> Dict:
        """Calculate real-time analytics from collected data"""
        if not self.thermal_data or not self.performance_data:
            return {}
            
        try:
            # Temperature analysis
            temps = [d['temperature'] for d in self.thermal_data]
            temp_analytics = {
                'current': temps[-1],
                'min': min(temps),
                'max': max(temps),
                'avg': np.mean(temps),
                'trend': np.polyfit(range(len(temps[-60:])), temps[-60:], 1)[0]  # Last minute trend
            }
            
            # Performance analysis
            read_speeds = []
            write_speeds = []
            for i in range(1, len(self.performance_data)):
                time_diff = (datetime.fromisoformat(self.performance_data[i]['timestamp']) - 
                           datetime.fromisoformat(self.performance_data[i-1]['timestamp'])).total_seconds()
                if time_diff > 0:
                    read_speed = (self.performance_data[i]['read_bytes'] - 
                                self.performance_data[i-1]['read_bytes']) / time_diff
                    write_speed = (self.performance_data[i]['write_bytes'] - 
                                 self.performance_data[i-1]['write_bytes']) / time_diff
                    read_speeds.append(read_speed)
                    write_speeds.append(write_speed)
            
            perf_analytics = {
                'read_speed': {
                    'current': read_speeds[-1] if read_speeds else 0,
                    'avg': np.mean(read_speeds) if read_speeds else 0,
                    'max': max(read_speeds) if read_speeds else 0
                },
                'write_speed': {
                    'current': write_speeds[-1] if write_speeds else 0,
                    'avg': np.mean(write_speeds) if write_speeds else 0,
                    'max': max(write_speeds) if write_speeds else 0
                }
            }
            
            return {
                'temperature': temp_analytics,
                'performance': perf_analytics
            }
            
        except Exception as e:
            logger.error(f"Error calculating analytics: {e}")
            return {}

monitor = SSDMonitor()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await monitor.connect(websocket)
    try:
        while True:
            data = await websocket.receive_json()
            if data['type'] == 'start_monitoring':
                monitor.device_path = data['device_path']
                monitor.monitoring = True
                asyncio.create_task(monitor.monitor_device())
            elif data['type'] == 'stop_monitoring':
                monitor.monitoring = False
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        monitor.disconnect(websocket)

@app.get("/devices")
async def list_devices():
    """List available storage devices"""
    devices = []
    context = pyudev.Context()
    
    for device in context.list_devices(subsystem='block', DEVTYPE='disk'):
        if device.get('ID_BUS') in ['usb', 'ata', 'scsi']:
            devices.append({
                'path': device.device_node,
                'model': device.get('ID_MODEL', ''),
                'serial': device.get('ID_SERIAL', ''),
                'bus': device.get('ID_BUS', ''),
                'size': device.get('size', 0)
            })
    
    return devices

@app.get("/device/{device_path}/smart")
async def get_smart(device_path: str):
    """Get SMART data for specific device"""
    monitor.device_path = device_path
    return monitor.get_smart_data()

@app.get("/device/{device_path}/benchmark")
async def run_benchmark(device_path: str):
    """Run basic benchmark on device"""
    try:
        # Run fio benchmark
        cmd = [
            "fio", "--name=benchmark", f"--filename={device_path}",
            "--direct=1", "--rw=randrw", "--bs=4k",
            "--size=100m", "--runtime=30", "--numjobs=4",
            "--group_reporting", "--output-format=json"
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        return json.loads(result.stdout)
    except Exception as e:
        logger.error(f"Benchmark error: {e}")
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)