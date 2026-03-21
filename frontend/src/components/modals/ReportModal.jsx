import { useState } from 'react'
import { Toast } from '../index'
import { reportUser } from '../../api'

const REASONS = [
  { value: 'spam',     label: '📢 Спам',              desc: 'Навязчивая реклама или рассылки' },
  { value: 'fake',     label: '🎭 Фейк',              desc: 'Ненастоящий профиль или чужие фото' },
  { value: 'abuse',    label: '🚫 Оскорбления',       desc: 'Агрессивное или неприемлемое поведение' },
  { value: 'underage', label: '⚠️ Несовершеннолетний', desc: 'Пользователь похож на ребёнка' },
  { value: 'other',    label: '💬 Другое',             desc: 'Иная причина' },
]

export default function ReportModal({ username, onClose }) {
  const [reason,    setReason]    = useState('')
  const [comment,   setComment]   = useState('')
  const [loading,   setLoading]   = useState(false)
  const [toast,     setToast]     = useState(null)
  const [toastType, setToastType] = useState('error')
  const [done,      setDone]      = useState(false)

  const handleSubmit = async () => {
    if (!reason) { setToast('Выберите причину'); setToastType('error'); return }
    setLoading(true)
    try {
      await reportUser(username, reason, comment)
      setDone(true)
    } catch (err) {
      const detail = err.response?.data?.detail
      setToast(detail === 'already_reported'
        ? 'Вы уже жаловались на этого пользователя'
        : detail || 'Ошибка отправки')
      setToastType('error')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div
      className="fixed inset-0 z-[60] bg-black/70 backdrop-blur-sm flex items-center justify-center p-4"
      onClick={(e) => e.target === e.currentTarget && onClose()}
    >
      <div className="bg-[#111] border border-white/10 rounded-2xl p-6 w-full max-w-sm relative">
        <button onClick={onClose} className="absolute top-4 right-4 text-white/30 hover:text-white/60 transition-colors">✕</button>

        {done ? (
          <div className="text-center py-6">
            <div className="text-4xl mb-3">✅</div>
            <h3 className="text-white font-semibold mb-2">Жалоба отправлена</h3>
            <p className="text-white/40 text-sm mb-5">Мы рассмотрим её в течение 48 часов</p>
            <button onClick={onClose} className="px-6 py-2.5 bg-white text-black rounded-xl text-sm font-medium hover:bg-white/90 transition-all">
              Закрыть
            </button>
          </div>
        ) : (
          <>
            <h2 className="text-white font-semibold mb-1">Пожаловаться</h2>
            <p className="text-white/30 text-xs mb-5">
              На пользователя <span className="text-white/60">@{username}</span>
            </p>

            <div className="space-y-2 mb-4">
              {REASONS.map((r) => (
                <div
                  key={r.value}
                  onClick={() => setReason(r.value)}
                  className={`flex items-start gap-3 p-3 rounded-xl border cursor-pointer transition-all select-none ${
                    reason === r.value
                      ? 'border-red-500/40 bg-red-500/5'
                      : 'border-white/8 bg-white/[0.02] hover:border-white/15'
                  }`}
                >
                  <div className={`w-4 h-4 rounded-full border mt-0.5 shrink-0 flex items-center justify-center transition-all ${
                    reason === r.value ? 'border-red-500 bg-red-500' : 'border-white/20'
                  }`}>
                    {reason === r.value && <div className="w-1.5 h-1.5 rounded-full bg-white" />}
                  </div>
                  <div>
                    <div className={`text-sm font-medium ${reason === r.value ? 'text-white' : 'text-white/60'}`}>{r.label}</div>
                    <div className="text-white/25 text-xs">{r.desc}</div>
                  </div>
                </div>
              ))}
            </div>

            {reason === 'other' && (
              <textarea
                className="w-full bg-white/5 border border-white/10 rounded-xl px-3 py-2.5 text-white text-sm placeholder-white/20 focus:outline-none focus:border-white/25 resize-none mb-4"
                rows={3}
                placeholder="Опишите ситуацию..."
                value={comment}
                onChange={(e) => setComment(e.target.value)}
              />
            )}

            <button
              onClick={handleSubmit}
              disabled={loading || !reason}
              className="w-full py-3 bg-red-500/80 hover:bg-red-500 text-white text-sm font-medium rounded-xl transition-all disabled:opacity-40"
            >
              {loading ? 'Отправляем...' : 'Отправить жалобу'}
            </button>
          </>
        )}
      </div>
      {toast && <Toast message={toast} type={toastType} onClose={() => setToast(null)} />}
    </div>
  )
}