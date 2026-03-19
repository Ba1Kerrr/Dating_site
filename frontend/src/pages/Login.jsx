import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { login } from '../api'
import useAuthStore from '../store/useAuthStore'
import { Toast } from '../components'

export default function Login() {
  const [form, setForm] = useState({ username: '', password: '' })
  const [showPw, setShowPw] = useState(false)
  const [toast, setToast] = useState(null)
  const [loading, setLoading] = useState(false)
  const { fetchMe } = useAuthStore()
  const navigate = useNavigate()

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    try {
      await login(form.username, form.password)
      await fetchMe()
      navigate('/')
    } catch (err) {
      setToast(err.response?.data?.detail || 'Неверный логин или пароль')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-[#0a0a0a] flex items-center justify-center px-4">
      <div className="w-full max-w-sm">
        <Link to="/" className="block text-center font-unbounded font-bold text-white text-xl tracking-widest mb-10">
          SOULMATES
        </Link>

        <div className="bg-white/5 border border-white/10 rounded-2xl p-8">
          <h1 className="font-unbounded text-white text-xl font-semibold mb-1">С возвращением</h1>
          <p className="text-white/40 text-sm font-onest mb-8">Войдите в свой аккаунт</p>

          <form onSubmit={handleSubmit} className="space-y-5">
            <div>
              <label className="text-white/60 text-xs font-onest mb-1.5 block">Имя пользователя</label>
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
              <label className="text-white/60 text-xs font-onest mb-1.5 block">Пароль</label>
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
                <button
                  type="button"
                  onClick={() => setShowPw(!showPw)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-white/30 hover:text-white/60 transition-colors text-base"
                >
                  {showPw ? '🙈' : '👁'}
                </button>
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-white text-black font-medium py-3 rounded-xl hover:bg-white/90 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? 'Входим...' : 'Войти'}
            </button>
          </form>

          <Link to="/forgot-password" className="block text-center text-white/30 text-xs mt-5 hover:text-white/50 transition-colors">
            Забыли пароль?
          </Link>
        </div>

        <p className="text-center text-white/30 text-sm mt-5 font-onest">
          Нет аккаунта?{' '}
          <Link to="/register" className="text-white/60 hover:text-white transition-colors">
            Зарегистрироваться
          </Link>
        </p>
      </div>

      {toast && <Toast message={toast} onClose={() => setToast(null)} />}
    </div>
  )
}