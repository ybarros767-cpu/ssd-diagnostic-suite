#!/usr/bin/env bash
# =====================================================================
# ssd_diag_auto_enhanced.sh — Diagnóstico avançado de SSD (SATA/NVMe/USB)
# Análise profissional com IA e métricas detalhadas de performance
# Modo profissional: sem prompts, barra de progresso dinâmica e ETA
# Integração com GPT-4 para análise preditiva e recomendações técnicas
# =====================================================================

set -Eeuo pipefail
export LC_ALL=C

# -------- Configuração de execução --------
QUIET=${QUIET:-0}
TARGET=${TARGET:-""}
QUICK=${QUICK:-0}
NO_BADBLOCKS=${NO_BADBLOCKS:-0}
NO_SELFTEST=${NO_SELFTEST:-0}
RUN_LONG=${RUN_LONG:-0}
DEEP_SCAN=${DEEP_SCAN:-0}       # Nova opção para scan profundo
BENCHMARK=${BENCHMARK:-1}        # Novo: benchmark de performance
COLLECT_THERMAL=${COLLECT_THERMAL:-1}  # Novo: monitoramento térmico
COLLECT_SMART_HISTORY=${COLLECT_SMART_HISTORY:-1}  # Novo: histórico SMART

# -------- IA (configuração expandida) --------
OPENAI_MODEL=${OPENAI_MODEL:-gpt-4o}
OPENAI_TEMPERATURE=${OPENAI_TEMPERATURE:-0.1}
OPENAI_MAX_TOKENS=${OPENAI_MAX_TOKENS:-4000}     # Aumentado para análise mais profunda
REPORT_MAX_LOG_CHARS=${REPORT_MAX_LOG_CHARS:-40000}  # Aumentado para mais contexto
REPORT_MAX_LOG_LINES=${REPORT_MAX_LOG_LINES:-2000}   # Aumentado para mais detalhes

# -------- Parâmetros técnicos --------
SMART_POLL_INTERVAL=30          # Intervalo de polling SMART (segundos)
THERMAL_POLL_INTERVAL=10        # Intervalo de polling térmico (segundos)
IO_TIMEOUT=120                  # Timeout para operações I/O (segundos)
MAX_RETRY_COUNT=3              # Tentativas máximas para operações críticas

# -------- Log técnico local --------
LOGFILE="debug_run.log"
exec > >(tee -a "$LOGFILE") 2>&1

# -------- Cronometria e progresso --------
START_TIME=$(date +%s)
timestamp() { date "+%Y-%m-%d %H:%M:%S"; }
elapsed()   { echo $(( $(date +%s) - START_TIME )); }
fmt_dur()   { local s=$1; printf "%02d:%02d:%02d" $((s/3600)) $((s%3600/60)) $((s%60)); }

# Etapas e pesos (total=100) - Expandido com novas etapas
STEP_NAMES=(
  "Dependências" "Coleta básica" "Coleta SMART" "Coleta térmica" 
  "Benchmarks" "Autotestes" "Badblocks" "Deep scan" 
  "Análise local" "IA básica" "IA preditiva" "Relatórios"
)
STEP_WEIGHTS=(8 10 12 8 12 10 15 5 5 5 5 5)
STEP_CUR=0
STEP_PROGRESS=0
PROG_STOP=0

# -------- Logging aprimorado --------
log()       { [[ "$QUIET" -eq 1 ]] && return 0; echo "[$1] $(timestamp) | ${*:2}"; }
log_step()  { log STEP "$@"; }
log_info()  { log INFO "$@"; }
log_warn()  { log WARN "$@" >&2; }
log_error() { log ERROR "$@" >&2; }
log_debug() { [[ "${DEBUG:-0}" -eq 1 ]] && log DEBUG "$@"; }

