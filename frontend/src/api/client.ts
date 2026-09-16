import axios, { AxiosInstance } from 'axios'

// Ler base URL do env ou usar padrão
const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'

console.log('[apiClient] Initializing with API_BASE:', API_BASE)

export const apiClient: AxiosInstance = axios.create({
  baseURL: `${API_BASE}/api`,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Interceptor para adicionar token aos headers
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
    console.log('[apiClient.request] Adding Authorization header to request:', config.url)
  }
  console.log('[apiClient.request] Making request to:', config.url, 'method:', config.method)
  return config
})

// Interceptor para error handling
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

    // Se 401, limpar token e redirecionar a login
    if (error.response?.status === 401) {
      console.warn('[apiClient.response] 401 Unauthorized, clearing token and redirecting to login')
      localStorage.removeItem('token')
      delete apiClient.defaults.headers.common['Authorization']
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export default apiClient
