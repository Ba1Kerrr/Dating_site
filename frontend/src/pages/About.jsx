import { Link } from 'react-router-dom'
import useAuthStore from '../store/useAuthStore'
import Navbar from '../components/Navbar'

export default function About() {
  const { user } = useAuthStore()

  const features = [
    { icon: '🧠', title: 'Умный подбор', text: 'ML-алгоритм анализирует предпочтения и предлагает тех, с кем вы действительно совместимы.' },
    { icon: '💬', title: 'Живые чаты', text: 'WebSocket-чаты в реальном времени — пишите без задержек и всегда будьте на связи.' },
    { icon: '🔒', title: 'Приватность', text: 'Ваши данные защищены. JWT-авторизация, шифрование паролей и контроль доступа.' },
    { icon: '⚡', title: 'Быстро', text: 'FastAPI на бэкенде — молниеносные ответы и асинхронная работа без лагов.' },
    { icon: '🌍', title: 'По городам', text: 'Поиск по геолокации — найдите людей рядом с вами или из любого уголка страны.' },
    { icon: '✨', title: 'Бесплатно', text: 'Базовый функционал полностью бесплатный. Создайте профиль и начните прямо сейчас.' },
  ]

  return (
    <div className="min-h-screen bg-[#0a0a0a]">
      <Navbar />

      <div className="pt-24 pb-12 px-4 text-center">
        <div className="mb-3 text-purple-400 text-sm font-medium">✦ О нас</div>
        <h1 className="font-unbounded text-white text-4xl md:text-5xl font-bold leading-tight mb-4">
          Знакомства,<br />
          которые <span className="text-purple-400">работают</span>
        </h1>
        <p className="text-white/50 font-onest text-lg max-w-xl mx-auto mb-4 leading-relaxed">
          SoulMates — это место, где умный алгоритм встречается с человеческой теплотой.
          Мы помогаем людям находить друг друга по-настоящему.
        </p>
        {user && (
          <p className="text-white/40 text-sm">
            Рады видеть тебя, <strong className="text-white">{user.username}</strong> ✨
          </p>
        )}
      </div>

      <div className="max-w-5xl mx-auto px-4 pb-16">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {features.map((f, i) => (
            <div
              key={i}
              className="bg-white/5 border border-white/10 rounded-2xl p-5 hover:border-white/20 transition-all"
              style={{ animationDelay: `${i * 80}ms` }}
            >
              <div className="text-2xl mb-3">{f.icon}</div>
              <div className="text-white font-medium mb-2">{f.title}</div>
              <div className="text-white/40 text-sm leading-relaxed">{f.text}</div>
            </div>
          ))}
        </div>
      </div>

      <div className="max-w-5xl mx-auto px-4 pb-24">
        <div className="bg-white/5 border border-white/10 rounded-2xl p-8 text-center">
          <h2 className="font-unbounded text-white text-2xl font-semibold mb-2">Готовы начать?</h2>
          <p className="text-white/40 text-sm mb-6">Тысячи людей уже нашли свою половинку на SoulMates</p>
          <div className="flex gap-4 justify-center flex-wrap">
            {user ? (
              <>
                <Link
                  to="/"
                  className="px-6 py-3 bg-white text-black rounded-xl font-medium hover:bg-white/90 transition-all"
                >
                  Смотреть анкеты
                </Link>
                <Link
                  to="/chat"
                  className="px-6 py-3 border border-white/20 text-white rounded-xl hover:border-white/40 transition-all"
                >
                  Мои чаты
                </Link>
              </>
            ) : (
              <>
                <button
                  onClick={() => useAuthStore.getState().openModal('register')}
                  className="px-6 py-3 bg-white text-black rounded-xl font-medium hover:bg-white/90 transition-all"
                >
                  Зарегистрироваться
                </button>
                <button
                  onClick={() => useAuthStore.getState().openModal('login')}
                  className="px-6 py-3 border border-white/20 text-white rounded-xl hover:border-white/40 transition-all"
                >
                  Войти
                </button>
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}