import { useEffect, useRef } from 'react'
import Plot from 'react-plotly.js'
import { Box, Paper, Typography, Grid } from '@mui/material'

interface RealtimeGraphsProps {
  metrics: {
    read_speed: number
    write_speed: number
    temperature: number
    iops: number
    timestamp?: Date
  }
}

export function RealtimeGraphs({ metrics }: RealtimeGraphsProps) {
  const tempHistory = useRef<number[]>([])
  const readHistory = useRef<number[]>([])
  const writeHistory = useRef<number[]>([])
  const iopsHistory = useRef<number[]>([])
  const timeHistory = useRef<string[]>([])

  useEffect(() => {
    const now = new Date().toLocaleTimeString()
    
    tempHistory.current.push(metrics.temperature || 0)
    readHistory.current.push(metrics.read_speed || 0)
    writeHistory.current.push(metrics.write_speed || 0)
    iopsHistory.current.push(metrics.iops || 0)
    timeHistory.current.push(now)

    // Manter apenas últimas 50 leituras
    if (tempHistory.current.length > 50) {
      tempHistory.current.shift()
      readHistory.current.shift()
      writeHistory.current.shift()
      iopsHistory.current.shift()
      timeHistory.current.shift()
    }
  }, [metrics])

  const tempData = [{
    x: timeHistory.current,
    y: tempHistory.current,
    type: 'scatter' as const,
    mode: 'lines+markers' as const,
    name: 'Temperatura',
    line: { color: '#ef5350', width: 2 }
  }]

  const throughputData = [
    {
      x: timeHistory.current,
      y: readHistory.current,
      type: 'scatter' as const,
      mode: 'lines+markers' as const,
      name: 'Leitura',
      line: { color: '#42a5f5', width: 2 }
    },
    {
      x: timeHistory.current,
      y: writeHistory.current,
      type: 'scatter' as const,
      mode: 'lines+markers' as const,
      name: 'Escrita',
      line: { color: '#66bb6a', width: 2 }
    }
  ]

  const iopsData = [{
    x: timeHistory.current,
    y: iopsHistory.current,
    type: 'scatter' as const,
    mode: 'lines+markers' as const,
    name: 'IOPS',
    line: { color: '#ffa726', width: 2 }
  }]

  const layout = { autosize: true, height: 300, margin: { l: 50, r: 30, t: 20, b: 50 } }

  return (
    <Box>
      <Grid container spacing={2}>
        {/* Gráfico de Temperatura */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>🌡️ Temperatura em Tempo Real</Typography>
            <Plot
              data={tempData}
              layout={{
                ...layout,
                yaxis: { title: 'Temperatura (°C)', range: [0, 100] }
              }}
              style={{ width: '100%' }}
            />
          </Paper>
        </Grid>

        {/* Gráfico de Throughput */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>⚡ Throughput (Leitura/Escrita)</Typography>
            <Plot
              data={throughputData}
              layout={{
                ...layout,
                yaxis: { title: 'Velocidade (MB/s)' }
              }}
              style={{ width: '100%' }}
            />
          </Paper>
        </Grid>

        {/* Gráfico de IOPS */}
        <Grid item xs={12}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>📈 IOPS em Tempo Real</Typography>
            <Plot
              data={iopsData}
              layout={{
                ...layout,
                height: 250,
                yaxis: { title: 'IOPS' }
              }}
              style={{ width: '100%' }}
            />
          </Paper>
        </Grid>
      </Grid>
    </Box>
  )
}

