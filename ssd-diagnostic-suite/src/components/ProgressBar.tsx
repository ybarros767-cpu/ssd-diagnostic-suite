import { Box, LinearProgress, Typography } from '@mui/material'

interface ProgressBarProps {
  value: number
  label?: string
}

export function ProgressBar({ value, label }: ProgressBarProps) {
  const clampedValue = Math.min(100, Math.max(0, value))
  return (
    <Box sx={{ width: '100%' }}>
      <Typography variant="body2" sx={{ mb: 0.5 }}>
        {label ?? 'Progresso'}
      </Typography>
      <LinearProgress 
        variant="determinate" 
        value={clampedValue}
        sx={{ height: 10, borderRadius: 5 }}
      />
      <Typography variant="caption" sx={{ mt: 0.5, display: 'block' }}>
        {Math.round(clampedValue)}%
      </Typography>
    </Box>
  )
}

