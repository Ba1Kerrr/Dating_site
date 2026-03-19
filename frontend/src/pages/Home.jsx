import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { getFeed } from '../api'
import useAuthStore from '../store/useAuthStore'
import Navbar from '../components/Navbar'

const API = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export default function Home() {
  const { user } = useAuthStore()
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
    <div className="min-h-screen bg-[#0a0a0a]">
      <Navbar />
      <main className="pt-20 px-4 max-w-5xl mx-auto">
        {user ? (
          <section className="py-10">
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
                      <div className="text-white font-medium text-sm">
                        {item.name || item.username}
                      </div>
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
          <section className="flex flex-col items-center justify-center min-h-[80vh] text-center">
            <h1 className="font-unbounded text-white text-4xl md:text-6xl font-bold leading-tight mb-6">
              Найди того,<br />
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-pink-400">
                кто тебя поймёт
              </span>
            </h1>
            <p className="text-white/50 font-onest text-lg max-w-md mb-10 leading-relaxed">
              SoulMates — место, где люди находят настоящие чувства. Умный подбор, живое общение, полная приватность.
            </p>
            <div className="flex gap-4 flex-wrap justify-center">
              <Link
                to="/register"
                className="px-8 py-4 bg-white text-black rounded-xl font-medium hover:bg-white/90 transition-all"
              >
                Начать знакомства
              </Link>
              <Link
                to="/login"
                className="px-8 py-4 border border-white/20 text-white rounded-xl hover:border-white/40 transition-all"
              >
                У меня есть аккаунт
              </Link>
            </div>
            <div className="flex gap-8 mt-16 text-white/30 text-sm font-onest">
              <span>🔒 Приватность</span>
              <span>🧠 Умный подбор</span>
              <span>💬 Живое общение</span>
            </div>
          </section>
        )}
      </main>
    </div>
  )
}