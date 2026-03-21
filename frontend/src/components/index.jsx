import { Navigate } from 'react-router-dom'
import { useState, useEffect, useCallback, createContext, useContext, useRef } from 'react'
import useAuthStore from '../store/useAuthStore'

// ─────────────────────────────────────────────
// PrivateRoute
// ─────────────────────────────────────────────
export function PrivateRoute({ children }) {
  const { user } = useAuthStore()
  if (!user) return <Navigate to="/" replace />
  return children
}

// ─────────────────────────────────────────────
// Toast Context — глобальный стек уведомлений
// ─────────────────────────────────────────────
const ToastContext = createContext(null)

const ICONS = {
  error:   '✕',
  success: '✓',
  info:    'i',
  warning: '!',
}

const STYLES = {
  error:   'border-red-500/40   bg-red-500/10   text-red-300',
  success: 'border-green-500/40 bg-green-500/10 text-green-300',
  info:    'border-purple-500/40 bg-purple-500/10 text-purple-300',
  warning: 'border-yellow-500/40 bg-yellow-500/10 text-yellow-300',
}

const ICON_STYLES = {
  error:   'bg-red-500/20   text-red-400',
  success: 'bg-green-500/20 text-green-400',
  info:    'bg-purple-500/20 text-purple-400',
  warning: 'bg-yellow-500/20 text-yellow-400',
}

let _uid = 0

export function ToastProvider({ children }) {
  const [toasts, setToasts] = useState([])

  const push = useCallback((message, type = 'error', duration = 4000) => {
    const id = ++_uid
    setToasts((prev) => [...prev.slice(-4), { id, message, type, duration, visible: true }])
    setTimeout(() => {
      setToasts((prev) => prev.map((t) => t.id === id ? { ...t, visible: false } : t))
      setTimeout(() => setToasts((prev) => prev.filter((t) => t.id !== id)), 350)
    }, duration)
    return id
  }, [])

  const dismiss = useCallback((id) => {
    setToasts((prev) => prev.map((t) => t.id === id ? { ...t, visible: false } : t))
    setTimeout(() => setToasts((prev) => prev.filter((t) => t.id !== id)), 350)
  }, [])

  return (
    <ToastContext.Provider value={push}>
      {children}
      <div className="fixed bottom-6 right-6 z-[100] flex flex-col gap-2 items-end pointer-events-none">
        {toasts.map((t) => (
          <div
            key={t.id}
            className={`
              pointer-events-auto flex items-start gap-3 px-4 py-3 rounded-xl border
              backdrop-blur-sm text-sm max-w-xs shadow-xl
              transition-all duration-300
              ${STYLES[t.type]}
              ${t.visible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-2'}
            `}
          >
            <div className={`w-5 h-5 rounded-full flex items-center justify-center text-xs font-bold shrink-0 mt-0.5 ${ICON_STYLES[t.type]}`}>
              {ICONS[t.type]}
            </div>
            <span className="leading-snug flex-1">{t.message}</span>
            <button
              onClick={() => dismiss(t.id)}
              className="text-white/20 hover:text-white/50 transition-colors text-xs ml-1 shrink-0 mt-0.5"
            >
              ✕
            </button>
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  )
}

export function useToast() {
  const ctx = useContext(ToastContext)
  if (!ctx) throw new Error('useToast must be used inside <ToastProvider>')
  return ctx
}

// ─────────────────────────────────────────────
// Старый Toast для обратной совместимости
// (используется в компонентах которые не переписаны)
// ─────────────────────────────────────────────
export function Toast({ message, type = 'error', onClose }) {
  const timerRef = useRef(null)

  useEffect(() => {
    timerRef.current = setTimeout(onClose, 3500)
    return () => clearTimeout(timerRef.current)
  }, [onClose])

  return (
    <div className={`
      fixed bottom-6 right-6 z-[101] flex items-start gap-3 px-4 py-3
      rounded-xl border backdrop-blur-sm text-sm max-w-xs shadow-xl
      ${STYLES[type]}
    `}>
      <div className={`w-5 h-5 rounded-full flex items-center justify-center text-xs font-bold shrink-0 mt-0.5 ${ICON_STYLES[type]}`}>
        {ICONS[type]}
      </div>
      <span className="leading-snug flex-1">{message}</span>
      <button onClick={onClose} className="text-white/20 hover:text-white/50 transition-colors text-xs ml-1 shrink-0 mt-0.5">✕</button>
    </div>
  )
}