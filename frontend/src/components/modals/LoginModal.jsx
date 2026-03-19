import { useState } from 'react'
import useAuthStore from '../../store/useAuthStore'
import { Toast } from '../index'

export default function LoginModal() {
  const [form, setForm] = useState({ username: '', password: '' })
  const [showPw, setShowPw] = useState(false)
  const [toast, setToast] = useState(null)
  const [loading, setLoading] = useState(false)

  const { modal, closeModal, switchToRegister, switchToForgot, login } = useAuthStore()

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    const result = await login(form.username, form.password)
    if (!result.success) setToast(result.error)
    setLoading(false)
  }

  if (!modal?.login) return null

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm"
      onClick={(e) => e.target === e.currentTarget && closeModal('login')}
    >
      <div className="bg-[#111] border border-white/10 rounded-2xl p-6 w-full max-w-sm relative">
        <button onClick={() => closeModal('login')} className="absolute top-4 right-4 text-white/30 hover:text-white/60 text-lg">✕</button>

        <h2 className="text-white font-unbounded font-semibold text-xl mb-1 text-center">С возвращением</h2>
        <p className="text-white/40 text-sm font-onest text-center mb-6">Войдите в свой аккаунт</p>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="text-white/60 text-xs mb-1.5 block">Имя пользователя</label>
            <input
              className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white text-sm placeholder-white/20 focus:outline-none focus:border-white/30 transition-colors"
              placeholder="username"
              value={form.username}
              onChange={(e) => setForm({ ...form, username: e.target.value })}
              autoComplete="username"
              required
            />
          </div>
          <div>
            <label className="text-white/60 text-xs mb-1.5 block">Пароль</label>
            <div className="relative">
              <input
                className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white text-sm placeholder-white/20 focus:outline-none focus:border-white/30 transition-colors pr-11"
                type={showPw ? 'text' : 'password'}
                placeholder="••••••••"
                value={form.password}
                onChange={(e) => setForm({ ...form, password: e.target.value })}
                autoComplete="current-password"
                required
              />
              <button type="button" onClick={() => setShowPw(!showPw)} className="absolute right-3 top-1/2 -translate-y-1/2 text-white/30 hover:text-white/60 text-base">
                {showPw ? '🙈' : '👁'}
              </button>
            </div>
          </div>
          <button type="submit" disabled={loading} className="w-full bg-white text-black font-medium py-3 rounded-xl hover:bg-white/90 transition-all disabled:opacity-50">
            {loading ? 'Входим...' : 'Войти'}
          </button>
        </form>

        <div className="flex flex-col items-center gap-2 mt-4">
          <button onClick={switchToForgot} className="text-white/30 hover:text-white/50 text-xs transition-colors">Забыли пароль?</button>
          <button onClick={switchToRegister} className="text-white/60 hover:text-white text-sm font-onest transition-colors">Нет аккаунта? Зарегистрироваться</button>
        </div>
      </div>
      {toast && <Toast message={toast} onClose={() => setToast(null)} />}
    </div>
  )
}