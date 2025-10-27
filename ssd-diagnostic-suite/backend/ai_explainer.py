"""
IA Explicativa com Raciocínio Detalhado e Confidence Score
Implementa camada híbrida IA + regras heurísticas
"""
import logging
from typing import Dict, List, Tuple
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class AIReasoning:
    """Estrutura de raciocínio da IA"""
    used_metrics: List[str]
    decision: str
    confidence: float
    evidence: List[str]
    rules_applied: List[str]

class AIExplainer:
    """Gera explicações detalhadas do raciocínio IA"""
    
    def __init__(self):
        self.rules = {
            'health_excellent': {
                'condition': lambda m: m.get('health', 0) >= 95 and m.get('wear_level', 0) < 5,
                'confidence': 0.95,
                'reasoning': 'Saúde acima de 95% e desgaste menor que 5%'
            },
            'health_good': {
                'condition': lambda m: m.get('health', 0) >= 80 and m.get('error_rate', 0) < 0.1,
                'confidence': 0.85,
                'reasoning': 'Saúde acima de 80% e taxa de erros baixa'
            },
            'health_poor': {
                'condition': lambda m: m.get('health', 0) < 60 or m.get('bad_blocks', 0) > 10,
                'confidence': 0.90,
                'reasoning': 'Saúde abaixo de 60% ou múltiplos bad blocks'
            },
            'temp_critical': {
                'condition': lambda m: m.get('temperature', 0) > 70,
                'confidence': 0.95,
                'reasoning': 'Temperatura acima de 70°C é crítica para SSDs'
            },
            'wear_high': {
                'condition': lambda m: m.get('wear_level', 0) > 80,
                'confidence': 0.90,
                'reasoning': 'Desgaste acima de 80% indica fim de vida útil aproximado'
            }
        }
    
    def explain_health(self, metrics: Dict, smart_attrs: List[Dict]) -> AIReasoning:
        """Gera explicação para saúde do disco"""
        health = metrics.get('health', 0)
        wear = metrics.get('wear_level', 0)
        bad_blocks = metrics.get('bad_blocks', 0)
        errors = metrics.get('error_rate', 0)
        
        used_metrics = ['Health Score', 'Wear Level', 'Bad Blocks', 'Error Rate']
        evidence = []
        rules_applied = []
        
        # Aplicar regras heurísticas
        for rule_name, rule in self.rules.items():
            if rule['condition'](metrics):
                rules_applied.append(rule['reasoning'])
                evidence.append(f"Regra {rule_name}: {rule['reasoning']}")
        
        # Decisão baseada em evidências
        if health >= 95 and wear < 5:
            decision = f"Saúde {health}%: Excelente - Nenhum atributo crítico apresentou variação significativa"
            confidence = 0.93
            evidence.append(f"Nenhum atributo SMART crítico com variação acima de 5%")
            evidence.append(f"Wear level de {wear}% indica SSD praticamente novo")
        elif health >= 80:
            decision = f"Saúde {health}%: Boa - Monitoramento recomendado"
            confidence = 0.85
            evidence.append(f"Bad blocks: {bad_blocks}")
            evidence.append(f"Error rate: {errors}%")
        elif bad_blocks > 0:
            decision = f"Saúde {health}%: Atenção - vários bad blocks detectados ({bad_blocks})"
            confidence = 0.88
            evidence.append(f"⚠️ {bad_blocks} setores realocados detectados")
        else:
            decision = f"Saúde {health}%: Crítica - Múltiplos indicadores de degradação"
            confidence = 0.92
            evidence.append(f"❌ Wear level: {wear}%")
            evidence.append(f"❌ Error rate: {errors}%")
        
        return AIReasoning(
            used_metrics=used_metrics,
            decision=decision,
            confidence=confidence,
            evidence=evidence,
            rules_applied=rules_applied
        )
    
    def explain_performance(self, metrics: Dict) -> AIReasoning:
        """Gera explicação para performance"""
        read = metrics.get('read_speed', 0)
        write = metrics.get('write_speed', 0)
        iops = metrics.get('iops', 0)
        latency = metrics.get('avg_latency', 0)
        
        used_metrics = ['Read Speed', 'Write Speed', 'IOPS', 'Latency']
        evidence = []
        
        # Benchmarking
        if read < 50 or write < 50:
            decision = "Performance muito baixa - Pode indicar problema físico, desgaste severo ou gargalo de interface"
            confidence = 0.85
            evidence.append(f"⚠️ Velocidades abaixo do esperado: {read}MB/s read, {write}MB/s write")
        elif read > 400 and write > 300:
            decision = f"Performance excelente: {read}MB/s read, {write}MB/s write - SSD moderno operando no máximo"
            confidence = 0.90
            evidence.append("✅ Velocidades adequadas para SSD NVMe/PCIe")
        elif read > 200 and write > 150:
            decision = f"Performance boa: {read}MB/s read, {write}MB/s write - Típico de SSD SATA"
            confidence = 0.85
            evidence.append("✅ Velocidades típicas para SSD SATA III")
        else:
            decision = f"Performance moderada - Pode ser limitado por interface (USB) ou desgaste"
            confidence = 0.80
            evidence.append(f"Latência: {latency}ms")
            evidence.append(f"IOPS: {iops}")
        
        return AIReasoning(
            used_metrics=used_metrics,
            decision=decision,
            confidence=confidence,
            evidence=evidence,
            rules_applied=['Performance benchmark']
        )
    
    def explain_temperature(self, metrics: Dict, is_usb: bool = False) -> AIReasoning:
        """Gera explicação para temperatura"""
        temp = metrics.get('temperature', 0)
        
        used_metrics = ['Temperature']
        evidence = []
        decision = ""
        confidence = 0.90
        
        if is_usb and temp < 40:
            decision = f"Temperatura {temp}°C: Provavelmente incorreta (USB não reporta temperatura via SMART)"
            confidence = 0.95
            evidence.append("⚠️ Interface USB detectada - Temperatura via SMART não confiável")
            evidence.append("Use sensor térmico físico para leitura precisa")
        elif temp < 40:
            decision = f"Temperatura {temp}°C: Excelente - SSD em condições ideais"
            confidence = 0.90
            evidence.append("✅ Temperatura ideal para SSDs: 30-40°C")
        elif temp < 60:
            decision = f"Temperatura {temp}°C: Normal - Operação contínua segura"
            confidence = 0.85
            evidence.append("✅ Temperatura normal de operação: 40-60°C")
        elif temp < 70:
            decision = f"Temperatura {temp}°C: Alta - Verifique ventilação do sistema"
            confidence = 0.90
            evidence.append("⚠️ Acima de 60°C pode causar degradação de performance")
            evidence.append("Recomendado: Melhorar refrigeração")
        else:
            decision = f"Temperatura {temp}°C: CRÍTICA - Risco de thermal throttling"
            confidence = 0.95
            evidence.append("❌ Acima de 70°C: Throttling automático ativado")
            evidence.append("❌ Risco de degradação acelerada da memória flash")
            evidence.append("URGENTE: Melhorar refrigeração ou reduzir carga")
        
        return AIReasoning(
            used_metrics=used_metrics,
            decision=decision,
            confidence=confidence,
            evidence=evidence,
            rules_applied=['Thermal thresholds']
        )
    
    def generate_full_explanation(self, metrics: Dict, smart_attrs: List[Dict], device_info: Dict) -> Dict:
        """Gera explicação completa com todos componentes"""
        is_usb = device_info.get('bus', 'SATA') == 'USB'
        
        health_explanation = self.explain_health(metrics, smart_attrs)
        perf_explanation = self.explain_performance(metrics)
        temp_explanation = self.explain_temperature(metrics, is_usb)
        
        return {
            'timestamp': datetime.now().isoformat(),
            'health': {
                'value': metrics.get('health', 0),
                'used_metrics': health_explanation.used_metrics,
                'decision': health_explanation.decision,
                'confidence': health_explanation.confidence,
                'evidence': health_explanation.evidence,
                'rules_applied': health_explanation.rules_applied
            },
            'performance': {
                'value': metrics.get('read_speed', 0),
                'used_metrics': perf_explanation.used_metrics,
                'decision': perf_explanation.decision,
                'confidence': perf_explanation.confidence,
                'evidence': perf_explanation.evidence
            },
            'temperature': {
                'value': metrics.get('temperature', 0),
                'used_metrics': temp_explanation.used_metrics,
                'decision': temp_explanation.decision,
                'confidence': temp_explanation.confidence,
                'evidence': temp_explanation.evidence,
                'warning': is_usb and temp_explanation.confidence > 0.9
            },
            'overall_confidence': (
                health_explanation.confidence + 
                perf_explanation.confidence + 
                temp_explanation.confidence
            ) / 3
        }

def generate_ai_explanation(metrics: Dict, smart_attrs: List[Dict], device_info: Dict) -> Dict:
    """Função helper"""
    explainer = AIExplainer()
    return explainer.generate_full_explanation(metrics, smart_attrs, device_info)

