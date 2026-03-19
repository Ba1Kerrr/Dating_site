import { Navigate } from 'react-router-dom'
import useAuthStore from '../store/useAuthStore'

export function PrivateRoute({ children }) {
  const { user } = useAuthStore()
  if (!user) return <Navigate to="/login" replace />
  return children
}


import { useState, useEffect } from 'react'

export function Toast({ message, type = 'error', onClose }) {
  useEffect(() => {
    const t = setTimeout(onClose, 3500)
    return () => clearTimeout(t)
  }, [onClose])

  const colors = {
    error: 'bg-red-500/20 border-red-500/40 text-red-300',
    success: 'bg-green-500/20 border-green-500/40 text-green-300',
    info: 'bg-purple-500/20 border-purple-500/40 text-purple-300',
  }

  return (
    <div className={`fixed bottom-6 right-6 z-50 px-5 py-3 rounded-xl border text-sm backdrop-blur ${colors[type]}`}>
      {message}
    </div>
  )
}