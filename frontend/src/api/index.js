import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_URL,
  withCredentials: true,
  headers: { 'Content-Type': 'application/json' },
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('authToken')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      const token = localStorage.getItem('authToken')
      const url = err.config?.url || ''
      const isAuthRoute =
        url.includes('/api/login') || url.includes('/api/register') ||
        url.includes('/auth/token') || url.includes('/api/forgot')
      if (token && !isAuthRoute) {
        localStorage.removeItem('authToken')
        window.location.href = '/'
      }
    }
    return Promise.reject(err)
  }
)

export const login = (username, password) =>
  api.post('/api/login', new URLSearchParams({ username, password }), {
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  })
export const logout       = ()     => api.post('/api/logout')
export const getToken     = (u, p) => api.post('/auth/token', { username: u, password: p })
export const refreshToken = (t)    => api.post('/auth/refresh', { refresh_token: t })
export const getMe        = ()     => api.get('/auth/me')

export const register = (data) =>
  api.post('/api/register', new URLSearchParams({
    username: data.username, email: data.email,
    password: data.password, confirm_password: data.confirm_password,
    input_key: data.input_key ?? data.email_code ?? '',
  }), { headers: { 'Content-Type': 'application/x-www-form-urlencoded' } })

export const sendEmailCode = (email) => api.post('/api/register/send-email', { email })

export const submitDopInfo = (data) => {
  const form = new FormData()
  form.append('age', data.age)
  form.append('gender', data.gender)
  form.append('name', data.name)
  form.append('location', data.location)
  form.append('bio', data.bio)
  if (data.file) form.append('file', data.file)
  return api.post('/api/register/dop-info', form)
}


export const getProfile  = (username) => api.get(`/api/profile/${username}`)
export const editProfile = (username, data) => {
  const form = new FormData()
  if (data.name)     form.append('name', data.name)
  if (data.bio)      form.append('bio', data.bio)
  if (data.location) form.append('location', data.location)
  if (data.age)      form.append('age', data.age)
  if (data.file)     form.append('file', data.file)
  return api.post(`/api/profile/${username}/edit`, form)
}


export const getFeed = () => api.get('/api/feed')

export const getChatList    = ()                          => api.get('/api/chat/list')
export const getChatHistory = (companion, limit=50, offset=0) =>
  api.get(`/api/chat/${companion}/history`, { params: { limit, offset } })

export const forgotPassword = (data) =>
  api.post('/api/forgot/password', new URLSearchParams(data), {
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  })
export const forgotUsername = (data) =>
  api.post('/api/forgot/username', new URLSearchParams(data), {
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  })


export const getSubscription   = ()       => api.get('/api/subscription/me')
export const activatePromo     = (code)   => api.post('/api/subscription/activate', { plan: 'premium', days: 30, promo_code: code })
export const getProfileViewers = (limit=20) => api.get('/api/subscription/viewers', { params: { limit } })
export const getPremiumFeed    = (f={})   => api.get('/api/subscription/feed/filtered', { params: f })

export const blockUser   = (username) => api.post(`/api/users/${username}/block`)
export const unblockUser = (username) => api.delete(`/api/users/${username}/block`)
export const getMyBlocks = ()         => api.get('/api/users/blocks')
export const reportUser  = (username, reason, comment) =>
  api.post(`/api/users/${username}/report`, { reason, comment })

export const getAdminReports = (status='pending', limit=50, offset=0) =>
  api.get('/api/admin/reports', { params: { status, limit, offset } })
export const reviewReport    = (id, action) =>
  api.post(`/api/admin/reports/${id}/review`, { action })

export default api