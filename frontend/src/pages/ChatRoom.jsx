import { useEffect, useRef, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { getChatHistory } from '../api'
import useAuthStore from '../store/useAuthStore'

const WS_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000'

export default function ChatRoom() {
  const { companion } = useParams()
  const { user } = useAuthStore()
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [status, setStatus] = useState('connecting') // connecting | online | offline
  const [offset, setOffset] = useState(0)
  const [hasMore, setHasMore] = useState(true)
  const wsRef = useRef(null)
  const bottomRef = useRef(null)
  const inputRef = useRef(null)

  // Загрузка истории
  useEffect(() => {
    getChatHistory(companion, 50, 0).then((r) => {
      const msgs = r.data.messages || []
      setMessages(msgs)
      setOffset(msgs.length)
      setTimeout(() => bottomRef.current?.scrollIntoView(), 50)
    })
  }, [companion])

  // WebSocket
  useEffect(() => {
    const connect = () => {
      const ws = new WebSocket(
        `${WS_URL}/api/chat/ws/${companion}?username=${user?.username}`
      )
      wsRef.current = ws

      ws.onopen = () => setStatus('online')
      ws.onclose = () => {
        setStatus('offline')
        setTimeout(connect, 3000)
      }
      ws.onerror = () => setStatus('offline')
      ws.onmessage = (e) => {
        const data = JSON.parse(e.data)
        if (data.type === 'status') return
        if (data.error) return
        setMessages((prev) => [...prev, data])
        setOffset((o) => o + 1)
        setTimeout(() => bottomRef.current?.scrollIntoView({ behavior: 'smooth' }), 50)
      }
    }
    connect()
    return () => wsRef.current?.close()
  }, [companion, user])

  const sendMessage = () => {
    const text = input.trim()
    if (!text || wsRef.current?.readyState !== WebSocket.OPEN) return
    wsRef.current.send(JSON.stringify({ text }))
    setInput('')
    inputRef.current?.focus()
  }

  const handleKey = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  const loadMore = async () => {
    const r = await getChatHistory(companion, 30, offset)
    const older = r.data.messages || []
    if (!older.length) { setHasMore(false); return }
    setMessages((prev) => [...older, ...prev])
    setOffset((o) => o + older.length)
  }

  const formatTime = (ts) => {
    if (!ts) return ''
    return new Date(ts).toLocaleTimeString('ru', { hour: '2-digit', minute: '2-digit' })
  }

  const statusColor = { connecting: 'text-yellow-400', online: 'text-green-400', offline: 'text-red-400' }
  const statusText = { connecting: 'соединение...', online: 'онлайн', offline: 'нет соединения' }

  return (
    <div className="flex flex-col h-screen bg-[#0a0a0a]">
      {/* Header */}
      <div className="flex items-center gap-4 px-4 py-4 border-b border-white/10 bg-black/60 backdrop-blur">
        <Link to="/chat" className="text-white/40 hover:text-white transition-colors text-lg">←</Link>
        <div className="w-9 h-9 rounded-full bg-purple-500/20 border border-purple-500/30 flex items-center justify-center text-purple-300 font-semibold text-sm">
          {companion[0].toUpperCase()}
        </div>
        <div>
          <div className="text-white font-medium text-sm">{companion}</div>
          <div className={`text-xs ${statusColor[status]}`}>{statusText[status]}</div>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-4 py-4 space-y-2">
        {hasMore && (
          <div className="text-center mb-4">
            <button
              onClick={loadMore}
              className="text-white/30 text-xs hover:text-white/50 transition-colors"
            >
              загрузить старые сообщения
            </button>
          </div>
        )}

        {messages.map((msg, i) => {
          const isMine = msg.sender === user?.username
          return (
            <div key={msg.id || i} className={`flex ${isMine ? 'justify-end' : 'justify-start'}`}>
              <div className={`max-w-[70%] px-4 py-2.5 rounded-2xl text-sm leading-relaxed ${
                isMine
                  ? 'bg-purple-600 text-white rounded-br-sm'
                  : 'bg-white/10 text-white/90 rounded-bl-sm'
              }`}>
                <div>{msg.text}</div>
                {msg.created_at && (
                  <div className={`text-xs mt-1 ${isMine ? 'text-purple-300' : 'text-white/30'} text-right`}>
                    {formatTime(msg.created_at)}
                  </div>
                )}
              </div>
            </div>
          )
        })}
        <div ref={bottomRef} />
      </div>

      {/* Input */}
      <div className="flex items-end gap-3 px-4 py-4 border-t border-white/10 bg-black/60 backdrop-blur">
        <textarea
          ref={inputRef}
          className="flex-1 bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white text-sm placeholder-white/20 focus:outline-none focus:border-white/30 transition-colors resize-none min-h-[46px] max-h-[120px]"
          placeholder="Напиши сообщение..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKey}
          rows={1}
        />
        <button
          onClick={sendMessage}
          disabled={!input.trim() || status !== 'online'}
          className="w-11 h-11 rounded-xl bg-purple-600 hover:bg-purple-500 disabled:bg-white/10 disabled:text-white/20 text-white transition-all flex items-center justify-center text-lg shrink-0"
        >
          ➤
        </button>
      </div>
    </div>
  )
}