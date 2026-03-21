import { Link } from 'react-router-dom'
import useAuthStore from '../store/useAuthStore'

export default function Footer() {
  const { openModal } = useAuthStore()

  return (
    <footer className="border-t border-white/5 bg-[#0a0a0a]">
      <div className="max-w-6xl mx-auto px-6 py-10">
        <div className="flex flex-col md:flex-row items-start justify-between gap-8">

          {/* Brand */}
          <div className="flex flex-col gap-3">
            <div className="flex items-center gap-2.5">
              <div className="w-6 h-6 rounded-md bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center text-[10px] font-bold text-white">
                S
              </div>
              <span className="font-unbounded text-xs font-semibold text-white tracking-wide">SOULMATES</span>
            </div>
            <p className="text-white/20 text-xs leading-relaxed max-w-[200px]">
              Умный подбор пар на основе ML-алгоритмов
            </p>
            <p className="text-white/15 text-xs">
              ИНН 772467557608 · Самозанятый
            </p>
          </div>

          {/* Links */}
          <div className="flex gap-12 text-xs">
            <div className="flex flex-col gap-2.5">
              <div className="text-white/20 uppercase tracking-widest text-[10px] font-medium mb-1">Навигация</div>
              <Link to="/" className="text-white/35 hover:text-white transition-colors">Главная</Link>
              <Link to="/about" className="text-white/35 hover:text-white transition-colors">О проекте</Link>
              <Link to="/chat" className="text-white/35 hover:text-white transition-colors">Чаты</Link>
            </div>
            <div className="flex flex-col gap-2.5">
              <div className="text-white/20 uppercase tracking-widest text-[10px] font-medium mb-1">Аккаунт</div>
              <button onClick={() => openModal('login')} className="text-white/35 hover:text-white transition-colors text-left">Войти</button>
              <button onClick={() => openModal('register')} className="text-white/35 hover:text-white transition-colors text-left">Регистрация</button>
            </div>
            <div className="flex flex-col gap-2.5">
              <div className="text-white/20 uppercase tracking-widest text-[10px] font-medium mb-1">Документы</div>
              <Link to="/privacy" className="text-white/35 hover:text-white transition-colors">Конфиденциальность</Link>
              <Link to="/terms" className="text-white/35 hover:text-white transition-colors">Соглашение</Link>
            </div>
          </div>
        </div>

        <div className="border-t border-white/5 mt-8 pt-6 flex flex-col sm:flex-row items-center justify-between gap-3">
          <p className="text-white/15 text-xs">© 2026 SoulMates. Все права защищены.</p>
          <div className="flex items-center gap-1.5 text-white/15 text-xs">
            <span>Сделано с</span>
            <span className="text-pink-500/60">♥</span>
            <span>и FastAPI + React</span>
          </div>
        </div>
      </div>
    </footer>
  )
}