import { useEffect, useState } from 'react'
import {
  AppBar,
  Toolbar,
  Typography,
  Container,
  Grid,
  Paper,
  Box,
  Button,
  Alert,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Card,
  CardContent,
  LinearProgress,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Switch,
  FormControlLabel,
  IconButton,
  Snackbar,
  Chip,
} from '@mui/material'
import {
  PlayArrow as StartIcon,
  Settings as SettingsIcon,
  Download as DownloadIcon,
  Storage as StorageIcon,
  Speed as SpeedIcon,
  Memory as MemoryIcon,
} from '@mui/icons-material'
import { ProgressBar } from './components/ProgressBar'
import { PhaseList, type Phase } from './components/PhaseList'
import { connectSocket, disconnectSocket, getApiBase } from './api/socket'

interface StatusPayload {
  phase?: string
  progress?: number
  message?: string
  read_mb_s?: number
  write_mb_s?: number
}

interface Device {
  path: string
  name: string
  model: string
  bus: string
  size: string
  type: string
}

interface Metrics {
  read_speed: number
  write_speed: number
  temperature: number
  health: number
  smart_data: any
  io_operations: number
  error_rate: number
  power_on_hours: number
  power_cycle_count: number
  bad_blocks: number
  wear_level: number
  avg_latency: number
  iops: number
}

interface Config {
    test_duration: number
    enable_advanced_analysis: boolean
    enable_ai_insights: boolean
    test_mode: 'simple' | 'advanced'
}

interface AdvancedConfig {
    enable_deep_scan: boolean
    enable_performance_test: boolean
    enable_integrity_check: boolean
    enable_wear_analysis: boolean
    smart_test_depth: 'basic' | 'standard' | 'deep'
}

