import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { getProfile, editProfile } from '../api'
import useAuthStore from '../store/useAuthStore'
import Navbar from '../components/Navbar'
import { Toast } from '../components'

const API = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export default function Profile() {
  const { username } = useParams()
  const { user } = useAuthStore()
  const [profile, setProfile] = useState(null)
  const [isOwn, setIsOwn] = useState(false)
  const [editOpen, setEditOpen] = useState(false)
  const [editForm, setEditForm] = useState({})
  const [editFile, setEditFile] = useState(null)
  const [saving, setSaving] = useState(false)
  const [toast, setToast] = useState(null)
  const [toastType, setToastType] = useState('error')

  useEffect(() => {
    getProfile(username).then((r) => {
      setProfile(r.data.profile)
      setIsOwn(r.data.is_own)
    })
  }, [username])

  const openEdit = () => {
    setEditForm({
      name: profile?.name || '',
      bio: profile?.bio || '',
      location: profile?.location || '',
      age: profile?.age || '',
    })
    setEditOpen(true)
  }

  const handleSave = async (e) => {
    e.preventDefault()
    setSaving(true)
    try {
      await editProfile(username, { ...editForm, file: editFile })
      const r = await getProfile(username)
      setProfile(r.data.profile)
      setEditOpen(false)
      setToast('Профиль обновлён')
      setToastType('success')
    } catch (err) {
      setToast(err.response?.data?.detail || 'Ошибка сохранения')
      setToastType('error')
    } finally {
      setSaving(false)
    }
  }

  if (!profile) {
    return (
      <div className="min-h-screen bg-[#0a0a0a] flex items-center justify-center">
        <div className="text-white/20 text-sm">Загрузка...</div>
      </div>
    )
  }

  const avatarUrl = profile.avatar ? `${API}/static/${profile.avatar}` : null
  const initial = (profile.name || profile.username || '?')[0].toUpperCase()

  return (
    <div className="min-h-screen bg-[#0a0a0a]">
      <Navbar />

      {/* Hero */}
      <div className="pt-16 relative">
        <div className="h-48 bg-gradient-to-br from-purple-900/40 to-pink-900/20" />
        <div className="max-w-3xl mx-auto px-4 pb-6">
          <div className="flex items-end justify-between -mt-16 mb-6">
            <div className="flex items-end gap-5">
              <div className="w-28 h-28 rounded-2xl border-4 border-[#0a0a0a] overflow-hidden bg-purple-500/20 flex items-center justify-center text-purple-300 text-3xl font-bold">
                {avatarUrl
                  ? <img src={avatarUrl} alt={profile.name} className="w-full h-full object-cover" />
                  : initial}
              </div>
              <div className="pb-1">
                <div className="text-white font-unbounded font-semibold text-xl">
                  {profile.name || profile.username}
                </div>
                <div className="text-white/30 text-sm">@{profile.username}</div>
              </div>
            </div>
            <div className="pb-1">
              {isOwn ? (
                <button
                  onClick={openEdit}
                  className="px-5 py-2.5 border border-white/20 rounded-xl text-white/70 hover:text-white hover:border-white/40 text-sm transition-all"
                >
                  ✏ Редактировать
                </button>
              ) : (
                <Link
                  to={`/chat/${profile.username}`}
                  className="px-5 py-2.5 bg-purple-600 hover:bg-purple-500 rounded-xl text-white text-sm font-medium transition-all"
                >
                  💬 Написать
                </Link>
              )}
            </div>
          </div>

          {/* Stats */}
          <div className="flex gap-6 mb-8 text-center">
            <div>
              <div className="text-white font-semibold">{profile.age || '—'}</div>
              <div className="text-white/30 text-xs">Лет</div>
            </div>
            <div>
              <div className="text-white font-semibold">{profile.location ? profile.location.slice(0, 3).toUpperCase() : '—'}</div>
              <div className="text-white/30 text-xs">Город</div>
            </div>
            <div>
              <div className="text-white font-semibold">{profile.gender === 'male' ? 'М' : profile.gender === 'female' ? 'Ж' : '—'}</div>
              <div className="text-white/30 text-xs">Пол</div>
            </div>
          </div>

          <div className="grid md:grid-cols-3 gap-4">
            <div className="md:col-span-2 space-y-4">
              <div className="bg-white/5 border border-white/10 rounded-2xl p-5">
                <div className="text-white/40 text-xs font-medium uppercase tracking-wider mb-3">О себе</div>
                <p className={`text-sm leading-relaxed ${profile.bio ? 'text-white/80' : 'text-white/20'}`}>
                  {profile.bio || 'Пока ничего не написано'}
                </p>
              </div>
              <div className="bg-white/5 border border-white/10 rounded-2xl p-5">
                <div className="text-white/40 text-xs font-medium uppercase tracking-wider mb-3">Теги</div>
                <div className="flex flex-wrap gap-2">
                  {profile.location && <span className="px-3 py-1 bg-white/5 border border-white/10 rounded-full text-white/60 text-xs">📍 {profile.location}</span>}
                  {profile.gender && <span className="px-3 py-1 bg-white/5 border border-white/10 rounded-full text-white/60 text-xs">{profile.gender === 'male' ? '👨 Парень' : '👩 Девушка'}</span>}
                  {profile.age && <span className="px-3 py-1 bg-white/5 border border-white/10 rounded-full text-white/60 text-xs">🎂 {profile.age} лет</span>}
                  <span className="px-3 py-1 bg-white/5 border border-white/10 rounded-full text-white/60 text-xs">✨ На сайте</span>
                </div>
              </div>
            </div>
            <div className="bg-white/5 border border-white/10 rounded-2xl p-5 h-fit">
              <div className="text-white/40 text-xs font-medium uppercase tracking-wider mb-3">Инфо</div>
              <div className="space-y-3 text-sm">
                <div className="flex items-center gap-3">
                  <span>📍</span>
                  <span className="text-white/40 text-xs w-14">Город</span>
                  <span className="text-white/70">{profile.location || '—'}</span>
                </div>
                {isOwn && (
                  <div className="flex items-center gap-3">
                    <span>📧</span>
                    <span className="text-white/40 text-xs w-14">Email</span>
                    <span className="text-white/70 text-xs truncate">{profile.email || '—'}</span>
                  </div>
                )}
                <div className="flex items-center gap-3">
                  <span>🎂</span>
                  <span className="text-white/40 text-xs w-14">Возраст</span>
                  <span className="text-white/70">{profile.age || '—'}</span>
                </div>
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
            <h2 className="text-white font-semibold mb-6">Редактировать профиль</h2>
            <form onSubmit={handleSave} className="space-y-4">
              {[['name', 'Имя', 'text'], ['location', 'Город', 'text'], ['age', 'Возраст', 'number']].map(([k, label, type]) => (
                <div key={k}>
                  <label className="text-white/40 text-xs mb-1.5 block">{label}</label>
                  <input
                    className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white text-sm placeholder-white/20 focus:outline-none focus:border-white/30 transition-colors"
                    type={type}
                    value={editForm[k] || ''}
                    onChange={(e) => setEditForm((f) => ({ ...f, [k]: e.target.value }))}
                  />
                </div>
              ))}
              <div>
                <label className="text-white/40 text-xs mb-1.5 block">О себе</label>
                <textarea
                  className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white text-sm placeholder-white/20 focus:outline-none focus:border-white/30 transition-colors resize-none"
                  rows={3}
                  value={editForm.bio || ''}
                  onChange={(e) => setEditForm((f) => ({ ...f, bio: e.target.value }))}
                />
              </div>
              <div>
                <label className="text-white/40 text-xs mb-1.5 block">Аватар</label>
                <input
                  className="w-full text-white/40 text-sm"
                  type="file"
                  accept="image/*"
                  onChange={(e) => setEditFile(e.target.files[0])}
                />
              </div>
              <div className="flex gap-3 pt-2">
                <button
                  type="submit"
                  disabled={saving}
                  className="flex-1 bg-white text-black py-2.5 rounded-xl font-medium hover:bg-white/90 transition-all disabled:opacity-50"
                >
                  {saving ? 'Сохраняем...' : 'Сохранить'}
                </button>
                <button
                  type="button"
                  onClick={() => setEditOpen(false)}
                  className="flex-1 border border-white/20 text-white/60 py-2.5 rounded-xl hover:border-white/40 transition-all"
                >
                  Отмена
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {toast && <Toast message={toast} type={toastType} onClose={() => setToast(null)} />}
    </div>
  )
}