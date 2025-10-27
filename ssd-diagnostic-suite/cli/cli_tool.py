#!/usr/bin/env python3
"""
CLI Tool para Automação Headless
Permite execução de diagnósticos via linha de comando
"""
import argparse
import sys
import json
import subprocess
from pathlib import Path

def run_smartctl(device_path: str):
    """Executa smartctl para um dispositivo"""
    try:
        result = subprocess.run(
            ['smartctl', '-a', '-j', device_path],
            capture_output=True,
            text=True,
            timeout=15
        )
        if result.returncode == 0:
            return json.loads(result.stdout)
        else:
            print(f"Erro ao ler SMART: {result.stderr}", file=sys.stderr)
            return None
    except Exception as e:
        print(f"Erro: {e}", file=sys.stderr)
        return None

def analyze_device(device_path: str, output_file: str = None):
    """Analisa dispositivo e gera relatório"""
    print(f"🔍 Analisando dispositivo: {device_path}")
    
    smart_data = run_smartctl(device_path)
    if not smart_data:
        print("❌ Falha ao obter dados SMART")
        sys.exit(1)
    
    # Resumo
    health = 100 if smart_data.get('smart_status', {}).get('passed', False) else 50
    temp = smart_data.get('temperature', {}).get('current', 0)
    
    print(f"\n📊 Resultados:")
    print(f"  Saúde: {health}%")
    print(f"  Temperatura: {temp}°C")
    
    if output_file:
        with open(output_file, 'w') as f:
            json.dump(smart_data, f, indent=2)
        print(f"\n✅ Relatório salvo em: {output_file}")
    
    return smart_data

def main():
    parser = argparse.ArgumentParser(description='Disk Diagnostic Suite - CLI Tool')
    parser.add_argument('device', help='Caminho do dispositivo (ex: /dev/sda)')
    parser.add_argument('-o', '--output', help='Arquivo de saída JSON')
    parser.add_argument('-f', '--format', choices=['json', 'summary'], default='summary', help='Formato de saída')
    
    args = parser.parse_args()
    
    # Verificar se dispositivo existe
    if not Path(args.device).exists():
        print(f"❌ Dispositivo não encontrado: {args.device}", file=sys.stderr)
        sys.exit(1)
    
    # Executar análise
    data = analyze_device(args.device, args.output)
    
    if args.format == 'json':
        print(json.dumps(data, indent=2))

if __name__ == '__main__':
    main()