function App() {
  const [progress, setProgress] = useState(0)
  const [message, setMessage] = useState('Aguardando início...')
  const [phases, setPhases] = useState<Phase[]>([
    { key: 'smart', title: 'Coleta SMART', status: 'pending' },
    { key: 'read', title: 'Teste de Leitura', status: 'pending' },
    { key: 'write', title: 'Teste de Escrita', status: 'pending' },
    { key: 'analysis', title: 'Análise Avançada', status: 'pending' },
    { key: 'report', title: 'Geração de Relatório', status: 'pending' },
  ])
  const [isMonitoring, setIsMonitoring] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [devices, setDevices] = useState<Device[]>([])
  const [selectedDevice, setSelectedDevice] = useState<string>('')
  const [metrics, setMetrics] = useState<Metrics>({
    read_speed: 0,
    write_speed: 0,
    temperature: 0,
    health: 0,
    smart_data: {},
    io_operations: 0,
    error_rate: 0,
    power_on_hours: 0,
    power_cycle_count: 0,
    bad_blocks: 0,
    wear_level: 0,
    avg_latency: 0,
    iops: 0
  })
  const [config, setConfig] = useState<Config>({
    test_duration: 60,
    enable_advanced_analysis: true,
    enable_ai_insights: true,
    test_mode: 'simple' as 'simple' | 'advanced'
  })
  
  const [advancedConfig, setAdvancedConfig] = useState<AdvancedConfig>({
    enable_deep_scan: false,
    enable_performance_test: true,
    enable_integrity_check: false,
    enable_wear_analysis: true,
    smart_test_depth: 'standard' as 'basic' | 'standard' | 'deep'
  })
  
  const [settingsOpen, setSettingsOpen] = useState(false)
  const [confirmOpen, setConfirmOpen] = useState(false)
  const [aiInsights, setAiInsights] = useState<string>('')
  const [successMessage, setSuccessMessage] = useState<string | null>(null)

  useEffect(() => {
    loadDevices()
    loadConfig()
  }, [])

  useEffect(() => {
    const socket = connectSocket()

    socket.on('connect', () => {
      setMessage('Conectado ao backend.')
      setError(null)
    })

    socket.on('status', (payload: StatusPayload) => {
      if (typeof payload.progress === 'number') {
        setProgress(payload.progress)
      }
      if (payload.message) {
        setMessage(payload.message)
      }
      
      // Atualiza fase atual
      if (payload.phase) {
        setPhases(prev => prev.map(p => {
          if (p.key === payload.phase) {
            return { ...p, status: 'running' }
          } else if (prev.findIndex(ph => ph.key === payload.phase) > prev.findIndex(ph => ph.key === p.key)) {
            return { ...p, status: 'done' }
          }
          return p
        }))
      }
    })

    socket.on('metrics_update', (metrics: Metrics) => {
      setMetrics(metrics)
    })

    socket.on('phase_done', (phaseKey: string) => {
      setPhases(prev => prev.map(p => {
        if (p.key === phaseKey) {
          return { ...p, status: 'done' }
        }
        return p
      }))
    })

    socket.on('diagnostic_complete', (data: any) => {
      if (data.ai_insights) {
        setAiInsights(data.ai_insights)
      }
      setIsMonitoring(false)
    })

    socket.on('error', (err: { message: string }) => {
      setError(err.message)
    })

    socket.on('disconnect', () => {
      setMessage('Desconectado do backend.')
    })

    return () => {
      disconnectSocket()
    }
  }, [])

  async function loadDevices() {
    try {
      const response = await fetch(`${getApiBase()}/devices`)
      const data = await response.json()
      setDevices(data)
      if (data.length > 0 && !selectedDevice) {
        setSelectedDevice(data[0].path)
      }
    } catch (err: any) {
      console.error('Erro ao carregar dispositivos:', err)
    }
  }

  async function loadConfig() {
    try {
      const response = await fetch(`${getApiBase()}/config`)
      const data = await response.json()
      setConfig(data)
    } catch (err: any) {
      console.error('Erro ao carregar configurações:', err)
    }
  }

  async function loadMetrics() {
    try {
      const response = await fetch(`${getApiBase()}/metrics`)
      const data = await response.json()
      setMetrics(data)
    } catch (err: any) {
      console.error('Erro ao carregar métricas:', err)
    }
  }

  async function startDiagnostic() {
    if (!selectedDevice) {
      setError('Selecione um dispositivo')
      return
    }

    try {
      setError(null)
      setIsMonitoring(true)
      setProgress(0)
      setMessage('Iniciando diagnóstico...')
      setAiInsights('')
      
      const device = devices.find(d => d.path === selectedDevice)
      
      if (!device) {
        setError('Dispositivo não encontrado')
        setIsMonitoring(false)
        return
      }
      
      const response = await fetch(`${getApiBase()}/run`, { 
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ device })
      })
      
      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.error || 'Falha ao iniciar diagnóstico')
      }
      
      setMessage('Diagnóstico em execução...')
    } catch (err: any) {
      console.error('Erro no startDiagnostic:', err)
      setError(`Erro ao iniciar: ${err.message}`)
      setIsMonitoring(false)
    }
  }

  async function downloadReport() {
    try {
      const response = await fetch(`${getApiBase()}/report`)
      if (response.ok) {
        const data = await response.json()
        const timestamp = new Date().toISOString().replace(/[:.]/g, '-')
        const deviceModel = data.selected_device?.model || 'unknown'
        const reportName = `Relatorio-${deviceModel}-${timestamp}.json`
        
        // Criar relatório completo formatado
        const reportContent = JSON.stringify(data, null, 2)
        const blob = new Blob([reportContent], { type: 'application/json' })
        
        // Download direto
        const url = window.URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = reportName
        document.body.appendChild(a)
        a.click()
        document.body.removeChild(a)
        window.URL.revokeObjectURL(url)
        
        setSuccessMessage('Relatório salvo com sucesso!')
        setTimeout(() => setSuccessMessage(null), 3000)
      } else {
        setError('Relatório ainda não disponível')
      }
    } catch (err: any) {
      setError(`Erro ao baixar relatório: ${err.message}`)
    }
  }

  function handleOpenSaveConfirm() {
    setConfirmOpen(true)
  }

  async function updateConfig() {
    try {
      const response = await fetch(`${getApiBase()}/config`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(config)
      })
      if (response.ok) {
        setConfirmOpen(false)
        setSuccessMessage('Configurações salvas com sucesso!')
        setTimeout(() => {
          setSuccessMessage(null)
          setSettingsOpen(false)
        }, 2000)
      }
    } catch (err: any) {
      setError(`Erro ao atualizar configurações: ${err.message}`)
      setConfirmOpen(false)
    }
  }

  useEffect(() => {
    if (isMonitoring) {
      const interval = setInterval(loadMetrics, 1000)
      return () => clearInterval(interval)
    }
  }, [isMonitoring])

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh', bgcolor: 'background.default' }}>
      <AppBar position="static">
        <Toolbar>
          <Typography variant="h6" sx={{ flexGrow: 1 }}>
            SSD Diagnostic Suite
          </Typography>
          {config.test_mode === 'advanced' && (
            <Chip 
              label="Modo Avançado" 
              color="primary" 
              size="small" 
              sx={{ mr: 1, fontWeight: 'bold' }} 
            />
          )}
          <IconButton color="inherit" onClick={() => setSettingsOpen(true)}>
            <SettingsIcon />
          </IconButton>
          <Button 
            color="inherit" 
            onClick={startDiagnostic}
            disabled={isMonitoring || !selectedDevice}
            startIcon={<StartIcon />}
            sx={{ ml: 1 }}
          >
            {isMonitoring ? 'Executando...' : 'Iniciar Diagnóstico'}
          </Button>
        </Toolbar>
      </AppBar>

      <Container maxWidth="xl" sx={{ py: 4, flex: 1 }}>
        {error && (
          <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
            {error}
          </Alert>
        )}
        
        {successMessage && (
          <Alert severity="success" sx={{ mb: 2 }} onClose={() => setSuccessMessage(null)}>
            {successMessage}
          </Alert>
        )}

        <Grid container spacing={3}>
          {/* Painel Esquerdo */}
          <Grid item xs={12} md={4}>
            {/* Seleção de Dispositivo */}
            <Paper sx={{ p: 3, mb: 2 }}>
              <Typography variant="h6" gutterBottom>
                Selecione o Dispositivo
              </Typography>
              <FormControl fullWidth>
                <InputLabel>Dispositivo</InputLabel>
                <Select
                  value={selectedDevice}
                  label="Dispositivo"
                  onChange={(e) => setSelectedDevice(e.target.value)}
                  disabled={isMonitoring}
                >
                  {devices.map((device) => (
                    <MenuItem key={device.path} value={device.path}>
                      <Box>
                        <Typography variant="body2" fontWeight="bold">
                          {device.model}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          {device.path} • {device.bus} • {device.size}
                        </Typography>
                      </Box>
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Paper>

            {/* Status da Execução */}
            <Paper sx={{ p: 3, mb: 2 }}>
              <Typography variant="h6" gutterBottom>
                Status da Execução
              </Typography>
              <ProgressBar value={progress} label={message} />
              
            {/* Métricas em Tempo Real */}
            {isMonitoring && metrics.read_speed > 0 && (
              <Box sx={{ mt: 3 }}>
                <Typography variant="subtitle2" gutterBottom>
                  Métricas em Tempo Real
                </Typography>
                <Grid container spacing={1}>
                  <Grid item xs={6}>
                    <Box sx={{ textAlign: 'center' }}>
                      <SpeedIcon sx={{ fontSize: 35, color: 'primary.main' }} />
                      <Typography variant="h6" color="primary">
                        {metrics.read_speed.toFixed(1)} MB/s
                      </Typography>
                      <Typography variant="caption">Leitura</Typography>
                    </Box>
                  </Grid>
                  <Grid item xs={6}>
                    <Box sx={{ textAlign: 'center' }}>
                      <SpeedIcon sx={{ fontSize: 35, color: 'secondary.main' }} />
                      <Typography variant="h6" color="secondary">
                        {metrics.write_speed.toFixed(1)} MB/s
                      </Typography>
                      <Typography variant="caption">Escrita</Typography>
                    </Box>
                  </Grid>
                  {metrics.iops > 0 && (
                    <Grid item xs={12}>
                      <Typography variant="caption" color="text.secondary" display="block" textAlign="center">
                        IOPS: {metrics.iops.toLocaleString()} | Temp: {metrics.temperature}°C
                      </Typography>
                    </Grid>
                  )}
                </Grid>
              </Box>
            )}
            </Paper>

            {/* Etapas */}
            <Paper sx={{ p: 3, mb: 2 }}>
              <Typography variant="h6" gutterBottom>
                Etapas
              </Typography>
              <PhaseList phases={phases} />
              
              <Box sx={{ mt: 3, display: 'flex', gap: 1 }}>
                <Button 
                  variant="outlined" 
                  onClick={downloadReport}
                  startIcon={<DownloadIcon />}
                  fullWidth
                  disabled={progress < 100}
                >
                  Baixar Relatório
                </Button>
              </Box>
            </Paper>

            {/* Insights de IA */}
            {aiInsights && (
              <Paper sx={{ p: 3, bgcolor: 'primary.light', color: 'primary.contrastText' }}>
                <Typography variant="h6" gutterBottom>
                  🤖 Análise por IA
                </Typography>
                <Typography variant="body2" sx={{ whiteSpace: 'pre-line' }}>
                  {aiInsights}
                </Typography>
              </Paper>
            )}
          </Grid>

          {/* Painel Direito */}
          <Grid item xs={12} md={8}>
            {/* Análise em Tempo Real */}
            <Paper sx={{ p: 3, mb: 2 }}>
              <Typography variant="h6" gutterBottom>
                📊 Análise em Tempo Real
              </Typography>
              <Box 
                sx={{ 
                  height: 300, 
                  display: 'flex', 
                  flexDirection: 'column',
                  alignItems: 'center', 
                  justifyContent: 'center', 
                  background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                  borderRadius: 2,
                  position: 'relative',
                  overflow: 'hidden'
                }}
              >
                <Box sx={{ 
                  position: 'absolute',
                  top: 0,
                  left: 0,
                  right: 0,
                  bottom: 0,
                  background: `conic-gradient(from 0deg, 
                    rgba(255,255,255,0.1) ${progress}%, 
                    transparent ${progress}%)`
                }} />
                <Typography variant="h2" sx={{ color: 'white', fontWeight: 'bold', zIndex: 1 }}>
                  {progress}%
                </Typography>
                <Typography sx={{ color: 'rgba(255,255,255,0.9)', mt: 1, zIndex: 1 }}>
                  {message}
                </Typography>
              </Box>
            </Paper>

            {/* Métricas Avançadas */}
            {isMonitoring && (
              <Grid container spacing={2}>
                <Grid item xs={12} md={4}>
                  <Card>
                    <CardContent>
                      <MemoryIcon sx={{ fontSize: 40, color: 'info.main', mb: 1 }} />
                      <Typography variant="h5" color="info.main">
                        {metrics.health?.toFixed(1) || 0}%
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Saúde do Disco
                      </Typography>
                      <LinearProgress 
                        variant="determinate" 
                        value={metrics.health || 0} 
                        sx={{ mt: 1 }}
                        color={metrics.health > 90 ? 'success' : metrics.health > 50 ? 'warning' : 'error'}
                      />
                    </CardContent>
                  </Card>
                </Grid>
                
                <Grid item xs={12} md={4}>
                  <Card>
                    <CardContent>
                      <SpeedIcon sx={{ fontSize: 40, color: 'error.main', mb: 1 }} />
                      <Typography variant="h5" color="error.main">
                        {metrics.temperature?.toFixed(1) || 0}°C
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Temperatura
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>

                <Grid item xs={12} md={4}>
                  <Card>
                    <CardContent>
                      <StorageIcon sx={{ fontSize: 40, color: 'success.main', mb: 1 }} />
                      <Typography variant="h5" color="success.main">
                        {((metrics.read_speed || 0) + (metrics.write_speed || 0)).toFixed(1)} MB/s
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Performance Total
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>

                {/* Novas métricas */}
                {metrics.iops > 0 && (
                  <Grid item xs={12} md={4}>
                    <Card>
                      <CardContent>
                        <SpeedIcon sx={{ fontSize: 40, color: 'warning.main', mb: 1 }} />
                        <Typography variant="h5" color="warning.main">
                          {metrics.iops.toLocaleString()}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          IOPS
                        </Typography>
                      </CardContent>
                    </Card>
                  </Grid>
                )}

                {metrics.avg_latency > 0 && (
                  <Grid item xs={12} md={4}>
                    <Card>
                      <CardContent>
                        <MemoryIcon sx={{ fontSize: 40, color: 'secondary.main', mb: 1 }} />
                        <Typography variant="h5" color="secondary.main">
                          {(metrics.avg_latency * 1000).toFixed(2)}ms
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          Latência Média
                        </Typography>
                      </CardContent>
                    </Card>
                  </Grid>
                )}

                {metrics.wear_level > 0 && (
                  <Grid item xs={12} md={4}>
                    <Card>
                      <CardContent>
                        <StorageIcon sx={{ fontSize: 40, color: 'error.main', mb: 1 }} />
                        <Typography variant="h5" color="error.main">
                          {metrics.wear_level.toFixed(1)}%
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          Desgaste
                        </Typography>
                      </CardContent>
                    </Card>
                  </Grid>
                )}
              </Grid>
            )}
          </Grid>
        </Grid>
      </Container>

      {/* Dialog de Configurações */}
      <Dialog open={settingsOpen} onClose={() => setSettingsOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>
          Configurações do Diagnóstico
          <Box sx={{ mt: 1, display: 'flex', gap: 1 }}>
            <Button
              size="small"
              variant={config.test_mode === 'simple' ? 'contained' : 'outlined'}
              onClick={() => setConfig({ ...config, test_mode: 'simple' })}
            >
              Modo Simplificado
            </Button>
            <Button
              size="small"
              variant={config.test_mode === 'advanced' ? 'contained' : 'outlined'}
              onClick={() => setConfig({ ...config, test_mode: 'advanced' })}
            >
              Modo Avançado
            </Button>
          </Box>
        </DialogTitle>
        <DialogContent>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3, pt: 2 }}>
            {/* Configurações Básicas */}
            <Box>
              <Typography variant="h6" gutterBottom>Configurações Básicas</Typography>
              <FormControlLabel
                control={
                  <Switch
                    checked={config.enable_ai_insights}
                    onChange={(e) => setConfig({ ...config, enable_ai_insights: e.target.checked })}
                  />
                }
                label="Insights por IA (Groq - Gratuito)"
              />
              <Typography variant="caption" display="block" color="text.secondary" sx={{ ml: 4 }}>
                Análise inteligente dos dados com IA gratuita
              </Typography>
            </Box>

            {/* Configurações Avançadas */}
            {config.test_mode === 'advanced' && (
              <Box>
                <Typography variant="h6" gutterBottom>Configurações Avançadas</Typography>
                
                <FormControlLabel
                  control={
                    <Switch
                      checked={advancedConfig.enable_deep_scan}
                      onChange={(e) => setAdvancedConfig({ ...advancedConfig, enable_deep_scan: e.target.checked })}
                    />
                  }
                  label="Scan Profundo (mais lento, mais completo)"
                />
                
                <FormControlLabel
                  control={
                    <Switch
                      checked={advancedConfig.enable_performance_test}
                      onChange={(e) => setAdvancedConfig({ ...advancedConfig, enable_performance_test: e.target.checked })}
                    />
                  }
                  label="Teste de Performance Completo"
                />
                
                <FormControlLabel
                  control={
                    <Switch
                      checked={advancedConfig.enable_integrity_check}
                      onChange={(e) => setAdvancedConfig({ ...advancedConfig, enable_integrity_check: e.target.checked })}
                    />
                  }
                  label="Verificação de Integridade de Dados"
                />
                
                <FormControlLabel
                  control={
                    <Switch
                      checked={advancedConfig.enable_wear_analysis}
                      onChange={(e) => setAdvancedConfig({ ...advancedConfig, enable_wear_analysis: e.target.checked })}
                    />
                  }
                  label="Análise de Desgaste Detalhada"
                />

                <FormControl fullWidth sx={{ mt: 2 }}>
                  <InputLabel>Profundidade do Teste SMART</InputLabel>
                  <Select
                    value={advancedConfig.smart_test_depth}
                    label="Profundidade do Teste SMART"
                    onChange={(e) => setAdvancedConfig({ ...advancedConfig, smart_test_depth: e.target.value as 'basic' | 'standard' | 'deep' })}
                  >
                    <MenuItem value="basic">Básico (Rápido)</MenuItem>
                    <MenuItem value="standard">Padrão (Recomendado)</MenuItem>
                    <MenuItem value="deep">Profundo (Lento)</MenuItem>
                  </Select>
                </FormControl>
              </Box>
            )}

            {/* Informações */}
            <Alert severity="info">
              {config.test_mode === 'simple' ? (
                <>
                  <strong>Modo Simplificado:</strong> Testes básicos e rápidos. 
                  Ideal para usuários que querem uma visão geral rápida do estado do SSD.
                </>
              ) : (
                <>
                  <strong>Modo Avançado:</strong> Análises completas e detalhadas. 
                  Demora mais, mas fornece informações completas sobre o estado do SSD.
                </>
              )}
            </Alert>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setSettingsOpen(false)}>Cancelar</Button>
          <Button onClick={handleOpenSaveConfirm} variant="contained">Salvar Configurações</Button>
        </DialogActions>
      </Dialog>

      {/* Dialog de Confirmação */}
      <Dialog open={confirmOpen} onClose={() => setConfirmOpen(false)} maxWidth="xs" fullWidth>
        <DialogTitle>Confirmar Alterações</DialogTitle>
        <DialogContent>
          <Typography>
            {config.test_mode === 'advanced' && advancedConfig.enable_deep_scan ? (
              <>Deseja realmente alterar para o modo avançado com scan profundo? Esta análise será mais demorada.</>
            ) : config.test_mode === 'advanced' ? (
              <>Deseja realmente salvar as configurações do modo avançado?</>
            ) : (
              <>Deseja realmente salvar as configurações?</>
            )}
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setConfirmOpen(false)}>Cancelar</Button>
          <Button onClick={updateConfig} variant="contained" color="primary">
            Confirmar e Salvar
          </Button>
        </DialogActions>
      </Dialog>

      {/* Snackbar para mensagens de sucesso */}
      <Snackbar
        open={!!successMessage}
        autoHideDuration={3000}
        onClose={() => setSuccessMessage(null)}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert severity="success" onClose={() => setSuccessMessage(null)}>
          {successMessage}
        </Alert>
      </Snackbar>
    </Box>
  )
}

export default App
