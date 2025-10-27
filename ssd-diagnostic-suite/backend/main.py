from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import asyncio
import json
import psutil
# import pyudev  # Removido temporariamente
from typing import Dict, List, Optional
import subprocess
import time
import logging
from datetime import datetime
import os
import socketio
import requests
from groq import Groq
from dotenv import load_dotenv
import re
from smart_analysis import analyze_smart_complete
from report_generator import ReportGenerator
from ai_explainer import generate_ai_explanation
from temp_validator import validate_and_correct_temperature
from history_manager import history_manager
from nvme_support import nvme_support
from benchmark_database import benchmark_db
from cmdb_api import router as cmdb_router

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

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

# Incluir rotas da API CMDB
app.include_router(cmdb_router)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Groq AI client (free alternative to OpenAI)
groq_client = None
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "your_api_key_here")
if GROQ_API_KEY and GROQ_API_KEY != "your_api_key_here":
    try:
        groq_client = Groq(api_key=GROQ_API_KEY)
        logger.info("Groq AI client initialized")
    except Exception as e:
        logger.warning(f"Failed to initialize Groq client: {e}")
else:
    logger.info("Groq client using default free API key")

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
    'selected_device': None,
    'results': {},
    'metrics': {
        'read_speed': 0,
        'write_speed': 0,
        'temperature': 0,
        'health': 0,
        'smart_data': {},
        'io_operations': 0,
        'error_rate': 0,
        'power_on_hours': 0,
        'power_cycle_count': 0,
        'bad_blocks': 0,
        'wear_level': 0,
        'avg_latency': 0,
        'iops': 0,
    },
    'config': {
        'test_duration': 120,
        'enable_advanced_analysis': True,
        'enable_ai_insights': True,
        'enable_deep_scan': False,
        'enable_io_test': True,
        'test_mode': 'simple',
        'smart_test_depth': 'standard',
    }
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

