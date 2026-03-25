import axios from 'axios'

const api = axios.create({
  baseURL: '/api/v1',
})

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// Response interceptor to handle errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export default api

// Config API
export const configApi = {
  getAll: () => api.get('/config/'),
  getByCategory: (category) => api.get(`/config/${category}`),
  get: (category, key) => api.get(`/config/${category}/${key}`),
  create: (data) => api.post('/config/', data),
  update: (category, key, data) => api.put(`/config/${category}/${key}`, data),
  delete: (category, key) => api.delete(`/config/${category}/${key}`),
  bulkUpdate: (configs) => api.post('/config/bulk', { configs }),
  reset: (category) => api.post('/config/reset', null, { params: category ? { category } : {} }),
}