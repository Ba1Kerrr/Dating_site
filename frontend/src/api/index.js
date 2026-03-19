import axios from 'axios'

// Определяем базовый URL
const baseURL = import.meta.env.PROD 
  ? '/api' 
  : (import.meta.env.VITE_API_URL || 'http://localhost:8000')

// Создаём axios
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  withCredentials: true,
})

// перехватчик — тихо игнорируем 401
api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) return Promise.reject(err) // тихо
    console.error(err)
    return Promise.reject(err)
  }
)

export const login = (username, password) => {
  const form = new FormData()
  form.append('username', username)
  form.append('password', password)
  return api.post('/api/login', form)
}

export const logout = () => api.post('/api/logout')

export const getToken = (username, password) =>
  api.post('/api/auth/token', { username, password })

export const refreshToken = (refresh_token) =>
  api.post('/api/auth/refresh', { refresh_token })

export const getMe = () => api.get('/auth/session')


export const register = (data) => {
  const form = new FormData()
  Object.entries(data).forEach(([k, v]) => form.append(k, v))
  return api.post('/api/register', form)
}

export const sendEmailCode = (email) =>
  api.post('/api/register/send-email', { email })

export const submitDopInfo = (data) => {
  const form = new FormData()
  Object.entries(data).forEach(([k, v]) => {
    if (v !== undefined && v !== null) form.append(k, v)
  })
  return api.post('/api/register/dop-info', form)
}

export const getProfile = (username) =>
  api.get(`/api/profile/${username}`)

export const editProfile = (username, data) => {
  const form = new FormData()
  Object.entries(data).forEach(([k, v]) => {
    if (v !== undefined && v !== null) form.append(k, v)
  })
  return api.post(`/api/profile/${username}/edit`, form)
}


export const getFeed = () => api.get('/api/feed')


export const getChatList = () => api.get('/api/chat/list')

export const getChatHistory = (companion, limit = 50, offset = 0) =>
  api.get(`/api/chat/${companion}/history`, { params: { limit, offset } })

export const forgotPassword = (data) =>
  api.post('/forgot_password', new URLSearchParams(data))

export const forgotUsername = (data) =>
  api.post('/forgot_username', new URLSearchParams(data))

export default api