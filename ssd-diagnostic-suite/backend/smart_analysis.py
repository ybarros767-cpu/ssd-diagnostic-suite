"""
Módulo de Análise SMART Completa
Implementa análise profissional de todos atributos SMART
"""
import subprocess
import json
import re
import logging
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class SmartAttribute:
    """Representa um atributo SMART"""
    id: int
    name: str
    raw_value: int
    normalized_value: int
    threshold: int
    type: str
    updated: bool
    failure_rate: float
    critical: bool

class SmartAnalyzer:
    """Analisa dados SMART completos"""
    
    # Atributos SMART críticos mais importantes
    CRITICAL_ATTRIBUTES = {
        # Physical
        1: ("Raw_Read_Error_Rate", "critical"),
        5: ("Reallocated_Sector_Ct", "critical"),
        196: ("Reallocated_Event_Count", "critical"),
        197: ("Current_Pending_Sector", "critical"),
        198: ("Offline_Uncorrectable", "critical"),
        
        # Wear/Health
        177: ("Wear_Leveling_Count", "warning"),
        184: ("End-to-End_Error", "critical"),
        
        # Performance
        7: ("Seek_Error_Rate", "warning"),
        
        # Thermal
        194: ("Temperature_Celsius", "info"),
        
        # Usage
        9: ("Power_On_Hours", "info"),
        12: ("Power_Cycle_Count", "info"),
    }
    
    def __init__(self):
        self.attributes = []
        self.warnings = []
        self.critical_issues = []
    
    def analyze_complete(self, device_path: str) -> Dict:
        """
        Análise COMPLETA e PROFUNDA do SMART
        Retorna todos atributos, warnings, critical issues
        """
        smart_data = self._collect_all_attributes(device_path)
        
        if not smart_data:
            return {
                'error': 'Não foi possível coletar dados SMART',
                'attributes': [],
                'analysis': []
            }
        
        # Parse todos atributos
        attributes = self._parse_all_attributes(smart_data)
        
        # Análise profunda
        analysis = self._deep_analysis(attributes)
        
        # Cálculo de saúde baseado em múltiplos fatores
        health_score = self._calculate_health_score(attributes)
        
        return {
            'device_path': device_path,
            'total_attributes': len(attributes),
            'attributes': [attr.__dict__ for attr in attributes],
            'analysis': analysis,
            'warnings': self.warnings,
            'critical_issues': self.critical_issues,
            'health_score': health_score,
            'recommendations': self._generate_recommendations(attributes, health_score)
        }
    
    def _collect_all_attributes(self, device_path: str) -> Dict:
        """Coleta TODOS os atributos SMART disponíveis"""
        try:
            # Tentar smartctl com todas flags
            result = subprocess.run(
                ['smartctl', '-A', '-j', device_path],
                capture_output=True, 
                text=True, 
                timeout=15
            )
            
            if result.returncode == 0:
                return json.loads(result.stdout)
            
            # Fallback: try without JSON
                result = subprocess.run(
                ['smartctl', '-A', device_path],
                capture_output=True, 
                text=True, 
                timeout=15
            )
            
            return self._parse_smart_text(result.stdout)
        except Exception as e:
            logger.error(f"Error collecting SMART: {e}")
            return {}
    
    def _parse_smart_text(self, text: str) -> Dict:
        """Parse SMART output em texto para dict"""
        data = {'ata_smart_attributes': {'table': []}}
        
        # Pattern para attributes
        pattern = r'(\d+)\s+(\w+[_\w]*)\s+0x\w+\s+(\d+)\s+(\d+)\s+(\d+)\s+(\w+)'
        
        for line in text.split('\n'):
            match = re.match(pattern, line)
            if match:
                attr_id, name, flag, value, worst, thresh, type_str = match.groups()
                data['ata_smart_attributes']['table'].append({
                    'id': int(attr_id),
                    'name': name,
                    'flags': {'value': int(flag, 16)},
                    'value': int(value),
                    'worst': int(worst),
                    'thresh': int(thresh),
                    'raw': {'value': self._extract_raw_value(line)},
                    'type': {'name': type_str}
                })
        
        return data
    
    def _extract_raw_value(self, line: str) -> int:
        """Extrai valor raw do SMART output"""
        # Procura padrão tipo "000000000012"
        match = re.search(r'(\d{12})', line)
        return int(match.group(1)) if match else 0
    
    def _parse_all_attributes(self, smart_data: Dict) -> List[SmartAttribute]:
        """Parse TODOS atributos SMART coletados"""
        attributes = []
        
        attrs = smart_data.get('ata_smart_attributes', {}).get('table', [])
        
        for attr in attrs:
            attr_id = attr.get('id', 0)
            name = attr.get('name', 'Unknown')
            raw_value = attr.get('raw', {}).get('value', 0)
            normalized = attr.get('value', 0)
            threshold = attr.get('thresh', 0)
            
            # Determinar se é crítico
            critical = name in [a[0] for a in self.CRITICAL_ATTRIBUTES.values() if a[1] == 'critical']
            
            # Calcular failure rate
            failure_rate = 0.0
            if threshold > 0 and normalized < threshold:
                failure_rate = ((threshold - normalized) / threshold) * 100
            
            attributes.append(SmartAttribute(
                id=attr_id,
                name=name,
                raw_value=raw_value,
                normalized_value=normalized,
                threshold=threshold,
                type=attr.get('type', {}).get('name', 'Old-age'),
                updated=bool(attr.get('flags', {}).get('value', 0) & 1),
                failure_rate=failure_rate,
                critical=critical
            ))
        
        return attributes
    
    def _deep_analysis(self, attributes: List[SmartAttribute]) -> List[Dict]:
        """Análise profunda de cada atributo"""
        analysis = []
        
        for attr in attributes:
            entry = {
                'attribute_id': attr.id,
                'name': attr.name,
                'status': 'OK',
                'value': attr.normalized_value,
                'threshold': attr.threshold,
                'failure_rate': attr.failure_rate,
                'raw_value': attr.raw_value,
                'interpretation': self._interpret_attribute(attr)
            }
            
            # Adicionar warnings
            if attr.failure_rate > 50:
                self.critical_issues.append(f"{attr.name}: {attr.failure_rate:.1f}% abaixo do threshold")
                screened['status'] = 'CRITICAL'
            elif attr.failure_rate > 0:
                self.warnings.append(f"{attr.name}: {attr.failure_rate:.1f}% abaixo do threshold")
                screened['status'] = 'WARNING'
            
            analysis.append(entry)
        
        return analysis
    
    def _interpret_attribute(self, attr: SmartAttribute) -> str:
        """Interpreta significado técnico de cada atributo"""
        interpretations = {
            5: "Setores realocados. Valores > 0 indicam degradação física.",
            196: "Eventos de realocação. Incrementos contínuos indicam problemas.",
            197: "Setores pendentes. Valores > 0: falha física em progresso.",
            194: f"Temperatura: {attr.raw_value}°C. Ideal: < 60°C",
            9: f"Potência ligada: {attr.raw_value}h ({attr.raw_value/24/365:.1f} anos)",
            12: f"Ciclos de energia: {attr.raw_value}",
        }
        
        return interpretations.get(attr.id, f"Atributo {attr.name}: valor {attr.normalized_value}")
    
    def _calculate_health_score(self, attributes: List[SmartAttribute]) -> Dict:
        """Calcula score de saúde baseado em múltiplos fatores"""
        if not attributes:
            return {'score': 100, 'status': 'Unknown', 'factors': []}
        
        factors = []
        total_weight = 0
        weighted_score = 0
        
        for attr in attributes:
            if attr.critical:
                weight = 3
            elif 'Wear' in attr.name or 'Health' in attr.name:
                weight = 2
            else:
                weight = 1
            
            # Score baseado em quanto está acima do threshold
            if attr.threshold == 0:
                attr_score = 100
            else:
                attr_score = max(0, min(100, (attr.normalized_value / attr.threshold) * 100))
            
            factors.append({
                'name': attr.name,
                'score': attr_score,
                'weight': weight
            })
            
            weighted_score += attr_score * weight
            total_weight += weight
        
        final_score = weighted_score / total_weight if total_weight > 0 else 100
        
        # Determinar status
        if final_score >= 95:
            status = 'Excellent'
        elif final_score >= 80:
            status = 'Good'
        elif final_score >= 60:
            status = 'Fair'
        elif final_score >= 40:
            status = 'Poor'
        else:
            status = 'Critical'
        
        return {
            'score': round(final_score, 2),
            'status': status,
            'factors': factors,
            'weighted_calculation': True
        }
    
    def _generate_recommendations(self, attributes: List[SmartAttribute], health: Dict) -> List[str]:
        """Gera recomendações baseadas na análise"""
        recommendations = []
        
        # Análise de wear
        wear_attrs = [a for a in attributes if 'Wear' in a.name or 'Health' in a.name]
        if wear_attrs:
            wear_pct = wear_attrs[0].raw_value if wear_attrs else 0
            if wear_pct > 80:
                recommendations.append(f"⚠️ DESGASTE CRÍTICO ({wear_pct}%): Considere substituição imediata")
            elif wear_pct > 60:
                recommendations.append(f"⚠️ Desgaste alto ({wear_pct}%): Planeje substituição em breve")
        
        # Análise de erros
        error_count = sum(1 for a in attributes if a.failure_rate > 50)
        if error_count > 0:
            recommendations.append(f"⚠️ {error_count} atributos com valores críticos")
        
        # Análise térmica
        temp_attrs = [a for a in attributes if a.id == 194]
        if temp_attrs:
            temp = temp_attrs[0].raw_value
            if temp > 70:
                recommendations.append(f"⚠️ TEMPERATURA ALTA ({temp}°C): Melhore ventilação")
        
        # Health geral
        if health['status'] in ['Poor', 'Critical']:
            recommendations.append("⚠️ BACKUP URGENTE: Saúde do disco comprometida")
            recommendations.append("⚠️ Considere substituição imediata")
        
        if not recommendations:
            recommendations.append("✅ Disco operando dentro dos parâmetros normais")
            recommendations.append("✅ Continue com backups regulares")
        
        return recommendations

def analyze_smart_complete(device_path: str) -> Dict:
    """Função helper para análise SMART completa"""
    analyzer = SmartAnalyzer()
    return analyzer.analyze_complete(device_path)

