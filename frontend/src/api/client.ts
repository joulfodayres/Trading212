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

    // If 401, the cookie is gone/invalid — redirect to login (avoid loop on the login call itself)
    if (error.response?.status === 401 && !error.config?.url?.includes('/auth/login')) {
      console.warn('[apiClient.response] 401 Unauthorized, redirecting to login')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export default apiClient
