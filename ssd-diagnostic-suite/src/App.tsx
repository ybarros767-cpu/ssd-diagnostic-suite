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
} from '@mui/material'
import {
  PlayArrow as StartIcon,
  Stop as StopIcon,
  Download as DownloadIcon,
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

function App() {
  const [progress, setProgress] = useState(0)
  const [message, setMessage] = useState('Aguardando início...')
  const [phases, setPhases] = useState<Phase[]>([
    { key: 'smart', title: 'Coleta SMART', status: 'pending' },
    { key: 'read', title: 'Teste de Leitura', status: 'pending' },
    { key: 'write', title: 'Teste de Escrita', status: 'pending' },
    { key: 'report', title: 'Geração de Relatório', status: 'pending' },
  ])
  const [isMonitoring, setIsMonitoring] = useState(false)
  const [error, setError] = useState<string | null>(null)

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
          }
          return p
        }))
      }
    })

    socket.on('phase_done', (phaseKey: string) => {
      setPhases(prev => prev.map(p => {
        if (p.key === phaseKey) {
          return { ...p, status: 'done' }
        }
        return p
      }))
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

  async function startDiagnostic() {
    try {
      setError(null)
      setIsMonitoring(true)
      setProgress(0)
      setMessage('Iniciando diagnóstico...')
      
      const response = await fetch(`${getApiBase()}/run`, { 
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      })
      
      if (!response.ok) {
        throw new Error('Falha ao iniciar diagnóstico')
      }
      
      setMessage('Diagnóstico em execução...')
    } catch (err: any) {
      setError(`Erro ao iniciar: ${err.message}`)
      setIsMonitoring(false)
    }
  }

  async function downloadReport() {
    try {
      const response = await fetch(`${getApiBase()}/report`)
      if (response.ok) {
        const blob = await response.blob()
        const url = window.URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `ssd-report-${new Date().toISOString()}.json`
        document.body.appendChild(a)
        a.click()
        document.body.removeChild(a)
        window.URL.revokeObjectURL(url)
      } else {
        setError('Relatório ainda não disponível')
      }
    } catch (err: any) {
      setError(`Erro ao baixar relatório: ${err.message}`)
    }
  }

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh', bgcolor: 'background.default' }}>
      <AppBar position="static">
        <Toolbar>
          <Typography variant="h6" sx={{ flexGrow: 1 }}>
            SSD Diagnostic Suite
          </Typography>
          <Button 
            color="inherit" 
            onClick={startDiagnostic}
            disabled={isMonitoring}
            startIcon={isMonitoring ? <StopIcon /> : <StartIcon />}
          >
            {isMonitoring ? 'Executando...' : 'Iniciar Diagnóstico'}
          </Button>
        </Toolbar>
      </AppBar>

      <Container maxWidth="lg" sx={{ py: 4, flex: 1 }}>
        {error && (
          <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
            {error}
          </Alert>
        )}

        <Grid container spacing={3}>
          <Grid item xs={12} md={4}>
            <Paper sx={{ p: 3, mb: 2 }}>
              <Typography variant="h6" gutterBottom>
                Status da Execução
              </Typography>
              <ProgressBar value={progress} label={message} />
            </Paper>

            <Paper sx={{ p: 3 }}>
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
                >
                  Baixar Relatório
                </Button>
              </Box>
            </Paper>
          </Grid>

          <Grid item xs={12} md={8}>
            <Paper sx={{ p: 3, height: 400 }}>
              <Typography variant="h6" gutterBottom>
                📊 Análise em Tempo Real
              </Typography>
              <Box 
                sx={{ 
                  height: 'calc(100% - 48px)', 
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
          </Grid>
        </Grid>
      </Container>
    </Box>
  )
}

export default App

