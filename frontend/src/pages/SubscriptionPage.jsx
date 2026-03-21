import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import Navbar from '../components/Navbar'
import Footer from '../components/Footer'
import { Toast } from '../components'
import { getSubscription, activatePromo, getProfileViewers } from '../api'
import useAuthStore from '../store/useAuthStore'

const API = import.meta.env.VITE_API_URL || 'http://localhost:8000'

// ── Компоненты ───────────────────────────────────────────────────────

function PlanBadge({ plan }) {
  if (plan === 'premium') {
    return (
      <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-gradient-to-r from-amber-500/20 to-yellow-500/20 border border-amber-500/30 text-amber-400 text-xs font-medium">
        <span>✦</span> Premium
      </span>
    )
  }
  return (
    <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-white/5 border border-white/10 text-white/40 text-xs">
      Free
    </span>
  )
}

function FeatureRow({ icon, title, desc, premium = false, active = false }) {
  return (
    <div className={`flex items-start gap-4 p-4 rounded-xl border transition-all ${
      active
        ? 'bg-amber-500/5 border-amber-500/20'
        : 'bg-white/[0.02] border-white/8'
    }`}>
      <div className={`w-9 h-9 rounded-lg flex items-center justify-center text-lg shrink-0 ${
        active ? 'bg-amber-500/15' : 'bg-white/5'
      }`}>
        {icon}
      </div>
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2 mb-0.5">
          <span className={`text-sm font-medium ${active ? 'text-white' : 'text-white/60'}`}>
            {title}
          </span>
          {premium && (
            <span className="text-[10px] px-1.5 py-0.5 rounded bg-amber-500/20 text-amber-400 font-medium">
              Premium
            </span>
          )}
        </div>
        <p className="text-white/30 text-xs leading-relaxed">{desc}</p>
      </div>
      <div className="shrink-0 mt-0.5">
        {active
          ? <span className="text-amber-400 text-sm">✓</span>
          : <span className="text-white/15 text-sm">✗</span>
        }
      </div>
    </div>
  )
}

function ViewerCard({ viewer }) {
  const avatarUrl = viewer.avatar ? `${API}/static/${viewer.avatar}` : null
  return (
    <Link
      to={`/users/${viewer.username}`}
      className="flex items-center gap-3 p-3 rounded-xl bg-white/[0.02] border border-white/8 hover:border-white/15 transition-all"
    >
      <div className="w-10 h-10 rounded-full overflow-hidden bg-purple-500/20 border border-purple-500/20 flex items-center justify-center text-purple-300 font-semibold text-sm shrink-0">
        {avatarUrl
          ? <img src={avatarUrl} alt={viewer.username} className="w-full h-full object-cover" />
          : viewer.username?.[0]?.toUpperCase()
        }
      </div>
      <div className="flex-1 min-w-0">
        <div className="text-white/80 text-sm font-medium truncate">
          {viewer.name || viewer.username}
        </div>
        <div className="text-white/25 text-xs">@{viewer.username}</div>
      </div>
      <div className="text-white/20 text-xs shrink-0">
        {viewer.viewed_at
          ? new Date(viewer.viewed_at).toLocaleDateString('ru', { day: 'numeric', month: 'short' })
          : ''
        }
      </div>
    </Link>
  )
}

// ── Главная страница ──────────────────────────────────────────────────

