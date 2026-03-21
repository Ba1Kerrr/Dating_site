import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import useAuthStore from '../../store/useAuthStore'
import { Toast } from '../index'
import { sendEmailCode } from '../../api'

export default function RegisterModal() {
  const navigate = useNavigate()
  const [form, setForm] = useState({
    username: '',
    email: '',
    password: '',
    confirmPassword: '',
  })
  const [codeSent, setCodeSent] = useState(false)
  const [code, setCode] = useState('')
  const [sendingCode, setSendingCode] = useState(false)
  const [agreed, setAgreed] = useState(false)
  const [toast, setToast] = useState(null)
  const [toastType, setToastType] = useState('error')
  const [loading, setLoading] = useState(false)

  const { modal, closeModal, switchToLogin, register } = useAuthStore()

  const showToast = (msg, type = 'error') => {
    setToast(typeof msg === 'string' ? msg : JSON.stringify(msg))
    setToastType(type)
  }

  const handleSendCode = async () => {
    if (!form.email) { showToast('Введите email'); return }
    setSendingCode(true)
    try {
      await sendEmailCode(form.email)
      setCodeSent(true)
      showToast('Код отправлен на почту', 'success')
    } catch (err) {
      showToast(err.response?.data?.detail || 'Ошибка отправки кода')
    } finally {
      setSendingCode(false)
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!agreed) {
      showToast('Необходимо принять условия соглашения')
      return
    }
    if (form.password !== form.confirmPassword) {
      showToast('Пароли не совпадают')
      return
    }
    if (!code) {
      showToast('Введите код из письма')
      return
    }
    setLoading(true)
    const result = await register({
      username:        form.username,
      email:           form.email,
      password:        form.password,
      confirmPassword: form.confirmPassword,
      email_code:      code,
    })
    if (result.success) {
      if (result.redirect) navigate(result.redirect)
    } else {
      showToast(result.error || 'Ошибка регистрации')
    }
    setLoading(false)
  }

  // Открыть документ в новой вкладке не закрывая модалку
  const openDoc = (path) => (e) => {
    e.preventDefault()
    window.open(path, '_blank', 'noopener,noreferrer')
  }

  if (!modal?.register) return null

  const inputCls =
    'w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white text-sm ' +
    'placeholder-white/20 focus:outline-none focus:border-white/30 transition-colors'

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm"
      onClick={(e) => e.target === e.currentTarget && closeModal('register')}
    >
      <div className="bg-[#111] border border-white/10 rounded-2xl p-6 w-full max-w-sm relative animate-in fade-in zoom-in duration-200 max-h-[90vh] overflow-y-auto">
        <button
          onClick={() => closeModal('register')}
          className="absolute top-4 right-4 text-white/30 hover:text-white/60 transition-colors text-lg z-10"
        >✕</button>

        <h2 className="text-white font-unbounded font-semibold text-xl mb-1 text-center">
          Регистрация
        </h2>
        <p className="text-white/40 text-sm font-onest text-center mb-6">
          Создайте аккаунт
        </p>

        <form onSubmit={handleSubmit} className="space-y-4">

          {/* Username */}
          <div>
            <label className="text-white/60 text-xs mb-1.5 block">Имя пользователя</label>
            <input
              className={inputCls}
              placeholder="username"
              value={form.username}
              onChange={(e) => setForm({ ...form, username: e.target.value })}
              autoComplete="username"
              required
            />
          </div>

          {/* Email + код */}
          <div>
            <label className="text-white/60 text-xs mb-1.5 block">Email</label>
            <div className="flex gap-2">
              <input
                className={inputCls + ' flex-1'}
                type="email"
                placeholder="you@example.com"
                value={form.email}
                onChange={(e) => setForm({ ...form, email: e.target.value })}
                autoComplete="email"
                required
              />
              <button
                type="button"
                onClick={handleSendCode}
                disabled={sendingCode}
                className="px-3 bg-white/5 border border-white/10 rounded-xl text-white/60 hover:text-white hover:border-white/30 text-sm transition-colors disabled:opacity-50 whitespace-nowrap"
              >
                {sendingCode ? '...' : codeSent ? '↺' : 'Код'}
              </button>
            </div>
          </div>

          {/* Код подтверждения */}
          {codeSent && (
            <div>
              <label className="text-white/60 text-xs mb-1.5 block">Код подтверждения</label>
              <input
                className={inputCls}
                placeholder="Введите код из письма"
                value={code}
                onChange={(e) => setCode(e.target.value)}
                required
              />
            </div>
          )}

          {/* Пароль */}
          <div>
            <label className="text-white/60 text-xs mb-1.5 block">Пароль</label>
            <input
              className={inputCls}
              type="password"
              placeholder="••••••••"
              value={form.password}
              onChange={(e) => setForm({ ...form, password: e.target.value })}
              autoComplete="new-password"
              required
            />
          </div>

          {/* Подтверждение пароля */}
          <div>
            <label className="text-white/60 text-xs mb-1.5 block">Подтверждение пароля</label>
            <input
              className={inputCls}
              type="password"
              placeholder="••••••••"
              value={form.confirmPassword}
              onChange={(e) => setForm({ ...form, confirmPassword: e.target.value })}
              autoComplete="new-password"
              required
            />
          </div>

          {/* Согласие с документами */}
          <div
            onClick={() => setAgreed(!agreed)}
            className={`flex items-start gap-3 p-3.5 rounded-xl border cursor-pointer transition-all select-none
              ${agreed
                ? 'border-purple-500/40 bg-purple-500/5'
                : 'border-white/10 bg-white/[0.02] hover:border-white/20'
              }`}
          >
            {/* Кастомный чекбокс */}
            <div className={`w-4 h-4 rounded shrink-0 mt-0.5 border transition-all flex items-center justify-center
              ${agreed
                ? 'bg-purple-500 border-purple-500'
                : 'border-white/30 bg-transparent'
              }`}
            >
              {agreed && (
                <svg width="10" height="8" viewBox="0 0 10 8" fill="none">
                  <path d="M1 4L3.5 6.5L9 1" stroke="white" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
              )}
            </div>
            <p className="text-white/40 text-xs leading-relaxed">
              Я прочитал(а) и принимаю{' '}
              <button
                type="button"
                onClick={openDoc('/terms')}
                className="text-purple-400 hover:text-purple-300 underline underline-offset-2 transition-colors"
              >
                Пользовательское соглашение
              </button>
              {' '}и{' '}
              <button
                type="button"
                onClick={openDoc('/privacy')}
                className="text-purple-400 hover:text-purple-300 underline underline-offset-2 transition-colors"
              >
                Политику конфиденциальности
              </button>
              , а также даю согласие на обработку моих персональных данных в соответствии с 152-ФЗ
            </p>
          </div>

          <button
            type="submit"
            disabled={loading || !agreed}
            className="w-full bg-white text-black font-medium py-3 rounded-xl hover:bg-white/90 transition-all disabled:opacity-40 disabled:cursor-not-allowed"
          >
            {loading ? 'Создаём...' : 'Создать аккаунт'}
          </button>
        </form>

        <button
          onClick={switchToLogin}
          className="block text-center text-white/40 hover:text-white/70 text-sm mt-5 font-onest w-full transition-colors"
        >
          Уже есть аккаунт? Войти
        </button>
      </div>

      {toast && <Toast message={toast} type={toastType} onClose={() => setToast(null)} />}
    </div>
  )
}