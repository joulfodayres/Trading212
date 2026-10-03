import api from './client'

export const authAPI = {
  login: (email: string, password: string) =>
    api.post('/auth/login', { email, password }),

  register: (email: string, password: string, password_confirm: string) =>
    api.post('/auth/register', { email, password, password_confirm }),

  logout: () => api.post('/auth/logout')
}

export const isinsAPI = {
  getAll: () => api.get('/isins'),

  getById: (id: string) => api.get(`/isins/${id}`),

  create: (isin: string) => api.post('/isins', { isin }),

  update: (id: string, data: any) =>
    api.put(`/isins/${id}`, data),

  delete: (id: string) => api.delete(`/isins/${id}`),

  getDetails: (id: string) => api.get(`/isins/${id}`),

  getTrades: (id: string) => api.get(`/isins/${id}/trades`),

  sync: () => api.get('/isins/sync-from-trading212'),

  toggleAutomation: (id: string) => api.put(`/isins/${id}/automation/toggle`)
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

export const reportsAPI = {
  upload: (files: File[]) => {
    const form = new FormData()
    files.forEach((f) => form.append('files', f))
    return api.post('/reports/upload', form, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  },

  listFiles: () => api.get('/reports/files'),

  summary: () => api.get('/reports/summary')
}

// Item #22 — "Gerir Ordens": manual, non-automated management of T212
// pending orders for a single ISIN. NOT subject to Item #15/#19 trading
// limits (deliberate product decision — manual path).
export const manualOrdersAPI = {
  getScreen: (isin: string) => api.get(`/v1/manual-orders/${encodeURIComponent(isin)}/screen`),

  executeCurrent: (isin: string, ticker: string, data: { edits: any[]; cancels: number[] }) =>
    api.post(`/v1/manual-orders/${encodeURIComponent(isin)}/execute-current`, data, {
      params: { ticker }
    }),

  generate: (data: any) => api.post('/v1/manual-orders/generate', data),

  applyNew: (isin: string, data: any) =>
    api.post(`/v1/manual-orders/${encodeURIComponent(isin)}/apply-new`, data),

  getValidationThresholds: () => api.get('/v1/manual-orders/config/validation-thresholds'),

  updateValidationThresholds: (data: any) =>
    api.put('/v1/manual-orders/config/validation-thresholds', data)
}