export default function SubscriptionPage() {
  const { user } = useAuthStore()
  const [sub, setSub]         = useState(null)
  const [viewers, setViewers] = useState([])
  const [promo, setPromo]     = useState('')
  const [loading, setLoading] = useState(false)
  const [loadingSub, setLoadingSub] = useState(true)
  const [toast, setToast]     = useState(null)
  const [toastType, setToastType] = useState('error')

  const showToast = (msg, type = 'error') => { setToast(msg); setToastType(type) }

  useEffect(() => {
    getSubscription()
      .then((r) => setSub(r.data))
      .catch(() => setSub({ plan: 'free', is_premium: false }))
      .finally(() => setLoadingSub(false))
  }, [])

  useEffect(() => {
    if (sub?.is_premium) {
      getProfileViewers(20)
        .then((r) => setViewers(r.data.viewers || []))
        .catch(() => setViewers([]))
    }
  }, [sub])

  const handleActivate = async () => {
    if (!promo.trim()) { showToast('Введите промокод'); return }
    setLoading(true)
    try {
      await activatePromo(promo.trim())
      const r = await getSubscription()
      setSub(r.data)
      setPromo('')
      showToast('Premium активирован! 🎉', 'success')
      // Загружаем просмотры
      getProfileViewers(20).then((r) => setViewers(r.data.viewers || []))
    } catch (err) {
      const detail = err.response?.data?.detail
      const msg = typeof detail === 'string' ? detail : detail?.message || 'Неверный промокод'
      showToast(msg)
    } finally {
      setLoading(false)
    }
  }

  const isPremium = sub?.is_premium || sub?.plan === 'premium'

  const features = [
    {
      icon: '🔍',
      title: 'Расширенные фильтры',
      desc: 'Фильтруй по возрасту, полу и городу — находи именно тех, кто тебе нужен',
      premium: true,
      active: isPremium,
    },
    {
      icon: '👁',
      title: 'Кто смотрел профиль',
      desc: 'Видишь кто заходил на твою страницу за последние 30 дней',
      premium: true,
      active: isPremium,
    },
    {
      icon: '⚡',
      title: 'Приоритет в ленте',
      desc: 'Твой профиль чаще показывается другим пользователям в рекомендациях',
      premium: true,
      active: isPremium,
    },
    {
      icon: '💬',
      title: 'Чаты',
      desc: 'Переписка с совместимыми пользователями',
      premium: false,
      active: true,
    },
    {
      icon: '🧠',
      title: 'ML-подбор пар',
      desc: 'Базовые рекомендации на основе алгоритма',
      premium: false,
      active: true,
    },
  ]

  return (
    <div className="min-h-screen bg-[#0a0a0a] flex flex-col">
      <Navbar />

      <main className="flex-1 pt-24 pb-20 px-4">
        <div className="max-w-2xl mx-auto">

          {/* Заголовок */}
          <div className="text-center mb-10">
            <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-amber-500/10 border border-amber-500/20 text-amber-400 text-xs mb-5">
              ✦ Подписки
            </div>
            <h1 className="font-unbounded text-white text-2xl md:text-3xl font-bold mb-3">
              Твой план
            </h1>
            <p className="text-white/35 text-sm font-onest">
              Разблокируй Premium-функции и находи людей быстрее
            </p>
          </div>

          {/* Текущий статус */}
          <div className={`rounded-2xl border p-6 mb-6 transition-all ${
            isPremium
              ? 'bg-gradient-to-br from-amber-500/10 to-yellow-500/5 border-amber-500/25'
              : 'bg-white/[0.02] border-white/8'
          }`}>
            {loadingSub ? (
              <div className="h-16 animate-pulse bg-white/5 rounded-xl" />
            ) : (
              <div className="flex items-center justify-between">
                <div>
                  <div className="text-white/40 text-xs mb-2">Текущий план</div>
                  <div className="flex items-center gap-3">
                    <PlanBadge plan={sub?.plan || 'free'} />
                    <span className="text-white font-unbounded font-semibold text-lg">
                      {isPremium ? 'Premium' : 'Free'}
                    </span>
                  </div>
                  {isPremium && (
                    <p className="text-amber-400/60 text-xs mt-2">
                      Все Premium-функции активны ✓
                    </p>
                  )}
                </div>
                {isPremium && (
                  <div className="text-4xl opacity-40">✦</div>
                )}
              </div>
            )}
          </div>

          {/* Активация промокода (только для free) */}
          {!isPremium && (
            <div className="bg-white/[0.02] border border-white/8 rounded-2xl p-6 mb-6">
              <h2 className="text-white font-medium mb-1">Активировать Premium</h2>
              <p className="text-white/30 text-xs mb-5 font-onest">
                Введите промокод для получения доступа к Premium-функциям на 30 дней
              </p>
              <div className="flex gap-2">
                <input
                  className="flex-1 bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white text-sm placeholder-white/20 focus:outline-none focus:border-amber-500/40 transition-colors font-mono tracking-wider uppercase"
                  placeholder="ПРОМОКОД"
                  value={promo}
                  onChange={(e) => setPromo(e.target.value.toUpperCase())}
                  onKeyDown={(e) => e.key === 'Enter' && handleActivate()}
                />
                <button
                  onClick={handleActivate}
                  disabled={loading}
                  className="px-5 py-3 bg-gradient-to-r from-amber-500 to-yellow-500 text-black text-sm font-semibold rounded-xl hover:opacity-90 transition-all disabled:opacity-40 whitespace-nowrap"
                >
                  {loading ? '...' : 'Активировать'}
                </button>
              </div>
              <p className="text-white/15 text-xs mt-3">
                Тестовый промокод: <span className="text-white/30 font-mono">TESTPREMIUM</span>
              </p>
            </div>
          )}

          {/* Список функций */}
          <div className="mb-6">
            <h2 className="text-white/40 text-xs font-medium uppercase tracking-wider mb-3">
              Что включено
            </h2>
            <div className="space-y-2">
              {features.map((f, i) => (
                <FeatureRow key={i} {...f} />
              ))}
            </div>
          </div>

          {/* Кто смотрел профиль — только Premium */}
          {isPremium && (
            <div className="bg-white/[0.02] border border-white/8 rounded-2xl p-6">
              <div className="flex items-center justify-between mb-4">
                <div>
                  <h2 className="text-white font-medium">Кто смотрел профиль</h2>
                  <p className="text-white/25 text-xs mt-0.5">За последние 30 дней</p>
                </div>
                <span className="text-amber-400/60 text-xs">
                  {viewers.length} чел.
                </span>
              </div>

              {viewers.length > 0 ? (
                <div className="space-y-2">
                  {viewers.map((v, i) => (
                    <ViewerCard key={i} viewer={v} />
                  ))}
                </div>
              ) : (
                <div className="text-center py-8">
                  <div className="text-3xl mb-2 opacity-30">👁</div>
                  <p className="text-white/20 text-sm">
                    Пока никто не смотрел профиль
                  </p>
                </div>
              )}
            </div>
          )}

          {/* Блок для незалогиненных */}
          {!user && (
            <div className="text-center py-12">
              <p className="text-white/40 mb-4">Войдите чтобы управлять подпиской</p>
              <button
                onClick={() => useAuthStore.getState().openModal('login')}
                className="px-6 py-3 bg-white text-black rounded-xl font-medium hover:bg-white/90 transition-all"
              >
                Войти
              </button>
            </div>
          )}

        </div>
      </main>

      <Footer />
      {toast && <Toast message={toast} type={toastType} onClose={() => setToast(null)} />}
    </div>
  )
}