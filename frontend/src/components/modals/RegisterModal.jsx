import { useState } from 'react'
import useAuthStore from '../../store/useAuthStore'
import { Toast } from '../index'
import { sendEmailCode } from '../../api'

export default function RegisterModal() {
  const [form, setForm] = useState({
    username: '',
    email: '',
    password: '',
    confirmPassword: ''
  })
  const [codeSent, setCodeSent] = useState(false)
  const [code, setCode] = useState('')
  const [sendingCode, setSendingCode] = useState(false)
  const [toast, setToast] = useState(null)
  const [loading, setLoading] = useState(false)
  
  const { modal, closeModal, switchToLogin, register } = useAuthStore()

  const handleSendCode = async () => {
    if (!form.email) {
      setToast('Введите email')
      return
    }
    setSendingCode(true)
    try {
      await sendEmailCode(form.email)
      setCodeSent(true)
      setToast('Код отправлен')
    } catch (err) {
      setToast(err.response?.data?.detail || 'Ошибка отправки')
    } finally {
      setSendingCode(false)
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (form.password !== form.confirmPassword) {
      setToast('Пароли не совпадают')
      return
    }
    setLoading(true)
    const result = await register({
      ...form,
      email_code: code
    })
    if (!result.success) {
      setToast(result.error)
    }
    setLoading(false)
  }

  if (!modal?.register) return null

  const inputCls = 'w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white text-sm placeholder-white/20 focus:outline-none focus:border-white/30 transition-colors'

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm"
      onClick={(e) => e.target === e.currentTarget && closeModal('register')}
    >
      <div className="bg-[#111] border border-white/10 rounded-2xl p-6 w-full max-w-sm relative animate-in fade-in zoom-in duration-200 max-h-[90vh] overflow-y-auto">
        <button
          onClick={() => closeModal('register')}
          className="absolute top-4 right-4 text-white/30 hover:text-white/60 transition-colors text-lg z-10"
        >
          ✕
        </button>
        
        <h2 className="text-white font-unbounded font-semibold text-xl mb-1 text-center">
          Регистрация
        </h2>
        <p className="text-white/40 text-sm font-onest text-center mb-6">
          Создайте аккаунт
        </p>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="text-white/60 text-xs mb-1.5 block">Имя пользователя</label>
            <input
              className={inputCls}
              placeholder="username"
              value={form.username}
              onChange={(e) => setForm({ ...form, username: e.target.value })}
              required
            />
          </div>

          <div>
            <label className="text-white/60 text-xs mb-1.5 block">Email</label>
            <div className="flex gap-2">
              <input
                className={inputCls + ' flex-1'}
                type="email"
                placeholder="you@example.com"
                value={form.email}
                onChange={(e) => setForm({ ...form, email: e.target.value })}
                required
                disabled={codeSent}
              />
              <button
                type="button"
                onClick={handleSendCode}
                disabled={codeSent || sendingCode}
                className="px-3 bg-white/5 border border-white/10 rounded-xl text-white/60 hover:text-white hover:border-white/30 text-sm transition-colors disabled:opacity-50"
              >
                {sendingCode ? '...' : codeSent ? '✓' : 'Код'}
              </button>
            </div>
          </div>

          {codeSent && (
            <div>
              <label className="text-white/60 text-xs mb-1.5 block">Код подтверждения</label>
              <input
                className={inputCls}
                placeholder="Введите код"
                value={code}
                onChange={(e) => setCode(e.target.value)}
                required
              />
            </div>
          )}

          <div>
            <label className="text-white/60 text-xs mb-1.5 block">Пароль</label>
            <input
              className={inputCls}
              type="password"
              placeholder="••••••••"
              value={form.password}
              onChange={(e) => setForm({ ...form, password: e.target.value })}
              required
            />
          </div>

          <div>
            <label className="text-white/60 text-xs mb-1.5 block">Подтверждение</label>
            <input
              className={inputCls}
              type="password"
              placeholder="••••••••"
              value={form.confirmPassword}
              onChange={(e) => setForm({ ...form, confirmPassword: e.target.value })}
              required
            />
          </div>

          <button
            type="submit"
            disabled={loading || (codeSent && !code)}
            className="w-full bg-white text-black font-medium py-3 rounded-xl hover:bg-white/90 transition-all disabled:opacity-50"
          >
            {loading ? 'Создаём...' : 'Создать аккаунт'}
          </button>
        </form>

        <button
          onClick={switchToLogin}
          className="block text-center text-white/60 hover:text-white text-sm mt-5 font-onest w-full"
        >
          Уже есть аккаунт? Войти
        </button>
      </div>

      {toast && <Toast message={toast} onClose={() => setToast(null)} />}
    </div>
  )
}