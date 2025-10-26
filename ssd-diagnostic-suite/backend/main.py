from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import asyncio
import json
import psutil
import pyudev
from typing import Dict, List, Optional
import subprocess
import time
import logging
from datetime import datetime
import numpy as np
import os
import socketio

app = FastAPI(
    title="SSD Diagnostic Suite API",
    description="API para diagnóstico de SSD em tempo real",
    version="1.0.0"
)

# CORS configuration
env_app = os.environ.get("APP_ENV", "development")
env_origins = os.environ.get("ALLOWED_ORIGINS", "")
if env_origins:
    allow_origins = [o.strip() for o in env_origins.split(",") if o.strip()]
else:
    allow_origins = ["*"] if env_app != "production" else []

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Socket.IO server
sio = socketio.AsyncServer(cors_allowed_origins=allow_origins, async_mode='asgi')
socket_app = socketio.ASGIApp(sio, app)

# Monitor state
monitor = {
    'running': False,
    'phase': None,
    'progress': 0,
    'message': 'Aguardando...',
    'device_path': None,
    'results': {}
}

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
        logger.info(f"Client connected. Total clients: {len(self.connected_clients)}")
        
    def disconnect(self, websocket: WebSocket):
        if websocket in self.connected_clients:
            self.connected_clients.remove(websocket)
            logger.info(f"Client disconnected. Total clients: {len(self.connected_clients)}")
        
    async def broadcast(self, data: Dict):
        for client in self.connected_clients[:]:  # copy list to avoid modification during iteration
            try:
                await client.send_json(data)
            except Exception as e:
                logger.error(f"Error broadcasting to client: {e}")
                self.disconnect(client)

ssd_monitor = SSDMonitor()

@sio.event
async def connect(sid, environ):
    logger.info(f"Socket.IO client connected: {sid}")
    await emit_status()

@sio.event
async def disconnect(sid):
    logger.info(f"Socket.IO client disconnected: {sid}")

async def emit_status():
    """Broadcast current status to all connected clients"""
    await sio.emit('status', {
        'phase': monitor['phase'],
        'progress': monitor['progress'],
        'message': monitor['message']
    })

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await ssd_monitor.connect(websocket)
    try:
        while True:
            data = await websocket.receive_json()
            if data.get('type') == 'start_monitoring':
                ssd_monitor.device_path = data.get('device_path')
                ssd_monitor.monitoring = True
                asyncio.create_task(ssd_monitor.monitor_device())
            elif data.get('type') == 'stop_monitoring':
                ssd_monitor.monitoring = False
    except WebSocketDisconnect:
        logger.info("WebSocket client disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        ssd_monitor.disconnect(websocket)

@app.post("/run")
async def start_diagnostic():
    """Inicia o diagnóstico de SSD"""
    if monitor['running']:
        return JSONResponse(
            status_code=400,
            content={"error": "Diagnóstico já em execução"}
        )
    
    try:
        monitor['running'] = True
        monitor['phase'] = 'smart'
        monitor['progress'] = 0
        monitor['message'] = 'Iniciando diagnóstico...'
        
        await emit_status()
        
        # Simula execução do diagnóstico em background
        asyncio.create_task(run_diagnostic())
        
        return {"status": "started", "message": "Diagnóstico iniciado"}
    except Exception as e:
        logger.error(f"Error starting diagnostic: {e}")
        monitor['running'] = False
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )

async def run_diagnostic():
    """Executa o diagnóstico de forma assíncrona"""
    try:
        # Fase 1: Coleta SMART
        monitor['phase'] = 'smart'
        monitor['progress'] = 10
        monitor['message'] = 'Coletando dados SMART...'
        await emit_status()
        await asyncio.sleep(2)
        
        # Fase 2: Teste de Leitura
        monitor['phase'] = 'read'
        monitor['progress'] = 40
        monitor['message'] = 'Executando teste de leitura...'
        await emit_status()
        await asyncio.sleep(3)
        
        # Fase 3: Teste de Escrita
        monitor['phase'] = 'write'
        monitor['progress'] = 70
        monitor['message'] = 'Executando teste de escrita...'
        await emit_status()
        await asyncio.sleep(3)
        
        # Fase 4: Relatório
        monitor['phase'] = 'report'
        monitor['progress'] = 90
        monitor['message'] = 'Gerando relatório...'
        await emit_status()
        await asyncio.sleep(2)
        
        monitor['progress'] = 100
        monitor['message'] = 'Diagnóstico concluído!'
        await emit_status()
        
        await sio.emit('phase_done', 'report')
        
    except Exception as e:
        logger.error(f"Error in diagnostic: {e}")
        monitor['message'] = f'Erro: {str(e)}'
    finally:
        monitor['running'] = False

@app.get("/report")
async def get_report():
    """Retorna o relatório de diagnóstico"""
    return {
        "status": "completed" if monitor['progress'] == 100 else "in_progress",
        "progress": monitor['progress'],
        "message": monitor['message'],
        "results": monitor.get('results', {})
    }

@app.get("/devices")
async def list_devices():
    """List available storage devices"""
    devices = []
    try:
        context = pyudev.Context()
        
        for device in context.list_devices(subsystem='block', DEVTYPE='disk'):
            if device.get('ID_BUS') in ['usb', 'ata', 'scsi']:
                size = device.get('size.bytes', 0)
                devices.append({
                    'path': device.device_node,
                    'model': device.get('ID_MODEL', 'Unknown'),
                    'serial': device.get('ID_SERIAL', 'Unknown'),
                    'bus': device.get('ID_BUS', 'Unknown'),
                    'size': size if size else device.get('size', '0')
                })
    except Exception as e:
        logger.error(f"Error listing devices: {e}")
    
    return devices

@app.get("/device/{device_path:path}/smart")
async def get_smart(device_path: str):
    """Get SMART data for specific device"""
    try:
        cmd = f"smartctl -a -j {device_path}"
        result = subprocess.run(cmd.split(), capture_output=True, text=True)
        if result.returncode == 0:
            return json.loads(result.stdout)
        else:
            return {"error": "Failed to get SMART data", "output": result.stderr}
    except Exception as e:
        logger.error(f"Error getting SMART data: {e}")
        return {"error": str(e)}

@app.get("/health")
def health():
    """Healthcheck endpoint"""
    return {"status": "ok", "running": monitor['running']}

@app.get("/")
def root():
    return {
        "status": "ok",
        "service": "SSD Diagnostic Suite API",
        "message": "Backend ativo e pronto para uso.",
        "version": "1.0.0",
        "endpoints": {
            "docs": "/docs",
            "health": "/health",
            "run": "/run (POST)",
            "report": "/report",
            "devices": "/devices"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
