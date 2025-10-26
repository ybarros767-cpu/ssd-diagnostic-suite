import { io, Socket } from 'socket.io-client'

const API_HOST = (import.meta.env.VITE_API_BASE_URL || `http://${window.location.hostname}:8000`)
let socket: Socket | null = null

export function connectSocket() {
  if (socket) return socket
  socket = io(API_HOST, { 
    transports: ['websocket', 'polling'], 
    path: '/socket.io',
    autoConnect: true,
    reconnection: true,
    reconnectionDelay: 1000,
    reconnectionAttempts: Infinity,
  })
  return socket
}

export function disconnectSocket() {
  if (socket) {
    socket.disconnect()
    socket = null
  }
}

export function getApiBase() {
  return API_HOST
}

