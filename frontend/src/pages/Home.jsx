import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { getFeed } from '../api'
import useAuthStore from '../store/useAuthStore'
import Navbar from '../components/Navbar'
import Footer from '../components/Footer'

const API = import.meta.env.VITE_API_URL || 'http://localhost:8000'

// Декоративный паттерн — плавающие круги для hero
function HeroOrbs() {
  return (
    <div className="absolute inset-0 overflow-hidden pointer-events-none">
      {/* Большой фиолетовый орб слева */}
      <div className="absolute -top-32 -left-32 w-[500px] h-[500px] rounded-full bg-purple-600/10 blur-[100px]" />
      {/* Розовый орб справа */}
      <div className="absolute top-0 -right-20 w-[350px] h-[350px] rounded-full bg-pink-600/10 blur-[100px]" />
      {/* Маленький яркий акцент */}
      <div className="absolute top-1/3 left-1/2 -translate-x-1/2 w-[200px] h-[200px] rounded-full bg-purple-500/8 blur-[60px]" />
    </div>
  )
}

// Статистика для Hero
function StatBadge({ value, label }) {
  return (
    <div className="flex flex-col items-center">
      <span className="text-white font-unbounded font-bold text-xl">{value}</span>
      <span className="text-white/30 text-xs mt-0.5">{label}</span>
    </div>
  )
}

