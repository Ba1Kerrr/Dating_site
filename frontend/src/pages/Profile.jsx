import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { getProfile, editProfile, getSubscription, blockUser, unblockUser, getMyBlocks } from '../api'
import useAuthStore from '../store/useAuthStore'
import Navbar from '../components/Navbar'
import { Toast } from '../components'
import ReportModal from '../components/modals/ReportModal'

const API = import.meta.env.VITE_API_URL || 'http://localhost:8000'

function PremiumBadge() {
  return (
    <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-gradient-to-r from-amber-500/20 to-yellow-500/20 border border-amber-500/30 text-amber-400 text-[10px] font-medium">
      ✦ Premium
    </span>
  )
}

export default function Profile() {
  const { username } = useParams()
  const { user } = useAuthStore()

  const [profile,      setProfile]      = useState(null)
  const [isOwn,        setIsOwn]        = useState(false)
  const [isPremium,    setIsPremium]    = useState(false)
  const [isBlocked,    setIsBlocked]    = useState(false)
  const [blockLoading, setBlockLoading] = useState(false)
  const [menuOpen,     setMenuOpen]     = useState(false)

  const [editOpen,  setEditOpen]  = useState(false)
  const [editForm,  setEditForm]  = useState({})
  const [editFile,  setEditFile]  = useState(null)
  const [saving,    setSaving]    = useState(false)

  const [reportOpen, setReportOpen] = useState(false)
  const [toast,      setToast]      = useState(null)
  const [toastType,  setToastType]  = useState('error')

  useEffect(() => {
    getProfile(username).then((r) => {
      const data = r.data
      if (data.profile) { setProfile(data.profile); setIsOwn(data.is_own ?? false) }
      else               { setProfile(data);          setIsOwn(data.is_own ?? false) }
    })
  }, [username])

  useEffect(() => {
    if (isOwn) {
      getSubscription()
        .then((r) => setIsPremium(r.data?.is_premium || r.data?.plan === 'premium'))
        .catch(() => setIsPremium(false))
    }
  }, [isOwn])

  // Проверяем заблокирован ли пользователь
  useEffect(() => {
    if (!isOwn && user) {
      getMyBlocks()
        .then((r) => {
          const blocked = (r.data?.blocked || []).some((b) => b.username === username)
          setIsBlocked(blocked)
        })
        .catch(() => setIsBlocked(false))
    }
  }, [username, isOwn, user])

  const handleBlock = async () => {
    setMenuOpen(false)
    setBlockLoading(true)
    try {
      if (isBlocked) {
        await unblockUser(username)
        setIsBlocked(false)
        setToast('Пользователь разблокирован')
        setToastType('info')
      } else {
        await blockUser(username)
        setIsBlocked(true)
        setToast('Пользователь заблокирован')
        setToastType('success')
      }
    } catch (err) {
      setToast(err.response?.data?.detail || 'Ошибка')
      setToastType('error')
    } finally {
      setBlockLoading(false)
    }
  }

  const openEdit = () => {
    setEditForm({
      name: profile?.name || '', bio: profile?.bio || '',
      location: profile?.location || '', age: profile?.age || '',
    })
    setEditOpen(true)
  }

  const handleSave = async (e) => {
    e.preventDefault()
    setSaving(true)
    try {
      await editProfile(username, { ...editForm, file: editFile })
      const r = await getProfile(username)
      setProfile(r.data.profile ?? r.data)
      setEditOpen(false)
      setToast('Профиль обновлён'); setToastType('success')
    } catch (err) {
      setToast(err.response?.data?.detail || 'Ошибка'); setToastType('error')
    } finally {
      setSaving(false)
    }
  }

  if (!profile) {
    return (
      <div className="min-h-screen bg-[#0a0a0a] flex items-center justify-center">
        <div className="w-6 h-6 border-2 border-white/10 border-t-white/40 rounded-full animate-spin" />
      </div>
    )
  }

  const avatarUrl = profile.avatar ? `${API}/static/${profile.avatar}` : null
  const initial   = (profile.name || profile.username || '?')[0].toUpperCase()
  const inputCls  = 'w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white text-sm placeholder-white/20 focus:outline-none focus:border-white/30 transition-colors'

  return (
    <div className="min-h-screen bg-[#0a0a0a]">
      <Navbar />

      <div className="pt-[58px] relative">
        <div className={`h-44 ${isPremium
          ? 'bg-gradient-to-br from-amber-900/30 via-purple-900/20 to-pink-900/20'
          : 'bg-gradient-to-br from-purple-900/30 to-pink-900/15'
        }`} />

        <div className="max-w-3xl mx-auto px-4 pb-8">

          {/* Avatar + name + actions */}
          <div className="flex items-end justify-between -mt-14 mb-6">
            <div className="flex items-end gap-4">
              <div className={`w-24 h-24 rounded-2xl border-4 border-[#0a0a0a] overflow-hidden flex items-center justify-center text-2xl font-bold shrink-0 ${
                isPremium
                  ? 'bg-gradient-to-br from-amber-500/20 to-yellow-500/10 text-amber-300 ring-2 ring-amber-500/20'
                  : 'bg-purple-500/20 text-purple-300'
              }`}>
                {avatarUrl
                  ? <img src={avatarUrl} alt={profile.name} className="w-full h-full object-cover" />
                  : initial}
              </div>
              <div className="pb-1">
                <div className="flex items-center gap-2 mb-0.5 flex-wrap">
                  <span className="text-white font-unbounded font-semibold text-lg leading-tight">
                    {profile.name || profile.username}
                  </span>
                  {isPremium && <PremiumBadge />}
                  {isBlocked && (
                    <span className="px-2 py-0.5 rounded-full bg-red-500/10 border border-red-500/20 text-red-400 text-[10px]">
                      заблокирован
                    </span>
                  )}
                </div>
                <div className="text-white/30 text-sm">@{profile.username}</div>
              </div>
            </div>

            <div className="pb-1 flex items-center gap-2">
              {isOwn ? (
                <>
                  <button
                    onClick={openEdit}
                    className="px-4 py-2 border border-white/15 rounded-xl text-white/60 hover:text-white hover:border-white/30 text-sm transition-all"
                  >
                    ✏ Редактировать
                  </button>
                  <Link
                    to="/subscription"
                    className={`px-4 py-2 rounded-xl text-xs font-medium transition-all ${
                      isPremium
                        ? 'bg-amber-500/10 border border-amber-500/20 text-amber-400 hover:bg-amber-500/15'
                        : 'bg-white/5 border border-white/10 text-white/40 hover:text-white hover:border-white/20'
                    }`}
                  >
                    {isPremium ? '✦ Premium' : '↑ Улучшить план'}
                  </Link>
                </>
              ) : (
                <>
                  {!isBlocked && (
                    <Link
                      to={`/chat/${profile.username}`}
                      className="px-5 py-2.5 bg-purple-600 hover:bg-purple-500 rounded-xl text-white text-sm font-medium transition-all"
                    >
                      💬 Написать
                    </Link>
                  )}

                  {/* ··· меню */}
                  <div className="relative">
                    <button
                      onClick={() => setMenuOpen(!menuOpen)}
                      className="w-9 h-9 flex items-center justify-center rounded-xl border border-white/10 text-white/40 hover:text-white hover:border-white/25 transition-all text-lg leading-none"
                    >
                      ···
                    </button>
                    {menuOpen && (
                      <>
                        {/* Клик вне меню — закрыть */}
                        <div className="fixed inset-0 z-10" onClick={() => setMenuOpen(false)} />
                        <div className="absolute right-0 top-11 w-48 bg-[#1a1a1a] border border-white/10 rounded-xl overflow-hidden shadow-xl z-20">
                          <button
                            onClick={handleBlock}
                            disabled={blockLoading}
                            className={`w-full px-4 py-3 text-left text-sm transition-colors flex items-center gap-2.5 ${
                              isBlocked
                                ? 'text-white/60 hover:bg-white/5'
                                : 'text-orange-400 hover:bg-orange-500/5'
                            }`}
                          >
                            <span>{isBlocked ? '🔓' : '🚫'}</span>
                            {isBlocked ? 'Разблокировать' : 'Заблокировать'}
                          </button>
                          <div className="border-t border-white/5" />
                          <button
                            onClick={() => { setMenuOpen(false); setReportOpen(true) }}
                            className="w-full px-4 py-3 text-left text-sm text-red-400 hover:bg-red-500/5 transition-colors flex items-center gap-2.5"
                          >
                            <span>⚑</span> Пожаловаться
                          </button>
                        </div>
                      </>
                    )}
                  </div>
                </>
              )}
            </div>
          </div>

          {/* Stats */}
          <div className="flex gap-6 mb-8">
            {[
              [profile.age || '—', 'Лет'],
              [profile.location ? profile.location.slice(0, 8) : '—', 'Город'],
              [profile.gender === 'male' ? 'М' : profile.gender === 'female' ? 'Ж' : '—', 'Пол'],
            ].map(([val, label]) => (
              <div key={label} className="text-center">
                <div className="text-white font-semibold">{val}</div>
                <div className="text-white/30 text-xs">{label}</div>
              </div>
            ))}
          </div>

          {/* Blocked notice */}
          {isBlocked && (
            <div className="mb-4 p-4 bg-orange-500/5 border border-orange-500/15 rounded-xl">
              <p className="text-orange-300/70 text-sm">
                Вы заблокировали этого пользователя — он не отображается в ленте и не может написать вам.
              </p>
              <button
                onClick={handleBlock}
                disabled={blockLoading}
                className="mt-2 text-orange-400 text-xs underline underline-offset-2 hover:text-orange-300 transition-colors"
              >
                Разблокировать
              </button>
            </div>
          )}

          {/* Premium viewers shortcut */}
          {isOwn && isPremium && (
            <Link
              to="/subscription"
              className="flex items-center gap-3 p-4 mb-4 rounded-xl bg-amber-500/5 border border-amber-500/15 hover:border-amber-500/30 transition-all"
            >
              <span className="text-xl">👁</span>
              <div>
                <div className="text-amber-400 text-sm font-medium">Кто смотрел профиль</div>
                <div className="text-white/25 text-xs">Посмотреть в разделе Premium</div>
              </div>
              <span className="ml-auto text-white/20 text-sm">→</span>
            </Link>
          )}

          {/* Content grid */}
          <div className="grid md:grid-cols-3 gap-4">
            <div className="md:col-span-2 space-y-4">
              <div className="bg-white/[0.03] border border-white/8 rounded-2xl p-5">
                <div className="text-white/30 text-xs font-medium uppercase tracking-wider mb-3">О себе</div>
                <p className={`text-sm leading-relaxed ${profile.bio ? 'text-white/70' : 'text-white/15'}`}>
                  {profile.bio || 'Пока ничего не написано'}
                </p>
              </div>
              <div className="bg-white/[0.03] border border-white/8 rounded-2xl p-5">
                <div className="text-white/30 text-xs font-medium uppercase tracking-wider mb-3">Теги</div>
                <div className="flex flex-wrap gap-2">
                  {profile.location && <span className="px-3 py-1 bg-white/5 border border-white/8 rounded-full text-white/50 text-xs">📍 {profile.location}</span>}
                  {profile.gender && <span className="px-3 py-1 bg-white/5 border border-white/8 rounded-full text-white/50 text-xs">{profile.gender === 'male' ? '👨 Парень' : '👩 Девушка'}</span>}
                  {profile.age && <span className="px-3 py-1 bg-white/5 border border-white/8 rounded-full text-white/50 text-xs">🎂 {profile.age} лет</span>}
                  {isPremium && <span className="px-3 py-1 bg-amber-500/10 border border-amber-500/20 rounded-full text-amber-400/70 text-xs">✦ Premium</span>}
                </div>
              </div>
            </div>

            <div className="bg-white/[0.03] border border-white/8 rounded-2xl p-5 h-fit">
              <div className="text-white/30 text-xs font-medium uppercase tracking-wider mb-3">Инфо</div>
              <div className="space-y-3">
                {[
                  ['📍', 'Город',   profile.location || '—'],
                  ['🎂', 'Возраст', profile.age      || '—'],
                  ...(isOwn ? [
                    ['📧', 'Email', profile.email || '—'],
                    ['💎', 'План',  isPremium ? 'Premium' : 'Free'],
                  ] : []),
                ].map(([icon, label, val]) => (
                  <div key={label} className="flex items-center gap-3">
                    <span className="text-base">{icon}</span>
                    <span className="text-white/25 text-xs w-14 shrink-0">{label}</span>
                    <span className={`text-xs truncate ${label === 'План' && isPremium ? 'text-amber-400 font-medium' : 'text-white/60'}`}>{val}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Edit Modal */}
      {editOpen && (
        <div
          className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4"
          onClick={(e) => e.target === e.currentTarget && setEditOpen(false)}
        >
          <div className="bg-[#111] border border-white/10 rounded-2xl p-6 w-full max-w-md">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-white font-semibold">Редактировать профиль</h2>
              <button onClick={() => setEditOpen(false)} className="text-white/30 hover:text-white/60">✕</button>
            </div>
            <form onSubmit={handleSave} className="space-y-4">
              {[['name','Имя','text'],['location','Город','text'],['age','Возраст','number']].map(([k,label,type]) => (
                <div key={k}>
                  <label className="text-white/40 text-xs mb-1.5 block">{label}</label>
                  <input className={inputCls} type={type} value={editForm[k]||''} onChange={(e)=>setEditForm(f=>({...f,[k]:e.target.value}))} />
                </div>
              ))}
              <div>
                <label className="text-white/40 text-xs mb-1.5 block">О себе</label>
                <textarea className={inputCls+' resize-none'} rows={3} value={editForm.bio||''} onChange={(e)=>setEditForm(f=>({...f,bio:e.target.value}))} />
              </div>
              <div>
                <label className="text-white/40 text-xs mb-1.5 block">Аватар</label>
                <input className="w-full text-white/30 text-sm file:mr-3 file:py-1.5 file:px-3 file:rounded-lg file:border-0 file:bg-white/10 file:text-white/60 file:text-xs" type="file" accept="image/*" onChange={(e)=>setEditFile(e.target.files[0])} />
              </div>
              <div className="flex gap-3 pt-2">
                <button type="submit" disabled={saving} className="flex-1 bg-white text-black py-2.5 rounded-xl font-medium text-sm disabled:opacity-50">
                  {saving ? 'Сохраняем...' : 'Сохранить'}
                </button>
                <button type="button" onClick={()=>setEditOpen(false)} className="flex-1 border border-white/15 text-white/50 py-2.5 rounded-xl text-sm">
                  Отмена
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {reportOpen && (
        <ReportModal username={profile.username} onClose={() => setReportOpen(false)} />
      )}

      {toast && <Toast message={toast} type={toastType} onClose={() => setToast(null)} />}
    </div>
  )
}