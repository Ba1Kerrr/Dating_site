import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { getChatList } from '../api'
import Navbar from '../components/Navbar'

const API = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export default function ChatList() {
  const [chats, setChats] = useState([])
  const [search, setSearch] = useState('')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    getChatList()
      .then((r) => setChats(r.data.chats || []))
      .catch(() => setChats([]))
      .finally(() => setLoading(false))
  }, [])

  const filtered = chats.filter((c) =>
    c.companion.toLowerCase().includes(search.toLowerCase())
  )
  const unread = filtered.filter((c) => c.unread_count > 0)
  const read = filtered.filter((c) => !c.unread_count)

  const formatTime = (ts) => {
    if (!ts) return ''
    return new Date(ts).toLocaleTimeString('ru', { hour: '2-digit', minute: '2-digit' })
  }

  const ChatItem = ({ chat }) => (
    <Link
      to={`/chat/${chat.companion}`}
      className="flex items-center gap-4 px-4 py-3 rounded-xl hover:bg-white/5 transition-colors group"
    >
      <div className="relative shrink-0">
        {chat.avatar ? (
          <img
            src={`${API}/static/${chat.avatar}`}
            alt={chat.companion}
            className="w-12 h-12 rounded-full object-cover"
            onError={(e) => { e.target.style.display = 'none' }}
          />
        ) : (
          <div className="w-12 h-12 rounded-full bg-purple-500/20 border border-purple-500/30 flex items-center justify-center text-purple-300 font-semibold">
            {chat.companion[0].toUpperCase()}
          </div>
        )}
        {chat.unread_count > 0 && (
          <div className="absolute -top-1 -right-1 w-5 h-5 bg-purple-500 rounded-full flex items-center justify-center text-xs text-white font-bold">
            {chat.unread_count}
          </div>
        )}
      </div>
      <div className="flex-1 min-w-0">
        <div className={`text-sm font-medium ${chat.unread_count ? 'text-white' : 'text-white/80'}`}>
          {chat.companion}
        </div>
        <div className="text-white/30 text-xs truncate mt-0.5">
          {chat.last_message || 'Нет сообщений'}
        </div>
      </div>
      {chat.last_message_at && (
        <div className="text-white/20 text-xs shrink-0">{formatTime(chat.last_message_at)}</div>
      )}
    </Link>
  )

  return (
    <div className="min-h-screen bg-[#0a0a0a]">
      <Navbar />
      <main className="pt-20 px-4 max-w-xl mx-auto py-10">
        <h1 className="font-unbounded text-white text-2xl font-semibold mb-1">Сообщения</h1>
        <p className="text-white/30 text-sm font-onest mb-6">{chats.length} активных чатов</p>

        <div className="relative mb-6">
          <span className="absolute left-4 top-1/2 -translate-y-1/2 text-white/20 text-lg">⌕</span>
          <input
            className="w-full bg-white/5 border border-white/10 rounded-xl pl-10 pr-4 py-3 text-white text-sm placeholder-white/20 focus:outline-none focus:border-white/30 transition-colors"
            placeholder="Поиск по имени..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>

        {loading ? (
          <div className="space-y-2">
            {[...Array(5)].map((_, i) => (
              <div key={i} className="h-16 bg-white/5 rounded-xl animate-pulse" />
            ))}
          </div>
        ) : filtered.length > 0 ? (
          <div>
            {unread.length > 0 && (
              <>
                <div className="text-white/20 text-xs font-medium uppercase tracking-wider mb-2 px-4">
                  Непрочитанные
                </div>
                <div className="mb-4">{unread.map((c) => <ChatItem key={c.companion} chat={c} />)}</div>
                <div className="text-white/20 text-xs font-medium uppercase tracking-wider mb-2 px-4">
                  Все чаты
                </div>
              </>
            )}
            <div>{read.map((c) => <ChatItem key={c.companion} chat={c} />)}</div>
          </div>
        ) : (
          <div className="text-center py-20">
            <div className="text-5xl mb-4">💬</div>
            <h3 className="text-white/60 font-medium mb-2">Пока нет чатов</h3>
            <p className="text-white/30 text-sm">Сделай мэтч с кем-нибудь и начни общение</p>
          </div>
        )}
      </main>
    </div>
  )
}