import api from './client'

export const authAPI = {
  login: (email: string, password: string) =>
    api.post('/auth/login', { email, password }),

  register: (email: string, password: string) =>
    api.post('/auth/register', { email, password }),

  logout: () => {
    localStorage.removeItem('token')
  }
}

export const isinsAPI = {
  getAll: () => api.get('/isins'),

  getById: (id: string) => api.get(`/isins/${id}`),

  create: (isin: string) => api.post('/isins', { isin }),

  update: (id: string, data: any) =>
    api.put(`/isins/${id}`, data),

  delete: (id: string) => api.delete(`/isins/${id}`),

  getDetails: (id: string) => api.get(`/isins/${id}/details`)
}

export const configAPI = {
  getConfig: () => api.get('/config'),

  updateConfig: (data: any) => api.put('/config', data),

  testConnection: () => api.post('/config/test')
}

export const automationAPI = {
  toggle: (isinId: string, enabled: boolean) =>
    api.put(`/isins/${isinId}/automation/toggle`, { enabled })
}
