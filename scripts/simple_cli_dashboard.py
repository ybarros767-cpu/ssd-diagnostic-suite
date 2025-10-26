#!/usr/bin/env python3
"""
SSD Diagnostic Suite - Simple CLI Dashboard
Painel CLI simples e funcional sem dependências extras
"""

import sys
import time
import json
import requests
from datetime import datetime
from typing import Dict, Optional
from threading import Thread, Event


class SimpleDashboard:
    """Painel CLI simples e eficiente"""
    
    def __init__(self, api_url: str = "http://localhost:8000"):
        self.api_url = api_url
        self.running = Event()
        self.status = {
            'phase': 'idle',
            'progress': 0.0,
            'message': 'Aguardando...',
            'temperature': 0.0,
            'read_speed': 0.0,
            'write_speed': 0.0,
            'health': 100.0
        }
    
    def clear_screen(self):
        """Limpa a tela"""
        print("\033[2J\033[H", end='')
    
    def print_header(self):
        """Imprime cabeçalho"""
        print("\033[1;34m" + "=" * 80)
        print("   SSD DIAGNOSTIC SUITE - CLI DASHBOARD")
        print("=" * 80 + "\033[0m\n")
    
    def print_status(self):
        """Imprime status atual"""
        phase_colors = {
            'smart': '\033[1;36m',    # Cyan
            'read': '\033[1;33m',     # Yellow  
            'write': '\033[1;35m',    # Magenta
            'report': '\033[1;32m',   # Green
            'idle': '\033[0m'         # White
        }
        
        color = phase_colors.get(self.status['phase'], '\033[0m')
        phase_name = self.status['phase'].upper() if self.status['phase'] != 'idle' else 'IDLE'
        
        print(f"Fase Atual:      {color}{phase_name}\033[0m")
        print(f"Mensagem:        {self.status['message']}")
        print(f"Progresso:       {self.status['progress']:.1f}%")
        print(f"Temperatura:     {self.status['temperature']:.1f}°C")
        print(f"Velocidade:      Leitura: {self.status['read_speed']:.2f} MB/s | "
              f"Escrita: {self.status['write_speed']:.2f} MB/s")
        
        # Barra de progresso
        bar_width = 50
        filled = int(self.status['progress'] / 100 * bar_width)
        bar = '█' * filled + '░' * (bar_width - filled)
        print(f"\n{bar} {self.status['progress']:.1f}%\n")
    
    def print_menu(self):
        """Imprime menu de opções"""
        print("\033[1;36m" + "-" * 80)
        print("COMANDOS DISPONÍVEIS:")
        print("-" * 80 + "\033[0m")
        print("  \033[1;32m[I]\033[0m - Iniciar Diagnóstico")
        print("  \033[1;32m[R]\033[0m - Ver Relatório")
        print("  \033[1;32m[S]\033[0m - Status do Backend")
        print("  \033[1;32m[D]\033[0m - Listar Dispositivos")
        print("  \033[1;32m[Q]\033[0m - Sair")
        print()
    
    def update_display(self):
        """Atualiza a exibição completa"""
        self.clear_screen()
        self.print_header()
        self.print_status()
        self.print_menu()
    
    def start_diagnostic(self):
        """Inicia diagnóstico"""
        try:
            response = requests.post(f"{self.api_url}/run", timeout=5)
            if response.status_code == 200:
                data = response.json()
                self.status['phase'] = 'smart'
                self.status['message'] = 'Diagnóstico iniciado!'
                print("\033[1;32m✓ Diagnóstico iniciado!\033[0m\n")
                return True
            else:
                print("\033[1;31m✗ Erro ao iniciar diagnóstico\033[0m\n")
                return False
        except Exception as e:
            print(f"\033[1;31m✗ Erro: {e}\033[0m\n")
            return False
    
    def get_report(self):
        """Obtém relatório"""
        try:
            response = requests.get(f"{self.api_url}/report", timeout=5)
            if response.status_code == 200:
                report = response.json()
                print("\n\033[1;36m" + "RELATÓRIO" + "\033[0m")
                print("-" * 80)
                print(json.dumps(report, indent=2))
                print("-" * 80 + "\n")
                input("\nPressione ENTER para continuar...")
            else:
                print("\033[1;31m✗ Relatório ainda não disponível\033[0m\n")
        except Exception as e:
            print(f"\033[1;31m✗ Erro: {e}\033[0m\n")
    
    def check_backend_status(self):
        """Verifica status do backend"""
        try:
            response = requests.get(f"{self.api_url}/health", timeout=2)
            if response.status_code == 200:
                data = response.json()
                print("\033[1;32m✓ Backend está rodando\033[0m")
                print(f"Status: {data.get('status', 'unknown')}\n")
            else:
                print("\033[1;31m✗ Backend não está respondendo\033[0m\n")
        except Exception as e:
            print("\033[1;31m✗ Backend não está acessível\033[0m\n")
        
        input("Pressione ENTER para continuar...")
    
    def list_devices(self):
        """Lista dispositivos disponíveis"""
        try:
            response = requests.get(f"{self.api_url}/devices", timeout=5)
            if response.status_code == 200:
                devices = response.json()
                print("\n\033[1;36mDISPOSITIVOS ENCONTRADOS:\033[0m")
                print("-" * 80)
                
                if devices:
                    for i, device in enumerate(devices, 1):
                        print(f"\n[{i}] {device.get('path', 'N/A')}")
                        print(f"    Modelo: {device.get('model', 'N/A')}")
                        print(f"    Serial: {device.get('serial', 'N/A')}")
                        print(f"    Bus: {device.get('bus', 'N/A')}")
                        print(f"    Tamanho: {device.get('size', 'N/A')} bytes")
                else:
                    print("Nenhum dispositivo encontrado")
                
                print("-" * 80 + "\n")
            else:
                print("\033[1;31m✗ Erro ao listar dispositivos\033[0m\n")
        except Exception as e:
            print(f"\033[1;31m✗ Erro: {e}\033[0m\n")
        
        input("Pressione ENTER para continuar...")
    
    def poll_status(self):
        """Verifica status do diagnóstico periodicamente"""
        while self.running.is_set():
            try:
                response = requests.get(f"{self.api_url}/report", timeout=2)
                if response.status_code == 200:
                    data = response.json()
                    if 'progress' in data:
                        self.status['progress'] = data['progress']
                    if 'message' in data:
                        self.status['message'] = data['message']
                    if 'phase' in data:
                        self.status['phase'] = data.get('phase', 'idle')
            except:
                pass
            
            time.sleep(1)
    
    def run(self):
        """Executa o painel principal"""
        self.clear_screen()
        
        # Iniciar thread de monitoramento
        self.running.set()
        monitor_thread = Thread(target=self.poll_status)
        monitor_thread.daemon = True
        monitor_thread.start()
        
        while True:
            self.update_display()
            
            try:
                choice = input("Escolha uma opção: ").strip().lower()
                
                if choice == 'i':
                    self.start_diagnostic()
                elif choice == 'r':
                    self.get_report()
                elif choice == 's':
                    self.check_backend_status()
                elif choice == 'd':
                    self.list_devices()
                elif choice == 'q':
                    print("\n\033[1;33mEncerrando...\033[0m\n")
                    break
                else:
                    print("\033[1;31mOpção inválida!\033[0m\n")
                    time.sleep(1)
                    
            except KeyboardInterrupt:
                print("\n\n\033[1;33mEncerrando...\033[0m\n")
                break
            except Exception as e:
                print(f"\033[1;31mErro: {e}\033[0m\n")
        
        self.running.clear()


def main():
    """Função principal"""
    print("\033[1;32m" + "=" * 80)
    print("  SSD DIAGNOSTIC SUITE - CLI Dashboard")
    print("=" * 80 + "\033[0m\n")
    
    try:
        dashboard = SimpleDashboard()
        dashboard.run()
    except Exception as e:
        print(f"\033[1;31mErro fatal: {e}\033[0m")
        sys.exit(1)


if __name__ == "__main__":
    main()

