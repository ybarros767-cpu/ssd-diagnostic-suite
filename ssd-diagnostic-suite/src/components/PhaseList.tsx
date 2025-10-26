import { List, ListItem, ListItemText, Chip } from '@mui/material'

export interface Phase {
  key: string
  title: string
  status: 'pending' | 'running' | 'done' | 'error'
}

interface PhaseListProps {
  phases: Phase[]
}

const getStatusInfo = (status: Phase['status']) => {
  switch (status) {
    case 'done':
      return { color: 'success' as const, label: 'Concluído' }
    case 'running':
      return { color: 'info' as const, label: 'Executando' }
    case 'error':
      return { color: 'error' as const, label: 'Erro' }
    default:
      return { color: 'default' as const, label: 'Pendente' }
  }
}

export function PhaseList({ phases }: PhaseListProps) {
  return (
    <List dense>
      {phases.map((p) => {
        const { color, label } = getStatusInfo(p.status)
        return (
          <ListItem key={p.key} secondaryAction={<Chip size="small" color={color} label={label} />}>
            <ListItemText primary={p.title} />
          </ListItem>
        )
      })}
    </List>
  )
}

