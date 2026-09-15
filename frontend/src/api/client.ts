import axios, { AxiosInstance } from 'axios'

// Ler base URL do env ou usar padrão
const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'

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
  }
  return config
})

// Interceptor para error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    // Se 401, limpar token e redirecionar a login
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      delete apiClient.defaults.headers.common['Authorization']
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export default apiClient
