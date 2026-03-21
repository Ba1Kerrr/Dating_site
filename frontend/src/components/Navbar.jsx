import { Link, useLocation } from 'react-router-dom'
import useAuthStore from '../store/useAuthStore'
import LoginModal from './modals/LoginModal'
import RegisterModal from './modals/RegisterModal'
import ForgotModal from './modals/ForgotModal'

export default function Navbar() {
  const { user, logout, openModal } = useAuthStore()
  const location = useLocation()

  const navCls = (path) =>
    `text-xs px-3 py-1.5 rounded-full transition-all duration-200 whitespace-nowrap ${
      location.pathname === path
        ? 'text-white bg-white/10 font-medium'
        : 'text-white/40 hover:text-white hover:bg-white/5'
    }`

  const isProfileActive =
    location.pathname.startsWith('/users/') || location.pathname.startsWith('/profile/')

  return (
    <>
      <nav className="fixed top-0 left-0 right-0 z-50">
        <div className="absolute inset-0 bg-[#0a0a0a]/80 backdrop-blur-xl border-b border-white/5" />

        <div className="relative max-w-6xl mx-auto px-6 h-[58px] flex items-center justify-between gap-6">

          {/* Logo */}
          <Link to="/" className="flex items-center gap-2.5 shrink-0 group">
            <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center text-xs font-bold text-white shadow-lg shadow-purple-500/25 group-hover:shadow-purple-500/40 transition-shadow">
              S
            </div>
            <span className="font-unbounded text-xs font-semibold text-white tracking-wide">SOULMATES</span>
          </Link>

          {/* Nav */}
          <div className="flex items-center gap-0.5">
            <Link to="/" className={navCls('/')}>Главная</Link>
            <Link to="/about" className={navCls('/about')}>О проекте</Link>
            {user && (
              <>
                <Link to="/chat" className={navCls('/chat')}>Чаты</Link>
                <Link
                  to={`/users/${user.username}`}
                  className={`text-xs px-3 py-1.5 rounded-full transition-all duration-200 whitespace-nowrap ${
                    isProfileActive
                      ? 'text-white bg-white/10 font-medium'
                      : 'text-white/40 hover:text-white hover:bg-white/5'
                  }`}
                >
                  Профиль
                </Link>
                {/* Подписка */}
                <Link
                  to="/subscription"
                  className={`text-xs px-3 py-1.5 rounded-full transition-all duration-200 whitespace-nowrap ${
                    location.pathname === '/subscription'
                      ? 'text-amber-400 bg-amber-500/10 font-medium'
                      : 'text-white/40 hover:text-amber-400 hover:bg-amber-500/5'
                  }`}
                >
                  ✦ Premium
                </Link>
              </>
            )}
          </div>

          {/* Auth */}
          <div className="flex items-center gap-2 shrink-0">
            {user ? (
              <div className="flex items-center gap-3">
                <div className="w-7 h-7 rounded-full bg-purple-500/20 border border-purple-500/30 flex items-center justify-center text-purple-300 text-xs font-semibold">
                  {user.username?.[0]?.toUpperCase()}
                </div>
                <button
                  onClick={logout}
                  className="text-white/30 text-xs hover:text-red-400 transition-colors"
                >
                  Выйти
                </button>
              </div>
            ) : (
              <>
                <button
                  onClick={() => openModal('login')}
                  className="px-4 py-1.5 text-white/50 text-xs hover:text-white transition-colors"
                >
                  Войти
                </button>
                <button
                  onClick={() => openModal('register')}
                  className="px-4 py-2 bg-white text-black text-xs font-semibold rounded-full hover:bg-white/90 transition-all shadow-lg"
                >
                  Регистрация
                </button>
              </>
            )}
          </div>
        </div>
      </nav>

      <LoginModal />
      <RegisterModal />
      <ForgotModal />
    </>
  )
}