export default function Home() {
  const { user, openModal } = useAuthStore()
  const [data, setData] = useState([])
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (!user) return
    setLoading(true)
    getFeed()
      .then((r) => setData(r.data.users || []))
      .catch(() => setData([]))
      .finally(() => setLoading(false))
  }, [user])

  return (
    <div className="min-h-screen bg-[#0a0a0a] flex flex-col">
      <Navbar />

      <main className="flex-1">
        {user ? (
          /* ── Лента для залогиненных ── */
          <section className="pt-24 pb-16 px-4 max-w-5xl mx-auto">
            <h2 className="font-unbounded text-white text-2xl font-semibold mb-2">
              Рекомендации для вас
            </h2>
            <p className="text-white/40 text-sm font-onest mb-8">
              Подобрали специально для тебя
            </p>

            {loading ? (
              <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4">
                {[...Array(8)].map((_, i) => (
                  <div key={i} className="aspect-[3/4] bg-white/5 rounded-2xl animate-pulse" />
                ))}
              </div>
            ) : data.length > 0 ? (
              <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4">
                {data.map((item) => (
                  <Link
                    key={item.username}
                    to={`/users/${item.username}`}
                    className="group relative aspect-[3/4] rounded-2xl overflow-hidden bg-white/5 border border-white/10 hover:border-white/20 transition-all"
                  >
                    {item.avatar ? (
                      <img
                        src={`${API}/static/${item.avatar}`}
                        alt={item.name || item.username}
                        className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                        loading="lazy"
                        onError={(e) => { e.target.style.display = 'none' }}
                      />
                    ) : (
                      <div className="w-full h-full flex items-center justify-center text-4xl text-white/20">
                        {(item.name || item.username)[0].toUpperCase()}
                      </div>
                    )}
                    <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/10 to-transparent" />
                    <div className="absolute bottom-0 left-0 right-0 p-4">
                      <div className="text-white font-medium text-sm">{item.name || item.username}</div>
                      <div className="text-white/50 text-xs mt-0.5 flex gap-2">
                        {item.age && <span>{item.age} лет</span>}
                        {item.location && <span>{item.location}</span>}
                      </div>
                    </div>
                  </Link>
                ))}
              </div>
            ) : (
              <div className="text-center py-20">
                <div className="text-5xl mb-4">🔍</div>
                <p className="text-white/40 font-onest mb-6">
                  Пока нет подходящих анкет.<br />Заполните профиль — и мы подберём пару.
                </p>
                <Link
                  to={`/profile/${user.username}`}
                  className="inline-block px-6 py-3 bg-white text-black rounded-xl font-medium hover:bg-white/90 transition-all"
                >
                  Заполнить профиль
                </Link>
              </div>
            )}
          </section>
        ) : (
          /* ── Hero для незалогиненных ── */
          <section className="relative min-h-[100dvh] flex flex-col items-center justify-center px-4 text-center overflow-hidden">
            <HeroOrbs />

            {/* Бейдж сверху */}
            <div className="relative mb-8 inline-flex items-center gap-2 px-4 py-2 rounded-full bg-white/5 border border-white/10 text-white/50 text-xs">
              <span className="w-1.5 h-1.5 rounded-full bg-green-400 animate-pulse" />
              ML-алгоритм подбора пар в реальном времени
            </div>

            {/* Заголовок */}
            <h1 className="relative font-unbounded font-bold text-white leading-[1.05] tracking-tight mb-6"
              style={{ fontSize: 'clamp(2.5rem, 8vw, 5.5rem)' }}
            >
              Найди того,
              <br />
              <span className="bg-gradient-to-r from-purple-400 via-pink-400 to-purple-400 bg-clip-text text-transparent">
                кто тебя поймёт
              </span>
            </h1>

            {/* Подзаголовок */}
            <p className="relative text-white/40 font-onest text-base md:text-lg max-w-lg mb-10 leading-relaxed">
              Умный подбор на основе интересов и поведения.
              Живые чаты, настоящие знакомства.
            </p>

            {/* CTA кнопки */}
            <div className="relative flex gap-3 flex-wrap justify-center mb-16">
              <button
                onClick={() => openModal('register')}
                className="px-7 py-3.5 bg-white text-black text-sm font-semibold rounded-full hover:bg-white/90 transition-all shadow-xl shadow-white/10 hover:shadow-white/20 hover:scale-[1.02] active:scale-[0.98]"
              >
                Начать знакомства →
              </button>
              <button
                onClick={() => openModal('login')}
                className="px-7 py-3.5 border border-white/15 text-white/70 text-sm rounded-full hover:border-white/30 hover:text-white transition-all"
              >
                Войти в аккаунт
              </button>
            </div>

            {/* Статистика */}
            <div className="relative flex items-center gap-8 md:gap-12">
              <StatBadge value="10K+" label="пользователей" />
              <div className="w-px h-8 bg-white/10" />
              <StatBadge value="82%" label="точность подбора" />
              <div className="w-px h-8 bg-white/10" />
              <StatBadge value="∞" label="бесплатно" />
            </div>

            {/* Нижний индикатор скролла */}
            <div className="absolute bottom-8 left-1/2 -translate-x-1/2 flex flex-col items-center gap-2 text-white/15">
              <span className="text-xs">прокрутите вниз</span>
              <div className="w-px h-8 bg-gradient-to-b from-white/20 to-transparent" />
            </div>
          </section>
        )}

        {/* ── Фича-секция (видна всем) ── */}
        {!user && (
          <section className="px-4 pb-24 max-w-5xl mx-auto">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {[
                { icon: '🧠', title: 'Умный подбор', text: 'Random Forest анализирует интересы, возраст, активность и предлагает совместимых людей' },
                { icon: '💬', title: 'Живые чаты', text: 'WebSocket-соединение — пишите без задержек, видите статус собеседника' },
                { icon: '🔒', title: 'Приватность', text: 'JWT-авторизация, bcrypt-хеширование, rate limiting — данные под защитой' },
              ].map((f, i) => (
                <div key={i} className="bg-white/[0.03] border border-white/8 rounded-2xl p-6 hover:bg-white/5 hover:border-white/15 transition-all">
                  <div className="text-2xl mb-4">{f.icon}</div>
                  <div className="text-white font-medium text-sm mb-2">{f.title}</div>
                  <div className="text-white/35 text-xs leading-relaxed">{f.text}</div>
                </div>
              ))}
            </div>
          </section>
        )}
      </main>

      <Footer />
    </div>
  )
}