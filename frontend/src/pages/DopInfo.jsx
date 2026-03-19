import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { submitDopInfo } from '../api'
import useAuthStore from '../store/useAuthStore'
import { Toast } from '../components'

export default function DopInfo() {
  const { user } = useAuthStore()
  const navigate = useNavigate()
  const [form, setForm] = useState({ name: '', age: '', gender: 'male', location: '', bio: '' })
  const [file, setFile] = useState(null)
  const [preview, setPreview] = useState(null)
  const [loading, setLoading] = useState(false)
  const [toast, setToast] = useState(null)

  const set = (k) => (e) => setForm((f) => ({ ...f, [k]: e.target.value }))

  const handleFile = (e) => {
    const f = e.target.files[0]
    if (!f) return
    setFile(f)
    setPreview(URL.createObjectURL(f))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    try {
      await submitDopInfo({ ...form, file })
      navigate('/')
    } catch (err) {
      setToast(err.response?.data?.detail || 'Ошибка сохранения')
    } finally {
      setLoading(false)
    }
  }

  const inputCls = 'w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white text-sm placeholder-white/20 focus:outline-none focus:border-white/30 transition-colors'

  return (
    <div className="min-h-screen bg-[#0a0a0a] flex items-center justify-center px-4 py-12">
      <div className="w-full max-w-lg">
        <div className="bg-white/5 border border-white/10 rounded-2xl p-8">
          <div className="text-xs text-purple-400 font-medium mb-2">Шаг 2 из 2</div>
          <h1 className="font-unbounded text-white text-xl font-semibold mb-1">
            Привет, <span className="text-purple-400">{user?.username}</span>!
          </h1>
          <p className="text-white/40 text-sm font-onest mb-8">
            Расскажите о себе — это поможет найти лучших кандидатов
          </p>

          <form onSubmit={handleSubmit} className="space-y-5">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="text-white/60 text-xs mb-1.5 block">Имя</label>
                <input className={inputCls} placeholder="Ваше имя" value={form.name} onChange={set('name')} />
              </div>
              <div>
                <label className="text-white/60 text-xs mb-1.5 block">Возраст</label>
                <input className={inputCls} type="number" placeholder="22" min="18" max="99" value={form.age} onChange={set('age')} />
              </div>
              <div>
                <label className="text-white/60 text-xs mb-1.5 block">Пол</label>
                <select className={inputCls + ' cursor-pointer'} value={form.gender} onChange={set('gender')}>
                  <option value="male">Мужской</option>
                  <option value="female">Женский</option>
                </select>
              </div>
              <div>
                <label className="text-white/60 text-xs mb-1.5 block">Город</label>
                <input className={inputCls} placeholder="Москва" value={form.location} onChange={set('location')} />
              </div>
            </div>

            <div>
              <label className="text-white/60 text-xs mb-1.5 block">О себе</label>
              <input className={inputCls} placeholder="Пара слов о вас..." value={form.bio} onChange={set('bio')} />
            </div>

            <div className="border-t border-white/10 pt-5">
              <label className="text-white/60 text-xs mb-3 block">Фото профиля</label>
              <label className="block cursor-pointer">
                <input type="file" accept="image/*" className="hidden" onChange={handleFile} />
                <div className="border-2 border-dashed border-white/10 rounded-xl p-6 text-center hover:border-white/20 transition-colors">
                  {preview ? (
                    <img src={preview} alt="preview" className="w-24 h-24 rounded-full object-cover mx-auto" />
                  ) : (
                    <>
                      <div className="text-3xl mb-2">📷</div>
                      <div className="text-white/40 text-sm">Нажмите или перетащите фото</div>
                      <div className="text-white/20 text-xs mt-1">JPG, PNG до 5 МБ</div>
                    </>
                  )}
                </div>
              </label>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-white text-black font-medium py-3 rounded-xl hover:bg-white/90 transition-all disabled:opacity-50"
            >
              {loading ? 'Сохраняем...' : 'Завершить регистрацию →'}
            </button>
          </form>
        </div>
      </div>

      {toast && <Toast message={toast} onClose={() => setToast(null)} />}
    </div>
  )
}