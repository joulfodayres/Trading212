import { create } from 'zustand'
import { apiClient } from '../api/client'

interface User {
  id: string
  email: string
  is_admin: boolean
  totp_enabled: boolean
}

interface AuthStore {
  user: User | null
  isAuthenticated: boolean
  isLoading: boolean
  error: string | null

  // MFA login flow (step 1 -> step 2)
  mfaRequired: boolean
  mfaSetupRequired: boolean
  preAuthToken: string | null

  login: (email: string, password: string) => Promise<void>
  verifyMfa: (code: string, trustDevice: boolean) => Promise<void>
  register: (email: string, password: string, passwordConfirm: string) => Promise<void>
  logout: () => Promise<void>
  logoutAll: () => Promise<void>
  checkAuth: () => Promise<void>
  clearError: () => void
  clearMfaFlow: () => void
}

export const useAuthStore = create<AuthStore>((set, get) => ({
  user: null,
  isAuthenticated: false,
  isLoading: false,
  error: null,

  mfaRequired: false,
  mfaSetupRequired: false,
  preAuthToken: null,

  login: async (email: string, password: string) => {
    set({ isLoading: true, error: null })
    try {
      const response = await apiClient.post('/auth/login', { email, password })
      const { mfa_required, mfa_setup_required, pre_auth_token } = response.data

      if (mfa_required) {
        set({
          isLoading: false,
          mfaRequired: true,
          preAuthToken: pre_auth_token
        })
        return
      }

      // Login completo (MFA não ativo ainda, ou dispositivo confiável)
      await get().checkAuth()
      set({
        isLoading: false,
        mfaSetupRequired: !!mfa_setup_required
      })
    } catch (error: any) {
      const status = error?.response?.status
      let message = error?.response?.data?.detail || 'Erro ao fazer login'

      if (status === 429) {
        const retryAfter = error?.response?.headers?.['retry-after']
        message = retryAfter
          ? `Demasiadas tentativas. Tenta novamente em ${retryAfter}s`
          : 'Demasiadas tentativas. Aguarda um pouco.'
      }

      set({ isLoading: false, error: message })
      throw new Error(message)
    }
  },

  verifyMfa: async (code: string, trustDevice: boolean) => {
    set({ isLoading: true, error: null })
    try {
      const preAuthToken = get().preAuthToken
      if (!preAuthToken) {
        throw new Error('Sessão de login expirada, tenta novamente')
      }

      await apiClient.post('/auth/login/verify-mfa', {
        pre_auth_token: preAuthToken,
        code,
        trust_device: trustDevice
      })

      await get().checkAuth()
      set({ isLoading: false, mfaRequired: false, preAuthToken: null })
    } catch (error: any) {
      const message = error?.response?.data?.detail || 'Código inválido'
      set({ isLoading: false, error: message })
      throw new Error(message)
    }
  },

  register: async (email: string, password: string, passwordConfirm: string) => {
    set({ isLoading: true, error: null })
    try {
      await apiClient.post('/auth/register', {
        email,
        password,
        password_confirm: passwordConfirm
      })
      set({ isLoading: false })
      // Registo não faz login automático — o utilizador entra a seguir e configura o MFA
    } catch (error: any) {
      const message = error?.response?.data?.detail || 'Erro ao criar conta'
      set({ isLoading: false, error: message })
      throw new Error(message)
    }
  },

  logout: async () => {
    try {
      await apiClient.post('/auth/logout')
    } catch (error) {
      console.error('[authStore.logout] Error:', error)
    } finally {
      set({ user: null, isAuthenticated: false, error: null })
    }
  },

  logoutAll: async () => {
    try {
      await apiClient.post('/auth/logout-all')
    } finally {
      set({ user: null, isAuthenticated: false, error: null })
    }
  },

  checkAuth: async () => {
    try {
      const response = await apiClient.get('/auth/me')
      set({ user: response.data.user, isAuthenticated: true })
    } catch (error) {
      set({ user: null, isAuthenticated: false })
    }
  },

  clearError: () => set({ error: null }),

  clearMfaFlow: () => set({ mfaRequired: false, preAuthToken: null, error: null })
}))
