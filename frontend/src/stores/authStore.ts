import { create } from 'zustand'
import { apiClient } from '../api/client'

interface User {
  id: string
  email: string
  is_admin: boolean
}

interface AuthStore {
  user: User | null
  token: string | null
  isAuthenticated: boolean
  isLoading: boolean
  error: string | null
  login: (email: string, password: string) => Promise<void>
  register: (email: string, password: string, passwordConfirm: string) => Promise<void>
  logout: () => Promise<void>
  setUser: (user: User) => void
  checkAuth: () => Promise<void>
  clearError: () => void
}

export const useAuthStore = create<AuthStore>((set, get) => ({
  user: null,
  token: localStorage.getItem('token'),
  isAuthenticated: !!localStorage.getItem('token'),
  isLoading: false,
  error: null,

  login: async (email: string, password: string) => {
    set({ isLoading: true, error: null })
    try {
      console.log('[authStore.login] Starting login request to /api/auth/login', { email })
      const response = await apiClient.post('/auth/login', {
        email,
        password
      })

      console.log('[authStore.login] Login response received:', response.status, response.data)

      // Backend returns: { access_token, token_type, user_id, email, message }
      const { access_token, user_id, email: userEmail } = response.data

      if (!access_token) {
        throw new Error('No access_token in response')
      }

      console.log('[authStore.login] Token received, saving to localStorage', { user_id, userEmail })

      // Save token to localStorage
      localStorage.setItem('token', access_token)

      // Add token to axios header
      apiClient.defaults.headers.common['Authorization'] = `Bearer ${access_token}`

      set({
        user: {
          id: user_id,
          email: userEmail,
          is_admin: false
        },
        token: access_token,
        isAuthenticated: true,
        isLoading: false
      })

      console.log('[authStore.login] Login state updated successfully')
    } catch (error: any) {
      const message = error?.response?.data?.detail || error?.message || 'Error logging in'
      console.error('[authStore.login] Login error:', {
        status: error?.response?.status,
        detail: error?.response?.data?.detail,
        message: error?.message,
        fullError: error
      })
      set({
        isLoading: false,
        error: message
      })
      throw new Error(message)
    }
  },

  register: async (email: string, password: string, passwordConfirm: string) => {
    set({ isLoading: true, error: null })
    try {
      const response = await apiClient.post('/auth/register', {
        email,
        password,
        password_confirm: passwordConfirm
      })

      // Backend returns: { access_token, token_type, user_id, email, message }
      const { access_token, user_id, email: userEmail } = response.data

      // Save token to localStorage
      localStorage.setItem('token', access_token)

      // Add token to axios header
      apiClient.defaults.headers.common['Authorization'] = `Bearer ${access_token}`

      set({
        user: {
          id: user_id,
          email: userEmail,
          is_admin: false
        },
        token: access_token,
        isAuthenticated: true,
        isLoading: false
      })
    } catch (error: any) {
      const message = error?.response?.data?.detail || 'Error creating account'
      set({
        isLoading: false,
        error: message
      })
      throw new Error(message)
    }
  },

  logout: async () => {
    try {
      await apiClient.post('/auth/logout')
    } catch (error) {
      console.error('Error logging out:', error)
    } finally {
      // Remove token from localStorage and headers
      localStorage.removeItem('token')
      delete apiClient.defaults.headers.common['Authorization']

      set({
        user: null,
        token: null,
        isAuthenticated: false,
        error: null
      })
    }
  },

  setUser: (user: User) => {
    set({ user })
  },

  checkAuth: async () => {
    const token = get().token
    if (!token) return

    try {
      const response = await apiClient.get('/auth/me', {
        params: { token }
      })

      const { user } = response.data

      set({
        user,
        isAuthenticated: true
      })
    } catch (error) {
      // Invalid or expired token
      localStorage.removeItem('token')
      delete apiClient.defaults.headers.common['Authorization']

      set({
        user: null,
        token: null,
        isAuthenticated: false
      })
    }
  },

  clearError: () => {
    set({ error: null })
  }
}))

// Restore token from localStorage and add to axios header on initialization
const token = localStorage.getItem('token')
if (token) {
  apiClient.defaults.headers.common['Authorization'] = `Bearer ${token}`
}
