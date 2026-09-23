import axios, { AxiosInstance } from 'axios'

// Read base URL from env or use default
const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'

console.log('[apiClient] Initializing with API_BASE:', API_BASE)

// Token now lives in an httpOnly cookie (Item #12) — the browser sends it
// automatically with withCredentials, JS never touches it (XSS protection).
export const apiClient: AxiosInstance = axios.create({
  baseURL: `${API_BASE}/api`,
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json'
  }
})

apiClient.interceptors.request.use((config) => {
  console.log('[apiClient.request] Making request to:', config.url, 'method:', config.method)
  return config
})

// Endpoints where a 401 is an *expected* possible outcome, not a sign that
// an established session died mid-use — never react to a 401 on these.
const AUTH_FLOW_PATHS = ['/auth/login', '/auth/login/verify-mfa', '/auth/me', '/auth/register']

apiClient.interceptors.response.use(
  (response) => {
    console.log('[apiClient.response] Received response from:', response.config.url, 'status:', response.status)
    return response
  },
  (error) => {
    console.error('[apiClient.response] Error response:', {
      url: error.config?.url,
      status: error.response?.status,
      detail: error.response?.data?.detail,
      message: error.message
    })

    const isAuthFlowCall = AUTH_FLOW_PATHS.some((path) => error.config?.url?.includes(path))

    // A 401 on any *other* protected endpoint means an established session
    // died mid-use (expired token, or a killswitch fired elsewhere) — drop
    // the local auth state so React Router (App.tsx) naturally routes back
    // to /login on next render. No window.location reload here: that caused
    // an infinite loop when /auth/me legitimately returns 401 on first load
    // (no session yet is the normal case, not an error to react to).
    if (error.response?.status === 401 && !isAuthFlowCall) {
      console.warn('[apiClient.response] 401 on a protected call — clearing session state')
      import('../stores/authStore').then(({ useAuthStore }) => {
        useAuthStore.setState({ user: null, isAuthenticated: false })
      })
    }

    return Promise.reject(error)
  }
)

export default apiClient
