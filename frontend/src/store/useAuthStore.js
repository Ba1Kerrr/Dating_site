import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import {
  login as apiLogin,
  logout as apiLogout,
  register as apiRegister,
} from '../api'
import api from '../api'

const MODAL_DEFAULT = { login: false, register: false, forgot: false }

const getSessionUser = () => api.get('/auth/session')

const useAuthStore = create(
  persist(
    (set) => ({
      user: null,
      token: null,
      loading: false,
      modal: MODAL_DEFAULT,

      openModal:        (name) => set({ modal: { ...MODAL_DEFAULT, [name]: true } }),
      closeModal:       (name) => set((s) => ({ modal: { ...s.modal, [name]: false } })),
      switchToLogin:    () => set({ modal: { ...MODAL_DEFAULT, login: true } }),
      switchToRegister: () => set({ modal: { ...MODAL_DEFAULT, register: true } }),
      switchToForgot:   () => set({ modal: { ...MODAL_DEFAULT, forgot: true } }),

      login: async (username, password) => {
        try {
          await apiLogin(username, password)
          const res = await getSessionUser()
          set({ user: res.data, modal: MODAL_DEFAULT })
          return { success: true }
        } catch (err) {
          return {
            success: false,
            error: err.response?.data?.detail || 'Неверный логин или пароль',
          }
        }
      },

      // После регистрации возвращаем { success: true, redirect: '/register/dop-info' }
      // чтобы компонент мог сделать navigate()
      register: async (formData) => {
        try {
          await apiRegister({
            username:         formData.username,
            email:            formData.email,
            password:         formData.password,
            confirm_password: formData.confirmPassword,
            input_key:        formData.email_code,
          })
          const res = await getSessionUser()
          set({ user: res.data, modal: MODAL_DEFAULT })
          return { success: true, redirect: '/register/dop-info' }
        } catch (err) {
          return {
            success: false,
            error: err.response?.data?.detail || 'Ошибка регистрации',
          }
        }
      },

      fetchMe: async () => {
        try {
          let res
          try {
            res = await getSessionUser()
          } catch {
            const token = localStorage.getItem('authToken')
            if (!token) { set({ user: null }); return }
            res = await api.get('/auth/me')
          }
          set({ user: res.data })
        } catch {
          set({ user: null })
        }
      },

      logout: async () => {
        try { await apiLogout() } catch {}
        set({ user: null, token: null })
      },
    }),
    {
      name: 'auth',
      partialize: (s) => ({ token: s.token }),
      onRehydrateStorage: () => (state) => {
        if (state) state.modal = MODAL_DEFAULT
      },
    }
  )
)

export default useAuthStore