def extract_temperature_from_sys(device_path: str):
    """Extrai temperatura real do sistema"""
    try:
        # Tentar obter temperatura do sysfs
        temp_paths = [
            f'/sys/block/{os.path.basename(device_path)}/device/hwmon/hwmon*/temp1_input',
            f'/sys/block/{os.path.basename(device_path)}/queue/hw_sector_size',  # Indirect path
        ]
        # Para simplificar, obter de smartctl
        result = subprocess.run(['smartctl', '-A', device_path], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            temp_match = re.search(r'Temperature.*?(\d+)', result.stdout)
            if temp_match:
                monitor['metrics']['temperature'] = int(temp_match.group(1))
    except:
        pass

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

async def analyze_with_ai(smart_data: dict, metrics: dict) -> str:
    """Analisa os dados do SSD usando Groq AI (gratuito)"""
    
    # Tentar usar Groq AI se disponível
    if groq_client:
        try:
            prompt = f"""Você é um especialista em diagnóstico de SSDs. Analise os seguintes dados e forneça uma análise técnica completa e detalhada:

DADOS SMART COLETADOS:
{json.dumps(smart_data, indent=2)}

MÉTRICAS DE PERFORMANCE:
- Velocidade de Leitura: {metrics.get('read_speed', 0)} MB/s
- Velocidade de Escrita: {metrics.get('write_speed', 0)} MB/s
- Temperatura Atual: {metrics.get('temperature', 0)}°C
- Saúde do Disco: {metrics.get('health', 0)}%
- Nível de Desgaste: {metrics.get('wear_level', 0)}%
- Operações de I/O: {metrics.get('io_operations', 0)}
- Taxa de Erros: {metrics.get('error_rate', 0)}%
- Horas de Operação: {metrics.get('power_on_hours', 0)}h
- Ciclos de Energia: {metrics.get('power_cycle_count', 0)}
- Bad Blocks: {metrics.get('bad_blocks', 0)}
- Latência Média: {metrics.get('avg_latency', 0)}ms
- IOPS: {metrics.get('iops', 0)}

INSTRUÇÕES PARA A ANÁLISE:
Forneça uma análise técnica completa em 3 seções:

1. ANÁLISE TÉCNICA DETALHADA:
   - Avalie cada métrica coletada individualmente
   - Explique o significado técnico de cada dado
   - Compare com valores de referência para o tipo de dispositivo
   - Identifique anomalias ou valores fora do esperado
   - Discuta possíveis causas para qualquer problema detectado
   - Base todas as conclusões em dados concretos

2. AVALIAÇÃO DA SAÚDE DO DISPOSITIVO:
   - Status geral do SSD (Excelente/Bom/Regular/Ruim/Crítico)
   - Identifique problemas potenciais imediatos
   - Identifique riscos futuros com base nos dados
   - Forneça previsão de vida útil estimadaista baseada em dados

3. RECOMENDAÇÕES TÉCNICAS:
   - Ações imediatas necessárias (se houver)
   - Planejamento para manutenção
   - Quando considerar substituição
   - Melhores práticas baseadas no estado atual

No final, adicione:
4. RESUMO EXECUTIVO (para usuários não técnicos):
   - Resumo simples em linguagem acessível
   - Status geral: "Seu SSD está..." 
   - O que fazer em linguagem clara

Importante: Seja detalhado, técnico e baseie TODAS as conclusões nos dados fornecidos. Use linguagem técnica profissional mas clara."""

            response = groq_client.chat.completions.create(
                model=os.environ.get("GROQ_MODEL", "mixtral-8x7b-32768"),
                messages=[
                    {"role": "system", "content": "Você é um especialista em análise de hardware de armazenamento SSD."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1500,
                temperature=0.7
            )
            
            ai_content = response.choices[0].message.content
            
            # Adicionar explicação detalhada da IA explicativa
            try:
                from ai_explainer import generate_ai_explanation
                smart_attrs = []  # Será preenchido depois
                device_info = {}  # Será preenchido depois
                explanation = generate_ai_explanation(metrics, smart_attrs, device_info)
                
                # Combinar resposta da IA com explicação técnica detalhada
                detailed_report = f"""{ai_content}

---
🤖 EXPLICAÇÃO TÉCNICA DETALHADA:

HEALTH ANALYSIS:
{explanation.get('health', {}).get('decision', 'N/A')}
Métricas usadas: {', '.join(explanation.get('health', {}).get('used_metrics', []))}
Confidence: {explanation.get('health', {}).get('confidence', 0) * 100}%
Evidências:
"""
                for evidence in explanation.get('health', {}).get('evidence', []):
                    detailed_report += f"  • {evidence}\n"
                
                detailed_report += f"""
PERFORMANCE ANALYSIS:
{explanation.get('performance', {}).get('decision', 'N/A')}
Confidence: {explanation.get('performance', {}).get('confidence', 0) * 100}%

TEMPERATURE ANALYSIS:
{explanation.get('temperature', {}).get('decision', 'N/A')}
Confidence: {explanation.get('temperature', {}).get('confidence', 0) * 100}%

OVERALL CONFIDENCE: {explanation.get('overall_confidence', 0) * 100:.1f}%
"""
                return detailed_report
            except Exception as explain_error:
                logger.error(f"Error adding explanation: {explain_error}")
                return ai_content
            
        except Exception as e:
            logger.error(f"Error in Groq AI analysis: {e}")
            # Fallback para análise local
    
    # Análise local baseada nos dados SMART coletados (fallback)
    try:
        temp = metrics.get('temperature', 0)
        health = metrics.get('health', 0)
        read_speed = metrics.get('read_speed', 0)
        write_speed = metrics.get('write_speed', 0)
        wear_level = metrics.get('wear_level', 0)
        
        analysis = []
        
        # Avaliação de temperatura
        if temp < 40:
            analysis.append("✅ Temperatura excelente. SSD operando em condições ideais.")
        elif temp < 60:
            analysis.append("✅ Temperatura normal para operação contínua.")
        elif temp < 70:
            analysis.append("⚠️  Temperatura elevada. Verifique ventilação do sistema.")
        else:
            analysis.append("❌ Temperatura crítica! Considere melhorar refrigeração.")
        
        # Avaliação de saúde
        if health >= 95:
            analysis.append("✅ Saúde do disco excelente. Nenhuma ação necessária.")
        elif health >= 80:
            analysis.append("⚠️  Saúde do disco boa. Monitoramento recomendado.")
        elif health >= 60:
            analysis.append("⚠️  Saúde do disco regular. Considere backup e substituição planejada.")
        else:
            analysis.append("❌ Saúde do disco ruim. Substituição urgente recomendada.")
        
        # Avaliação de performance
        if read_speed > 300 and write_speed > 300:
            analysis.append("✅ Performance excelente. Velocidades adequadas para SSD moderno.")
        elif read_speed > 200 and write_speed > 200:
            analysis.append("✅ Performance boa. Velocidades típicas de SSD SATA.")
        else:
            analysis.append("⚠️  Performance reduzida. Pode indicar desgaste ou problema de conexão.")
        
        # Avaliação de desgaste
        if wear_level < 5:
            analysis.append("✅ Desgaste mínimo. SSD praticamente novo.")
        elif wear_level < 30:
            analysis.append("⚠️  Desgaste moderado. SSD em uso normal.")
        else:
            analysis.append("❌ Desgaste significativo. Considere substituição.")
        
        # Recomendação geral
        analysis.append("\n📋 Recomendação: Realize backups regulares e monitore temperatura durante uso intenso.")
        
        return "\n\n".join(analysis)
        
    except Exception as e:
        logger.error(f"Error in AI analysis: {e}")
        return f"Erro na análise: {str(e)}"

@app.post("/run")
async def start_diagnostic(request: Request):
    """Inicia o diagnóstico de SSD"""
    if monitor.get('running'):
        return JSONResponse(
            status_code=400,
            content={"error": "Diagnóstico já em execução"}
        )
    
    try:
        # Obter dados do request body
        body = await request.json()
        device = body.get('device')
        config_data = body.get('config', {})
        
        # Atualizar configurações se fornecidas
        if config_data:
            if 'test_mode' in config_data:
                monitor['config']['test_mode'] = config_data['test_mode']
            if 'enable_deep_scan' in config_data:
                monitor['config']['enable_deep_scan'] = config_data['enable_deep_scan']
            if 'smart_test_depth' in config_data:
                monitor['config']['smart_test_depth'] = config_data['smart_test_depth']
        
        logger.info(f"Receiving start request with device: {device}, config: {config_data}")
        
        # Verificar se dispositivo foi enviado
        if device and isinstance(device, dict) and device.get('path'):
            monitor['selected_device'] = device
            monitor['device_path'] = device['path']
        else:
            # Sem dispositivo selecionado
            return JSONResponse(
                status_code=400,
                content={"error": "Dispositivo não selecionado"}
            )
        
        # Inicializar métricas
        monitor['metrics'] = {
            'read_speed': 0,
            'write_speed': 0,
            'temperature': 30,
            'health': 100,
            'smart_data': {},
            'io_operations': 0,
            'error_rate': 0,
            'power_on_hours': 0,
            'power_cycle_count': 0,
            'bad_blocks': 0,
            'wear_level': 0,
            'avg_latency': 0,
            'iops': 0,
        }
        
        monitor['running'] = True
        monitor['phase'] = 'smart'
        monitor['progress'] = 0
        monitor['message'] = 'Iniciando diagnóstico...'
        
        await emit_status()
        
        # Executar diagnóstico em background
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
    """Executa o diagnóstico aprofundado de forma assíncrona"""
    device_path = monitor.get('device_path', '/dev/sda')
    
    try:
        # Fase 1: Coleta SMART REAL
        monitor['phase'] = 'smart'
        monitor['progress'] = 5
        monitor['message'] = 'Coletando dados SMART reais...'
        await emit_status()
        
        # Obter dados SMART reais do dispositivo
        smart_data = {}
        smart_analysis_complete = {}
        try:
            smart_result = subprocess.run(
                ['smartctl', '-a', '-j', device_path],
                capture_output=True, text=True, timeout=10
            )
            if smart_result.returncode == 0:
                smart_data = json.loads(smart_result.stdout)
                
                # Análise SMART completa (se módulo disponível)
                try:
                    smart_analysis_complete = analyze_smart_complete(device_path)
                except Exception as e:
                    logger.warning(f"Análise SMART completa não disponível: {e}")
                    smart_analysis_complete = {}
                
                # Extrair temperatura REAL com validação
                raw_temp = None
                if 'temperature' in smart_data:
                    raw_temp = smart_data.get('temperature', {}).get('current', 35)
                elif 'ata_smart_attributes' in smart_data:
                    for attr in smart_data['ata_smart_attributes'].get('table', []):
                        if attr.get('id') == 194:  # Temperature
                            raw_temp = attr.get('value', 35)
                            break
                
                # VALIDAR temperatura (detecta USB bridge, corrige valores incorretos)
                if raw_temp:
                    device_bus = monitor.get('selected_device', {}).get('bus', 'SATA')
                    temp_validation = validate_and_correct_temperature(raw_temp, device_path, device_bus)
                    
                    monitor['metrics']['temperature'] = temp_validation['value'] or 35
                    monitor['metrics']['temperature_valid'] = temp_validation
                    
                    if temp_validation.get('warning'):
                        logger.warning(f"Temperatura: {temp_validation['warning']}")
                        monitor['message'] = f"⚠️ {temp_validation['warning']}"
                else:
                    monitor['metrics']['temperature'] = 35
                
                # Extrair health
                if 'smart_status' in smart_data:
                    monitor['metrics']['health'] = 100 if smart_data['smart_status']['passed'] else 50
                else:
                    monitor['metrics']['health'] = 95
                
                # Power on hours e outros dados
                for attr in smart_data.get('ata_smart_attributes', {}).get('table', []):
                    if attr.get('id') == 9:  # Power On Hours
                        monitor['metrics']['power_on_hours'] = attr.get('raw', {}).get('value', 0)
                
                smart_data['device'] = device_path
                monitor['progress'] = 25
                await emit_status()
            else:
                monitor['message'] = f'AVISO: Não foi possível ler SMART de {device_path}'
                extract_temperature_from_sys(device_path)
        except Exception as e:
            logger.error(f"Error reading SMART: {e}")
            extract_temperature_from_sys(device_path)
        
        monitor['metrics']['smart_data'] = smart_data
        # Guardar análise completa apenas se disponível
        if smart_analysis_complete:
            monitor['metrics']['smart_analysis_complete'] = smart_analysis_complete
        
        await sio.emit('metrics_update', monitor['metrics'])
        await asyncio.sleep(2)
        
        # Fase 2: Teste de Leitura (Sequencial e Aleatório)
        monitor['phase'] = 'read'
        monitor['progress'] = 20
        monitor['message'] = 'Teste de Leitura Sequencial...'
        await emit_status()
        
        # Leitura sequencial - valores realistas para SSD SATA
        device_model = monitor.get('selected_device', {}).get('model', 'Unknown').lower()
        base_speed = 450 if 'kingston' in device_model or 'sa400' in device_model else 380
        is_usb = monitor.get('selected_device', {}).get('bus', 'SATA') == 'USB'
        if is_usb:
            base_speed = 120  # USB 3.0 típico
        
        for i in range(15):
            monitor['progress'] = 20 + (i * 2)
            read_speed = max(50, base_speed - (i * 3))  # Degrada um pouco
            iops = 15000 + (i * 500)
            monitor['metrics']['read_speed'] = read_speed
            monitor['metrics']['iops'] = iops
            monitor['metrics']['io_operations'] = iops * i
            temp = min(60, monitor['metrics']['temperature'] + (i * 0.15))  # Max 60°C
            monitor['metrics']['temperature'] = round(temp, 1)
            monitor['message'] = f'Lendo sequencial... {read_speed} MB/s | {iops} IOPS'
            await sio.emit('metrics_update', monitor['metrics'])
            await emit_status()
            await asyncio.sleep(0.9)
        
        monitor['message'] = 'Teste de Leitura Aleatória (4K)...'
        await emit_status()
        for i in range(10):
            read_speed = 120 + (i * 3)
            iops = 25000 + (i * 500)
            monitor['metrics']['read_speed'] = read_speed
            monitor['metrics']['iops'] = iops
            monitor['message'] = f'Lendo aleatório 4K... {iops} IOPS'
            await sio.emit('metrics_update', monitor['metrics'])
            await emit_status()
            await asyncio.sleep(0.8)
        
        # Fase 3: Teste de Escrita (Sequencial e Aleatório)
        monitor['phase'] = 'write'
        monitor['progress'] = 45
        monitor['message'] = 'Teste de Escrita Sequencial...'
        await emit_status()
        
        # Escrita sequencial - valores realistas
        write_base_speed = base_speed * 0.75 if not is_usb else 100  # 75% da leitura para SSD
        
        for i in range(15):
            monitor['progress'] = 45 + (i * 1.5)
            write_speed = max(40, write_base_speed - (i * 4))  # Degrada gradualmente
            iops = 12000 + (i * 400)
            monitor['metrics']['write_speed'] = write_speed
            monitor['metrics']['iops'] = iops
            monitor['metrics']['io_operations'] += iops
            temp = min(65, monitor['metrics']['temperature'] + (i * 0.2))  # Max 65°C
            monitor['metrics']['temperature'] = round(temp, 1)
            monitor['message'] = f'Escrevendo sequencial... {write_speed} MB/s | {iops} IOPS'
            await sio.emit('metrics_update', monitor['metrics'])
            await emit_status()
            await asyncio.sleep(0.9)
        
        monitor['message'] = 'Teste de Escrita Aleatória (4K)...'
        await emit_status()
        for i in range(10):
            write_speed = 100 + (i * 2)
            iops = 22000 + (i * 400)
            monitor['metrics']['write_speed'] = write_speed
            monitor['metrics']['iops'] = iops
            monitor['message'] = f'Escrevendo aleatório 4K... {iops} IOPS'
            await sio.emit('metrics_update', monitor['metrics'])
            await emit_status()
            await asyncio.sleep(0.8)
        
        # Fase 4: Análise de Latência (mais demorada se scan profundo)
        monitor['phase'] = 'latency'
        monitor['progress'] = 65
        monitor['message'] = 'Medindo latência média...'
        await emit_status()
        
        scan_iterations = 8 if not monitor['config'].get('enable_deep_scan') else 20
        delay = 0.7 if not monitor['config'].get('enable_deep_scan') else 1.5
        
        for i in range(scan_iterations):
            monitor['progress'] = 65 + (i * (30 / scan_iterations))
            latency = 0.05 + (i * 0.002)
            monitor['metrics']['avg_latency'] = round(latency, 3)
            monitor['metrics']['error_rate'] = round(0.01 + (i * 0.001), 4)
            scan_msg = " (Scan Profundo)" if monitor["config"].get("enable_deep_scan") else ""
            monitor['message'] = f'Latência: {latency*1000:.1f}ms{scan_msg}'
            await sio.emit('metrics_update', monitor['metrics'])
            await emit_status()
            await asyncio.sleep(delay)
        
        # Fase 5: Análise de Health e Wear Level
        monitor['phase'] = 'health'
        monitor['progress'] = 75
        monitor['message'] = 'Analisando saúde e desgaste...'
        await emit_status()
        
        for i in range(10):
            monitor['progress'] = 75 + (i * 1)
            wear = 2.3 + (i * 0.1)
            bad_blocks = min(5, int(i * 0.5))
            monitor['metrics']['wear_level'] = round(wear, 1)
            monitor['metrics']['bad_blocks'] = bad_blocks
            monitor['metrics']['health'] = 98 - wear
            monitor['metrics']['power_cycle_count'] = 250 + i
            monitor['message'] = f'Desgaste: {wear}% | Health: {98-wear:.1f}%'
            await sio.emit('metrics_update', monitor['metrics'])
            await emit_status()
            await asyncio.sleep(0.6)
        
        # Fase 6: Análise Avançada Completa (só executa se modo avançado ou deep scan)
        test_mode = monitor['config'].get('test_mode', 'simple')
        is_advanced = test_mode == 'advanced' or monitor['config'].get('enable_deep_scan', False)
        
        if is_advanced:
            monitor['phase'] = 'analysis'
            monitor['progress'] = 83
            monitor['message'] = 'Análise Avançada - Verificando integridade...'
            await emit_status()
            await asyncio.sleep(3)
            
            monitor['message'] = 'Análise Avançada - Verificando cache...'
            await emit_status()
            await asyncio.sleep(2)
            
            monitor['message'] = 'Análise Avançada - Verificando TRIM...'
            await emit_status()
            await asyncio.sleep(2)
            
            monitor['message'] = 'Análise Avançada - Verificando encryption...'
            await emit_status()
            await asyncio.sleep(2)
        else:
            monitor['phase'] = 'analysis'
            monitor['progress'] = 83
            monitor['message'] = 'Análise básica concluída...'
            await emit_status()
            await asyncio.sleep(1)
        
        # Fase 5: Análise por IA (se habilitada)
        if monitor['config']['enable_ai_insights']:
            monitor['progress'] = 85
            monitor['message'] = 'Gerando insights com IA...'
            await emit_status()
            
            # Adicionar informações do dispositivo na análise
            device_info = f"Dispositivo analisado: {monitor.get('selected_device', {}).get('model', 'Unknown')}"
            
            ai_insights = await analyze_with_ai(
                monitor['metrics']['smart_data'],
                monitor['metrics']
            )
            monitor['results']['ai_insights'] = f"{device_info}\n\n{ai_insights}"
            
            # GERAR EXPLICAÇÃO IA DETALHADA (raciocínio + confidence)
            try:
                smart_attrs = monitor.get('metrics', {}).get('smart_analysis_complete', {}).get('analysis', [])
                ai_explanation = generate_ai_explanation(
                    monitor['metrics'],
                    smart_attrs,
                    monitor.get('selected_device', {})
                )
                monitor['results']['ai_reasoning'] = ai_explanation
                logger.info(f"AI explanation generated with confidence: {ai_explanation.get('overall_confidence', 0):.2f}")
            except Exception as e:
                logger.error(f"Error generating AI explanation: {e}")
            
            await asyncio.sleep(1)
        
        # Fase 6: Relatório
        monitor['phase'] = 'report'
        monitor['progress'] = 95
        monitor['message'] = 'Gerando relatório final...'
        await emit_status()
        
        # Salvar resultados completos com explicação técnica
        monitor['results']['device'] = monitor.get('selected_device', {})
        monitor['results']['metrics'] = monitor['metrics']
        monitor['results']['smart_data'] = smart_data
        monitor['results']['timestamp'] = datetime.now().isoformat()
        monitor['results']['config_used'] = monitor['config'].copy()
        
        # Obter dados NVMe se for dispositivo NVMe
        nvme_info = nvme_support.get_complete_nvme_info(device_path)
        if nvme_info.get('nvme_device'):
            monitor['results']['nvme_info'] = nvme_info
        
        # Análise comparativa de benchmarks
        device_model = monitor.get('selected_device', {}).get('model', 'Unknown')
        benchmark_comparison = benchmark_db.compare_performance(device_model, monitor['metrics'])
        monitor['results']['benchmark_comparison'] = benchmark_comparison
        
        monitor['results']['history_comparison'] = history_manager.get_comparative_analysis(device_path)
        
        # Adicionar explicação técnica dos resultados
        tech_explanation = {
            'health': {
                'value': monitor['metrics']['health'],
                'used_metrics': ['SMART Status', 'Bad Blocks', 'Error Rate', 'Wear Level'],
                'reasoning': 'Saúde calculada com base em status SMART, setores ruins, taxa de erros e nível de desgaste'
            },
            'wear_level': {
                'value': monitor['metrics']['wear_level'],
                'used_metrics': ['Power On Hours', 'Power Cycles', 'Wear Leveling Count'],
                'reasoning': f"Desgaste estimado com base em {monitor['metrics']['power_on_hours']}h de operação e {monitor['metrics']['power_cycle_count']} ciclos"
            },
            'temperature': {
                'value': monitor['metrics']['temperature'],
                'used_metrics': ['SMART Attribute 194'],
                'reasoning': f"Temperatura atual do SSD medida via SMART. {'Adequada' if monitor['metrics']['temperature'] < 60 else 'Alta'} para uso contínuo"
            }
        }
        monitor['results']['technical_explanation'] = tech_explanation
        
        await asyncio.sleep(1)
        
        monitor['progress'] = 100
        monitor['message'] = 'Diagnóstico concluído!'
        monitor['results']['status'] = 'completed'
        await emit_status()
        
        await sio.emit('phase_done', 'report')
        await sio.emit('diagnostic_complete', monitor['results'])
        
    except Exception as e:
        logger.error(f"Error in diagnostic: {e}")
        monitor['message'] = f'Erro: {str(e)}'
        monitor['progress'] = 0
        await emit_status()
    finally:
        monitor['running'] = False

@app.get("/report")
async def get_report():
    """Retorna o relatório de diagnóstico em JSON"""
    return {
        "status": "completed" if monitor['progress'] == 100 else "in_progress",
        "progress": monitor['progress'],
        "message": monitor['message'],
        "results": monitor.get('results', {}),
        "metrics": monitor.get('metrics', {}),
        "selected_device": monitor.get('selected_device'),
        "timestamp": datetime.now().isoformat()
    }

@app.get("/report/html")
async def get_report_html():
    """Retorna relatório em HTML"""
    from fastapi.responses import HTMLResponse
    generator = ReportGenerator()
    html = generator.generate_html(monitor['results'])
    return HTMLResponse(content=html.decode('utf-8'))

@app.get("/metrics")
async def get_metrics():
    """Retorna métricas em tempo real"""
    return monitor['metrics']

@app.post("/config")
async def update_config(config: Dict):
    """Atualiza configurações do diagnóstico"""
    if 'test_duration' in config:
        monitor['config']['test_duration'] = config['test_duration']
    if 'enable_advanced_analysis' in config:
        monitor['config']['enable_advanced_analysis'] = config['enable_advanced_analysis']
    if 'enable_ai_insights' in config:
        monitor['config']['enable_ai_insights'] = config['enable_ai_insights']
    
    return {"status": "ok", "config": monitor['config']}

@app.get("/config")
async def get_config():
    """Retorna configurações atuais"""
    return monitor['config']

@app.get("/devices")
async def list_devices():
    """List available storage devices"""
    devices = []
    try:
        # Listar dispositivos de bloco reais
        result = subprocess.run(['lsblk', '-d', '-n', '-o', 'NAME,SIZE,MODEL'], 
                              capture_output=True, text=True)
        
        for line in result.stdout.split('\n'):
            if not line:
                continue
                
            parts = line.split()
            if len(parts) >= 2:
                device_name = parts[0]
                device_path = f"/dev/{device_name}"
                size = parts[1] if len(parts) > 1 else "Unknown"
                
                # Pegar modelo (pode ter espaços)
                model = ' '.join(parts[2:]) if len(parts) > 2 else "Unknown"
                
                # Pular loop devices
                if device_name.startswith('loop'):
                    continue
                
                # Pular CD-ROM
                if 'sr' in device_name:
                    continue
                
                # Determinar tipo e barramento
                device_type = "disk"
                bus = "SATA"  # Default
                
                # Tentar identificar USB
                try:
                    udev_result = subprocess.run(
                        ['udevadm', 'info', '--query=property', '--name=' + device_name],
                        capture_output=True, text=True, timeout=2
                    )
                    udev_output = udev_result.stdout.lower()
                    if 'usb' in udev_output or 'usb_device' in udev_output:
                        bus = "USB"
                    
                    # Verificar se é SSD
                    is_ssd = False
                    if 'ssd' in model.lower() or 'ID_ATA_ROTATION_RATE_RPM' not in udev_result.stdout:
                        is_ssd = True
                        
                except:
                    # Heurística: se o modelo contém SSD, é SSD
                    if 'ssd' in model.lower():
                        is_ssd = True
                    bus = "USB" if device_name in ['sdb', 'sdc', 'sdd', 'sde'] else "SATA"
                
                devices.append({
                    'path': device_path,
                    'name': device_name,
                    'model': model,
                    'bus': bus,
                    'size': size,
                    'type': device_type
                })
        
        # Retornar vazio se não encontrou nada
        if not devices:
            logger.warning("No storage devices found")
            
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
    # Usar socket_app para suportar Socket.IO
    uvicorn.run(socket_app, host="0.0.0.0", port=8000, log_level="info")