# -------- Barra de progresso dinâmica --------
print_progress() {
  local total=0 cur=0 i
  for i in "${STEP_WEIGHTS[@]}"; do total=$((total+i)); done
  local sum_prev=0
  local idx=0
  while (( idx < STEP_CUR )); do sum_prev=$((sum_prev + STEP_WEIGHTS[idx])); idx=$((idx+1)); done
  local stepw=${STEP_WEIGHTS[$STEP_CUR]:-0}
  local pct=$(( (sum_prev*100 + stepw*STEP_PROGRESS) / total ))
  (( pct>100 )) && pct=100
  
  # Barra de progresso visual aprimorada
  local width=30
  local filled=$(( width * pct / 100 ))
  local empty=$(( width - filled ))
  local bar=""
  for ((i=0; i<filled; i++)); do bar+="█"; done
  for ((i=0; i<empty; i++)); do bar+="░"; done

  local name="${STEP_NAMES[$STEP_CUR]}"
  local e=$(elapsed)
  
  # ETA dinâmico baseado em métricas históricas
  local eta_base=180
  (( NO_BADBLOCKS==0 && QUICK==0 )) && eta_base=$((eta_base+900))
  (( RUN_LONG==1 )) && eta_base=$((eta_base+1800))
  (( DEEP_SCAN==1 )) && eta_base=$((eta_base+1200))
  (( BENCHMARK==1 )) && eta_base=$((eta_base+600))
  local eta=$((eta_base * (100-pct) / 100))
  (( eta < 0 )) && eta=0

  printf "\r%s %3d%% - %s | %s decorrido | ETA: %s  " "$bar" "$pct" "$name" "$(fmt_dur "$e")" "$(fmt_dur "$eta")"
}

progress_thread() {
  while (( PROG_STOP == 0 )); do
    print_progress
    sleep 5
  done
  print_progress
  echo
}

start_progress() { PROG_STOP=0; progress_thread & PROG_PID=$!; }
stop_progress()  { PROG_STOP=1; [[ -n "${PROG_PID:-}" ]] && wait "$PROG_PID" 2>/dev/null || true; }

next_step() { STEP_CUR=$((STEP_CUR+1)); STEP_PROGRESS=0; }
step_progress() {
  local p=$1
  (( p<0 )) && p=0
  (( p>100 )) && p=100
  STEP_PROGRESS=$p
}

# -------- Funções de utilidade aprimoradas --------
is_nvme()     { [[ "$1" =~ /dev/nvme[0-9]+n[0-9]+ ]]; }
is_usb()      { lsblk -no TRAN "$1" 2>/dev/null | grep -qi usb; }
list_disks()  { lsblk -ndo NAME,TYPE | awk '$2=="disk"{print "/dev/"$1}'; }
pretty()      { lsblk -o NAME,PATH,SIZE,MODEL,SERIAL,TRAN,MOUNTPOINTS,FSTYPE,LABEL -d; }

get_smart_value() {
    local dev=$1 attr=$2
    local val
    if is_nvme "$dev"; then
        val=$(nvme smart-log "$dev" 2>/dev/null | grep -i "$attr" | awk '{print $NF}')
    else
        val=$(smartctl -A "$dev" 2>/dev/null | grep -i "$attr" | awk '{print $10}')
    fi
    echo "${val:-0}"
}

get_temperature() {
    local dev=$1
    if is_nvme "$dev"; then
        nvme smart-log "$dev" 2>/dev/null | grep -i "temperature" | head -1 | awk '{print $3}'
    else
        smartctl -A "$dev" 2>/dev/null | grep -i "temperature" | head -1 | awk '{print $10}'
    fi
}

# -------- Funções de benchmark --------
run_disk_benchmark() {
    local dev=$1
    local results="$OUTDIR/benchmark_results.txt"
    log_step "Executando benchmarks de performance"
    
    # FIO - testes sintéticos
    if command -v fio &>/dev/null; then
        log_info "Executando testes FIO..."
        {
            # Teste de leitura sequencial
            fio --name=seq_read --filename="$dev" --direct=1 --rw=read \
                --bs=1M --size=1G --numjobs=1 --runtime=60 --time_based
            
            # Teste de leitura aleatória
            fio --name=rand_read --filename="$dev" --direct=1 --rw=randread \
                --bs=4k --size=1G --numjobs=4 --runtime=60 --time_based
            
            # Teste IOPS
            fio --name=iops_test --filename="$dev" --direct=1 --rw=randrw \
                --bs=4k --size=1G --numjobs=4 --runtime=60 --time_based
        } > "$results" 2>&1
    fi
    
    # DD - teste básico de throughput
    log_info "Executando teste DD..."
    {
        echo "=== DD Read Test ==="
        dd if="$dev" of=/dev/null bs=1M count=1000 2>&1
    } >> "$results"
    
    step_progress 100
}

