"""
Gerador de Relatórios PDF Profissionais
Exporta PDFs com relatório técnico e sumário executivo
"""
import logging
from typing import Dict
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import standardFonts
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT

logger = logging.getLogger(__name__)

class PDFGenerator:
    """Gera relatórios PDF profissionais"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Configura estilos personalizados"""
        self.styles.add(ParagraphStyle(
            name='TitleStyle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#667eea'),
            spaceAfter=30,
            alignment=TA_CENTER
        ))
        
        self.styles.add(ParagraphStyle(
            name='Heading2Custom',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#764ba2'),
            spaceAfter=12
        ))
        
        self.styles.add(ParagraphStyle(
            name='Summary',
            parent=self.styles['Normal'],
            fontSize=12,
            backColor=colors.HexColor('#fff3cd'),
            borderColor=colors.HexColor('#ffc107'),
            borderWidth=1,
            borderPadding=10,
            spaceAfter=10
        ))
    
    def generate_pdf(self, data: Dict) -> bytes:
        """Gera PDF profissional"""
        from io import BytesIO
        
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=72)
        story = []
        
        # Título
        story.append(Paragraph("🔍 Disk Diagnostic Suite - Relatório Profissional", self.styles['TitleStyle']))
        story.append(Spacer(1, 12))
        
        # Informações do Dispositivo
        device = data.get('device', {})
        story.append(Paragraph(f"<b>Dispositivo:</b> {device.get('model', 'Unknown')}", self.styles['Heading2Custom']))
        story.append(Paragraph(f"<b>Caminho:</b> {device.get('path', 'N/A')}", self.styles['Normal']))
        story.append(Paragraph(f"<b>Bus:</b> {device.get('bus', 'N/A')}", self.styles['Normal']))
        story.append(Paragraph(f"<b>Tamanho:</b> {device.get('size', 'N/A')}", self.styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Sumário Executivo
        story.append(Paragraph("📋 Sumário Executivo", self.styles['Heading2Custom']))
        
        metrics = data.get('metrics', {})
        health = metrics.get('health', 0)
        temp = metrics.get('temperature', 0)
        
        summary_text = f"""
        Status Geral: {'Excelente' if health >= 95 else 'Bom' if health >= 80 else 'Atenção'}<br/>
        Saúde do Disco: {health}%<br/>
        Temperatura: {temp}°C<br/>
        Desgaste: {metrics.get('wear_level', 0)}%<br/>
        """
        
        story.append(Paragraph(summary_text, self.styles['Summary']))
        story.append(Spacer(1, 20))
        
        # Métricas de Performance
        story.append(Paragraph("⚡ Métricas de Performance", self.styles['Heading2Custom']))
        
        perf_data = [
            ['Métrica', 'Valor', 'Status'],
            ['Velocidade Leitura', f"{metrics.get('read_speed', 0)} MB/s", 'OK'],
            ['Velocidade Escrita', f"{metrics.get('write_speed', 0)} MB/s", 'OK'],
            ['Temperatura', f"{temp}°C", 'Adequada' if temp < 60 else 'Alta'],
            ['IOPS', f"{metrics.get('iops', 0):,}", 'OK'],
            ['Latência Média', f"{metrics.get('avg_latency', 0):.2f} ms", 'OK'],
        ]
        
        perf_table = Table(perf_data, colWidths=[120, 100, 80])
        perf_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8f9fa')),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey)
        ]))
        
        story.append(perf_table)
        story.append(PageBreak())
        
        # Análise por IA
        if data.get('ai_insights'):
            story.append(Paragraph("🤖 Análise Inteligente (IA)", self.styles['Heading2Custom']))
            story.append(Paragraph(data['ai_insights'].replace('\n', '<br/>'), self.styles['Normal']))
            story.append(Spacer(1, 20))
        
        # Build PDF
        doc.build(story)
        
        pdf_bytes = buffer.getvalue()
        buffer.close()
        
        return pdf_bytes

def generate_professional_pdf(data: Dict) -> bytes:
    """Função helper"""
    generator = PDFGenerator()
    return generator.generate_pdf(data)

