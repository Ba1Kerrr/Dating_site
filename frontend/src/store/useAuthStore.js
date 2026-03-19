import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import {
  getMe,
  login as apiLogin,
  logout as apiLogout,
  register as apiRegister,
} from '../api'

const MODAL_DEFAULT = { login: false, register: false, forgot: false }

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
          const res = await getMe()
          set({ user: res.data, modal: MODAL_DEFAULT })
          return { success: true }
        } catch (err) {
          return { success: false, error: err.response?.data?.detail || 'Неверный логин или пароль' }
        }
      },

      register: async (formData) => {
        try {
          await apiRegister({
            username:         formData.username,
            email:            formData.email,
            input_key:        formData.email_code,
            password:         formData.password,
            confirm_password: formData.confirmPassword,
          })
          const res = await getMe()
          set({ user: res.data, modal: MODAL_DEFAULT })
          return { success: true }
        } catch (err) {
          return { success: false, error: err.response?.data?.detail || 'Ошибка регистрации' }
        }
      },

      fetchMe: async () => {
        try {
          set({ loading: true })
          const res = await getMe()
          set({ user: res.data, loading: false })
        } catch {
          set({ user: null, loading: false })
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