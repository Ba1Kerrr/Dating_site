import { useState } from 'react'
import useAuthStore from '../../store/useAuthStore'
import { forgotPassword, forgotUsername } from '../../api'
import { Toast } from '../index'

export default function ForgotModal() {
  const [mode, setMode] = useState('choose') // choose | password | username
  const [form, setForm] = useState({ username: '', email: '', new_password: '' })
  const [toast, setToast] = useState(null)
  const [loading, setLoading] = useState(false)
  
  const { modal, closeModal, switchToLogin } = useAuthStore()

  const handlePasswordReset = async (e) => {
    e.preventDefault()
    setLoading(true)
    try {
      await forgotPassword({ username: form.username, new_password: form.new_password })
      setToast('Пароль изменён')
      setTimeout(() => {
        closeModal('forgot')
        switchToLogin()
      }, 1500)
    } catch (err) {
      setToast(err.response?.data?.detail || 'Ошибка')
    } finally {
      setLoading(false)
    }
  }

  const handleUsernameReset = async (e) => {
    e.preventDefault()
    setLoading(true)
    try {
      await forgotUsername({ email: form.email, new_password: form.new_password })
      setToast('Проверьте email')
      setTimeout(() => {
        closeModal('forgot')
        switchToLogin()
      }, 1500)
    } catch (err) {
      setToast(err.response?.data?.detail || 'Ошибка')
    } finally {
      setLoading(false)
    }
  }

  if (!modal?.forgot) return null

  const inputCls = 'w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white text-sm placeholder-white/20 focus:outline-none focus:border-white/30 transition-colors'

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm"
      onClick={(e) => e.target === e.currentTarget && closeModal('forgot')}
    >
      <div className="bg-[#111] border border-white/10 rounded-2xl p-6 w-full max-w-sm relative animate-in fade-in zoom-in duration-200">
        <button
          onClick={() => closeModal('forgot')}
          className="absolute top-4 right-4 text-white/30 hover:text-white/60 transition-colors text-lg"
        >
          ✕
        </button>
        
        {mode === 'choose' && (
          <>
            <h2 className="text-white font-unbounded font-semibold text-xl mb-6 text-center">
              Восстановление
            </h2>
            <div className="space-y-3">
              <button
                onClick={() => setMode('password')}
                className="w-full p-4 bg-white/5 border border-white/10 rounded-xl text-white hover:border-white/30 transition-all text-left"
              >
                <div className="font-medium mb-1">🔑 Забыли пароль</div>
                <div className="text-white/30 text-xs">Знаю имя, но не помню пароль</div>
              </button>
              <button
                onClick={() => setMode('username')}
                className="w-full p-4 bg-white/5 border border-white/10 rounded-xl text-white hover:border-white/30 transition-all text-left"
              >
                <div className="font-medium mb-1">📧 Забыли имя</div>
                <div className="text-white/30 text-xs">Знаю email, но не помню имя</div>
              </button>
            </div>
          </>
        )}

        {mode === 'password' && (
          <>
            <h2 className="text-white font-unbounded font-semibold text-xl mb-1 text-center">
              Забыли пароль?
            </h2>
            <p className="text-white/40 text-sm font-onest text-center mb-6">
              Введите имя и новый пароль
            </p>
            <form onSubmit={handlePasswordReset} className="space-y-4">
              <input
                className={inputCls}
                placeholder="Имя пользователя"
                value={form.username}
                onChange={(e) => setForm({ ...form, username: e.target.value })}
                required
              />
              <input
                className={inputCls}
                type="password"
                placeholder="Новый пароль"
                value={form.new_password}
                onChange={(e) => setForm({ ...form, new_password: e.target.value })}
                required
              />
              <button
                type="submit"
                disabled={loading}
                className="w-full bg-white text-black font-medium py-3 rounded-xl hover:bg-white/90 transition-all disabled:opacity-50"
              >
                {loading ? '...' : 'Изменить пароль'}
              </button>
            </form>
          </>
        )}

        {mode === 'username' && (
          <>
            <h2 className="text-white font-unbounded font-semibold text-xl mb-1 text-center">
              Забыли имя?
            </h2>
            <p className="text-white/40 text-sm font-onest text-center mb-6">
              Введите email и новый пароль
            </p>
            <form onSubmit={handleUsernameReset} className="space-y-4">
              <input
                className={inputCls}
                type="email"
                placeholder="Email"
                value={form.email}
                onChange={(e) => setForm({ ...form, email: e.target.value })}
                required
              />
              <input
                className={inputCls}
                type="password"
                placeholder="Новый пароль"
                value={form.new_password}
                onChange={(e) => setForm({ ...form, new_password: e.target.value })}
                required
              />
              <button
                type="submit"
                disabled={loading}
                className="w-full bg-white text-black font-medium py-3 rounded-xl hover:bg-white/90 transition-all disabled:opacity-50"
              >
                {loading ? '...' : 'Восстановить'}
              </button>
            </form>
          </>
        )}

        <button
          onClick={switchToLogin}
          className="block text-center text-white/30 hover:text-white/50 text-xs mt-5 w-full"
        >
          ← Ко входу
        </button>
      </div>

      {toast && <Toast message={toast} onClose={() => setToast(null)} />}
    </div>
  )
}