# -------- Monitoramento térmico -------- 
start_thermal_monitoring() {
    local dev=$1
    local thermal_log="$OUTDIR/thermal_history.log"
    
    log_info "Iniciando monitoramento térmico..."
    while true; do
        local temp=$(get_temperature "$dev")
        echo "$(date +%s) $temp" >> "$thermal_log"
        sleep "$THERMAL_POLL_INTERVAL"
    done &
    THERMAL_PID=$!
}

stop_thermal_monitoring() {
    [[ -n "${THERMAL_PID:-}" ]] && kill "$THERMAL_PID" 2>/dev/null || true
}

# -------- Coleta de dados aprimorada --------
collect_smart_history() {
    local dev=$1
    local history_file="$OUTDIR/smart_history.log"
    local start_time=$(date +%s)
    local duration=600  # 10 minutos de coleta
    
    log_info "Coletando histórico SMART..."
    while (( $(date +%s) - start_time < duration )); do
        if is_nvme "$dev"; then
            nvme smart-log "$dev" >> "$history_file" 2>/dev/null
        else
            smartctl -A "$dev" >> "$history_file" 2>/dev/null
        fi
        sleep "$SMART_POLL_INTERVAL"
    done
}

collect_deep_data() {
    local dev=$1
    log_step "Coleta profunda de dados"
    
    # Coleta de logs do sistema
    journalctl --since "24 hours ago" | grep -i "storage\|disk\|nvme\|ata" > "$OUTDIR/system_logs.txt"
    
    # Análise de performance do dispositivo
    if command -v iostat &>/dev/null; then
        iostat -x 1 60 > "$OUTDIR/iostat_data.txt" &
        IOSTAT_PID=$!
    fi
    
    # Eventos SMART detalhados
    if ! is_nvme "$dev"; then
        smartctl -l xerror "$dev" > "$OUTDIR/smart_xerror.txt" 2>/dev/null
        smartctl -l directory "$dev" > "$OUTDIR/smart_directory.txt" 2>/dev/null
        smartctl -l background "$dev" > "$OUTDIR/smart_background.txt" 2>/dev/null
    fi
    
    step_progress 100
}

# -------- Análise avançada --------
analyze_performance_metrics() {
    local dev=$1
    python3 - <<PY
import json, os, re
from datetime import datetime

def parse_fio_results(file):
    results = {}
    if os.path.exists(file):
        with open(file, 'r') as f:
            data = f.read()
            # Parse FIO results
            iops = re.findall(r'iops=(\d+)', data)
            bw = re.findall(r'bw=(\d+)([KMG])iB/s', data)
            results['iops'] = [int(i) for i in iops]
            results['bandwidth'] = []
            for val, unit in bw:
                multiplier = {'K': 1024, 'M': 1024*1024, 'G': 1024*1024*1024}
                results['bandwidth'].append(int(val) * multiplier[unit])
    return results

def analyze_thermal_history(file):
    results = {'max': 0, 'min': 999, 'avg': 0}
    if os.path.exists(file):
        temps = []
        with open(file, 'r') as f:
            for line in f:
                ts, temp = line.strip().split()
                temps.append(float(temp))
        if temps:
            results['max'] = max(temps)
            results['min'] = min(temps)
            results['avg'] = sum(temps) / len(temps)
    return results

outdir = os.environ.get('OUTDIR', '.')
dev = os.environ.get('DEV', '')

# Análise completa
analysis = {
    'device': dev,
    'timestamp': datetime.utcnow().isoformat(),
    'performance': parse_fio_results(f"{outdir}/benchmark_results.txt"),
    'thermal': analyze_thermal_history(f"{outdir}/thermal_history.log"),
    'recommendations': []
}

# Gerar recomendações baseadas em métricas
if analysis['thermal']['max'] > 70:
    analysis['recommendations'].append({
        'type': 'warning',
        'message': 'Temperatura máxima acima do ideal. Verificar refrigeração.'
    })

if analysis['performance'].get('iops', []):
    avg_iops = sum(analysis['performance']['iops']) / len(analysis['performance']['iops'])
    if avg_iops < 1000:
        analysis['recommendations'].append({
            'type': 'performance',
            'message': f'Performance abaixo do esperado (IOPS: {avg_iops:.0f})'
        })

with open(f"{outdir}/performance_analysis.json", 'w') as f:
    json.dump(analysis, f, indent=2)
PY
}

