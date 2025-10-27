"""
Gerador de Relatórios Multi-formato
Exporta relatórios em JSON, PDF e HTML
"""
from typing import Dict, List
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class ReportGenerator:
    """Gera relтурios em múltiplos formatos"""
    
    def __init__(self):
        self.reports = {}
    
    def generate_pdf(self, data: Dict) -> bytes:
        """Gera PDF usando reportlab"""
        try:
            from pdf_generator import generate_professional_pdf
            return generate_professional_pdf(data)
        except Exception as e:
            logger.error(f"Erro ao gerar PDF: {e}")
            # Fallback para HTML
            return self.generate_html(data)
    
    def generate_html(self, data: Dict) -> bytes:
        """Gera relatório HTML visual e profissional"""
        device = data.get('device', {})
        metrics = data.get('metrics', {})
        smart = data.get('smart_analysis_complete', {})
        ai_insights = data.get('ai_insights', '')
        
        html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>Relatório Diagnóstico</title>
    <style>
        body {{ font-family: Arial, sans-serif; padding: 20px; }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        .header {{ background: #667eea; color: white; padding: 20px; text-align: center; }}
        .metric {{ background: #f8f9fa; padding: 15px; margin: 10px 0; border-radius: 5px; }}
        table {{ width: 100%; border-collapse: collapse; }}
        th, td {{ padding: 8px; border: 1px solid #ddd; }}
        th {{ background: #667eea; color: white; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Relatório de Diagnóstico de Disco</h1>
            <p>Gerado em {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</p>
        </div>
        
        <h2>Dispositivo: {device.get('model', 'Unknown')}</h2>
        
        <div class="metric">
            <strong>Saúde:</strong> {metrics.get('health', 0)}%
        </div>
        <div class="metric">
            <strong>Leitura:</strong> {metrics.get('read_speed', 0)} MB/s
        </div>
        <div class="metric">
            <strong>Escrita:</strong> {metrics.get('write_speed', 0)} MB/s
        </div>
        <div class="metric">
            <strong>Temperatura:</strong> {metrics.get('temperature', 0)}°C
        </div>
        
        <h2>Análise IA</h2>
        <pre>{ai_insights}</pre>
    </div>
</body>
</html>"""
        
        return html.encode('utf-8')

