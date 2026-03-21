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
  const [dragOver, setDragOver] = useState(false)

  const setField = (k) => (e) => setForm((f) => ({ ...f, [k]: e.target.value }))

  const applyFile = (f) => {
    if (!f) return
    if (!f.type.startsWith('image/')) { setToast('Только изображения'); return }
    if (f.size > 5 * 1024 * 1024) { setToast('Файл слишком большой (макс. 5 МБ)'); return }
    setFile(f)
    setPreview(URL.createObjectURL(f))
  }

  const handleFile = (e) => applyFile(e.target.files[0])

  const handleDrop = (e) => {
    e.preventDefault()
    setDragOver(false)
    applyFile(e.dataTransfer.files[0])
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

  const inputCls =
    'w-full bg-white/5 border border-white/8 rounded-xl px-4 py-3 text-white text-sm ' +
    'placeholder-white/20 focus:outline-none focus:border-white/25 focus:bg-white/8 transition-all'

  const selectCls = inputCls + ' cursor-pointer'

  return (
    <div className="min-h-screen bg-[#0a0a0a] flex items-center justify-center px-4 py-16 relative overflow-hidden">

      {/* Фоновые орбы */}
      <div className="absolute -top-40 -left-40 w-[500px] h-[500px] rounded-full bg-purple-600/8 blur-[120px] pointer-events-none" />
      <div className="absolute -bottom-20 -right-20 w-[400px] h-[400px] rounded-full bg-pink-600/8 blur-[100px] pointer-events-none" />

      <div className="relative w-full max-w-lg">

        {/* Шапка */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-purple-500/10 border border-purple-500/20 text-purple-400 text-xs mb-5">
            <span className="w-1.5 h-1.5 rounded-full bg-purple-400" />
            Шаг 2 из 2
          </div>
          <h1 className="font-unbounded text-white text-2xl font-bold mb-2">
            Привет,{' '}
            <span className="bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
              {user?.username}
            </span>
            !
          </h1>
          <p className="text-white/35 text-sm font-onest leading-relaxed">
            Расскажите о себе — это поможет найти лучших кандидатов
          </p>
        </div>

        {/* Карточка формы */}
        <div className="bg-white/[0.03] border border-white/8 rounded-2xl p-7 backdrop-blur-sm">
          <form onSubmit={handleSubmit} className="space-y-5">

            {/* Имя + Возраст */}
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="text-white/40 text-xs mb-1.5 block">Имя</label>
                <input
                  className={inputCls}
                  placeholder="Ваше имя"
                  value={form.name}
                  onChange={setField('name')}
                />
              </div>
              <div>
                <label className="text-white/40 text-xs mb-1.5 block">Возраст</label>
                <input
                  className={inputCls}
                  type="number"
                  placeholder="22"
                  min="18"
                  max="99"
                  value={form.age}
                  onChange={setField('age')}
                />
              </div>
            </div>

            {/* Пол + Город */}
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="text-white/40 text-xs mb-1.5 block">Пол</label>
                <select className={selectCls} value={form.gender} onChange={setField('gender')}>
                  <option value="male">Мужской</option>
                  <option value="female">Женский</option>
                </select>
              </div>
              <div>
                <label className="text-white/40 text-xs mb-1.5 block">Город</label>
                <input
                  className={inputCls}
                  placeholder="Москва"
                  value={form.location}
                  onChange={setField('location')}
                />
              </div>
            </div>

            {/* О себе */}
            <div>
              <label className="text-white/40 text-xs mb-1.5 block">О себе</label>
              <textarea
                className={inputCls + ' resize-none'}
                rows={3}
                placeholder="Пара слов о вас..."
                value={form.bio}
                onChange={setField('bio')}
              />
            </div>

            {/* Разделитель */}
            <div className="border-t border-white/5 my-1" />

            {/* Фото */}
            <div>
              <label className="text-white/40 text-xs mb-3 block">Фото профиля</label>
              <label
                className={`relative block cursor-pointer rounded-xl border-2 border-dashed transition-all duration-200 overflow-hidden
                  ${dragOver ? 'border-purple-400/60 bg-purple-500/5' : 'border-white/10 hover:border-white/20 hover:bg-white/[0.02]'}`}
                onDragOver={(e) => { e.preventDefault(); setDragOver(true) }}
                onDragLeave={() => setDragOver(false)}
                onDrop={handleDrop}
              >
                <input
                  type="file"
                  accept="image/*"
                  className="hidden"
                  onChange={handleFile}
                />

                {preview ? (
                  <div className="relative">
                    <img
                      src={preview}
                      alt="preview"
                      className="w-full h-48 object-cover"
                    />
                    <div className="absolute inset-0 bg-black/40 flex items-center justify-center opacity-0 hover:opacity-100 transition-opacity">
                      <span className="text-white text-xs bg-black/60 px-3 py-1.5 rounded-full">
                        Сменить фото
                      </span>
                    </div>
                  </div>
                ) : (
                  <div className="flex flex-col items-center justify-center py-10 px-4 text-center">
                    <div className="w-12 h-12 rounded-xl bg-white/5 flex items-center justify-center text-2xl mb-3">
                      📷
                    </div>
                    <div className="text-white/50 text-sm mb-1">
                      Нажмите или перетащите фото
                    </div>
                    <div className="text-white/20 text-xs">JPG, PNG до 5 МБ</div>
                  </div>
                )}
              </label>
            </div>

            {/* Кнопка */}
            <button
              type="submit"
              disabled={loading}
              className="w-full py-3.5 bg-white text-black text-sm font-semibold rounded-xl hover:bg-white/90 transition-all disabled:opacity-40 disabled:cursor-not-allowed hover:scale-[1.01] active:scale-[0.99]"
            >
              {loading ? (
                <span className="flex items-center justify-center gap-2">
                  <span className="w-4 h-4 border-2 border-black/20 border-t-black rounded-full animate-spin" />
                  Сохраняем...
                </span>
              ) : (
                'Завершить регистрацию →'
              )}
            </button>

            {/* Пропустить */}
            <button
              type="button"
              onClick={() => navigate('/')}
              className="w-full text-white/20 text-xs hover:text-white/40 transition-colors py-1"
            >
              Пропустить, заполню позже
            </button>
          </form>
        </div>
      </div>

      {toast && <Toast message={toast} onClose={() => setToast(null)} />}
    </div>
  )
}