# -------- Geração de relatórios aprimorada --------
generate_advanced_reports() {
    log_step "Gerando relatórios avançados"
    
    # Relatório técnico detalhado em HTML
    python3 - <<'PY'
import json, os
from datetime import datetime
import plotly.graph_objects as go
from plotly.subplots import make_subplots

outdir = os.environ.get('OUTDIR', '.')

def create_thermal_plot():
    thermal_file = f"{outdir}/thermal_history.log"
    if os.path.exists(thermal_file):
        times, temps = [], []
        with open(thermal_file, 'r') as f:
            for line in f:
                ts, temp = line.strip().split()
                times.append(datetime.fromtimestamp(int(ts)))
                temps.append(float(temp))
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=times, y=temps, name='Temperatura'))
        fig.update_layout(title='Histórico Térmico',
                         xaxis_title='Tempo',
                         yaxis_title='Temperatura (°C)')
        fig.write_html(f"{outdir}/thermal_plot.html")

def create_performance_plot():
    perf_file = f"{outdir}/performance_analysis.json"
    if os.path.exists(perf_file):
        with open(perf_file, 'r') as f:
            data = json.load(f)
        
        if 'performance' in data:
            fig = make_subplots(rows=2, cols=1,
                              subplot_titles=('IOPS', 'Bandwidth'))
            
            if 'iops' in data['performance']:
                fig.add_trace(
                    go.Scatter(y=data['performance']['iops'],
                              name='IOPS'),
                    row=1, col=1)
            
            if 'bandwidth' in data['performance']:
                fig.add_trace(
                    go.Scatter(y=data['performance']['bandwidth'],
                              name='Bandwidth'),
                    row=2, col=1)
            
            fig.update_layout(height=800, title='Métricas de Performance')
            fig.write_html(f"{outdir}/performance_plot.html")

# Gerar visualizações
create_thermal_plot()
create_performance_plot()

