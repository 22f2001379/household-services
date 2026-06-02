import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:5001',
  headers: {
    'Content-Type': 'application/json; charset=utf-8',
  },
  withCredentials: true,
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth_token')
  if (token) {
    config.headers['Authentication-Token'] = token
  }
  return config
})

export function setAuthToken(token) {
  if (token) {
    localStorage.setItem('auth_token', token)
  }
}

export default {
  login(email, password) {
    return api.post('/api/login', { email, password })
  },
  register(registerDetails) {
    return api.post('/api/register', registerDetails)
  },
  getUsers() {
    return api.get('/api/admin/users')
  },
  addServices(data) {
    return api.post('/api/add/services', data)
  },
  getServices() {
    return api.get('/api/get/services')
  },
  updateServices(serviceId, data) {
    return api.put(`/api/update/services/${serviceId}`, data)
  },
  deleteServices(serviceId) {
    return api.delete(`/api/delete/services/${serviceId}`)
  },
  getCustomers() {
    return api.get('/api/get/customers')
  },
  getProfessionals() {
    return api.get('/api/get/professionals')
  },
  deleteUsers(userId) {
    return api.delete(`/api/delete/user/${userId}`)
  },
  updateUser(userId, data) {
    return api.put(`/api/update/user/${userId}`, data)
  },
  addServiceRequest(data) {
    return api.post('/api/add/service-request', data)
  },
  getServiceRequest() {
    return api.get('/api/get/service-request')
  },
  updateServiceRequest(id, data) {
    return api.put(`/api/update/service-request/${id}`, data)
  },
  getProfessionalServiceRequest(id) {
    return api.get(`/api/get/professional-service-request/${id}`)
  },
  updateProfessionalServiceRequest(id, data) {
    return api.put(`/api/update/professional-service-request/${id}`, data)
  },
  addReview(data) {
    return api.post('/api/get/reviews', data)
  },
}
