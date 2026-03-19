import { Link } from 'react-router-dom'
import useAuthStore from '../store/useAuthStore'
import LoginModal from './modals/LoginModal'
import RegisterModal from './modals/RegisterModal'
import ForgotModal from './modals/ForgotModal'

export default function Navbar() {
  const { user, logout, openModal } = useAuthStore()

  return (
    <>
      <nav className="bg-[#16161c] border-b border-[#23232e] sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 h-[60px] flex items-center justify-between gap-4">
          <Link to="/" className="font-unbounded text-sm font-semibold bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent shrink-0">
            SOULMATES
          </Link>

          <div className="flex gap-0.5 overflow-x-auto scrollbar-hide">
            <Link to="/" className="text-gray-500 text-xs px-3 py-1.5 rounded-full hover:text-white hover:bg-[#23232e] transition-colors whitespace-nowrap">
              Главная
            </Link>
            <Link to="/about" className="text-gray-500 text-xs px-3 py-1.5 rounded-full hover:text-white hover:bg-[#23232e] transition-colors whitespace-nowrap">
              О проекте
            </Link>
            {user && (
              <>
                <Link to="/chat" className="text-gray-500 text-xs px-3 py-1.5 rounded-full hover:text-white hover:bg-[#23232e] transition-colors whitespace-nowrap">
                  Чаты
                </Link>
                <Link to={`/users/${user.username}`} className="text-gray-500 text-xs px-3 py-1.5 rounded-full hover:text-white hover:bg-[#23232e] transition-colors whitespace-nowrap">
                  Профиль
                </Link>
              </>
            )}
          </div>

          <div className="flex items-center gap-2 shrink-0">
            {user ? (
              <button
                onClick={logout}
                className="px-3 py-1.5 border border-[#23232e] text-xs rounded-full hover:border-purple-400 hover:text-purple-400 transition-colors"
              >
                Выйти
              </button>
            ) : (
              <>
                <button
                  onClick={() => openModal('login')}
                  className="px-3 py-1.5 text-gray-500 text-xs hover:text-white transition-colors"
                >
                  Войти
                </button>
                <button
                  onClick={() => openModal('register')}
                  className="px-4 py-1.5 bg-gradient-to-r from-purple-400 to-pink-400 text-black text-xs font-semibold rounded-full hover:opacity-90 transition-all"
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