# Gerar relatório HTML
html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Relatório Técnico Detalhado - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        .section {{ margin: 20px 0; }}
        .warning {{ color: #f44336; }}
        .info {{ color: #2196F3; }}
    </style>
</head>
<body>
    <h1>Relatório Técnico Detalhado</h1>
    
    <div class="section">
        <h2>Análise de Performance</h2>
        <iframe src="performance_plot.html" width="100%" height="800px" frameborder="0"></iframe>
    </div>
    
    <div class="section">
        <h2>Análise Térmica</h2>
        <iframe src="thermal_plot.html" width="100%" height="400px" frameborder="0"></iframe>
    </div>
    
    <div class="section">
        <h2>Recomendações</h2>
        {''.join([
            f"<p class='{rec['type']}'>{rec['message']}</p>"
            for rec in json.load(open(f"{outdir}/performance_analysis.json"))['recommendations']
        ])}
    </div>
</body>
</html>
"""

with open(f"{outdir}/relatorio_tecnico.html", 'w') as f:
    f.write(html_content)
PY
    
    step_progress 100
}

# -------- Função principal aprimorada --------
main() {
    require_root
    start_progress
    
    # Etapa 0 - Dependências
    STEP_CUR=0; step_progress 0
    install_deps
    
    # Seleção e validação do dispositivo
    if [[ -n "$TARGET" ]]; then
        DEV="$TARGET"
    else
        DEV="$(auto_pick_device)"
    fi
    [[ -b "${DEV:-}" ]] || { stop_progress; log_error "Nenhum disco elegível detectado."; exit 1; }
    
    # Preparação
    prepare_outdir
    export OUTDIR DEV
    safety_checks
    
    # Início do monitoramento térmico
    if (( COLLECT_THERMAL == 1 )); then
        start_thermal_monitoring "$DEV"
    fi
    
    # Coleta de dados básica
    next_step; step_progress 0
    collect_parallel
    
    # Coleta SMART detalhada
    next_step; step_progress 0
    if (( COLLECT_SMART_HISTORY == 1 )); then
        collect_smart_history "$DEV"
    fi
    
    # Coleta térmica
    next_step; step_progress 0
    if (( COLLECT_THERMAL == 1 )); then
        # Aguarda acumulação de dados térmicos
        sleep 60
    fi
    
    # Benchmarks
    next_step; step_progress 0
    if (( BENCHMARK == 1 )); then
        run_disk_benchmark "$DEV"
    fi
    
    # Autotestes
    next_step; step_progress 0
    run_autotests
    
    # Badblocks
    next_step; step_progress 0
    run_badblocks
    
    # Deep scan
    next_step; step_progress 0
    if (( DEEP_SCAN == 1 )); then
        collect_deep_data "$DEV"
    fi
    
    # Análise local
    next_step; step_progress 0
    analyze_local
    analyze_performance_metrics "$DEV"
    
    # IA básica
    next_step; step_progress 0
    call_openai
    
    # IA preditiva (segunda passagem com dados complementares)
    next_step; step_progress 0
    if [[ -n "${OPENAI_API_KEY:-}" ]]; then
        python3 - <<PY
import json, os
import requests

def prepare_predictive_prompt():
    outdir = os.environ.get('OUTDIR', '.')
    with open(f"{outdir}/performance_analysis.json") as f:
        perf_data = json.load(f)
    with open(f"{outdir}/summary.json") as f:
        summary = json.load(f)
    
    prompt = f"""Analise os dados de performance e saúde do dispositivo para gerar:
1. Previsão de vida útil restante
2. Riscos potenciais identificados
3. Recomendações de otimização
4. Necessidade de ações preventivas

Dados de performance: {json.dumps(perf_data, indent=2)}
Dados básicos: {json.dumps(summary, indent=2)}
"""
    return prompt

headers = {
    "Authorization": f"Bearer {os.environ.get('OPENAI_API_KEY')}",
    "Content-Type": "application/json"
}

data = {
    "model": os.environ.get("OPENAI_MODEL", "gpt-4o"),
    "messages": [
        {"role": "system", "content": "Você é um especialista em análise preditiva de storage."},
        {"role": "user", "content": prepare_predictive_prompt()}
    ],
    "temperature": float(os.environ.get("OPENAI_TEMPERATURE", "0.1")),
    "max_tokens": int(os.environ.get("OPENAI_MAX_TOKENS", "2400"))
}

response = requests.post(
    "https://api.openai.com/v1/chat/completions",
    headers=headers,
    json=data
)

if response.status_code == 200:
    content = response.json()["choices"][0]["message"]["content"]
    with open(f"{os.environ.get('OUTDIR')}/analise_preditiva.txt", "w") as f:
        f.write(content)
PY
    fi
    
    # Relatórios
    next_step; step_progress 0
    generate_reports
    generate_advanced_reports
    
    # Finalização
    if (( COLLECT_THERMAL == 1 )); then
        stop_thermal_monitoring
    fi
    if [[ -n "${IOSTAT_PID:-}" ]]; then
        kill "$IOSTAT_PID" 2>/dev/null || true
    fi
    
    stop_progress
    echo
    log_info "Diagnóstico concluído. Relatórios disponíveis em: $OUTDIR"
    
    # Sumário final
    if [[ -f "$OUTDIR/summary.json" ]]; then
        echo
        echo "=== SUMÁRIO DA ANÁLISE ==="
        cat "$OUTDIR/summary.json"
        echo
        echo "Relatórios gerados:"
        echo "- Relatório analítico: $ANALYTIC_PDF"
        echo "- Relatório técnico: $OUTDIR/relatorio_tecnico.html"
        echo "- Análise preditiva: $OUTDIR/analise_preditiva.txt"
        echo "- Dados brutos: $LOG_RAW"
    fi
}

main "$@"