import axios from 'axios'

const api = axios.create({
  baseURL: 'http://127.0.0.1:5001',  // Flask backend URL
  headers: {
    'Content-Type': 'application/json; charset=utf-8',
  },
  // type: "POST",
  // data: {},
  // dataType: 'json',
  // xhrFields: {
  //    withCredentials: true
  // },
  // crossDomain: true,
  // contentType: 'application/json; charset=utf-8'
  withCredentials: true  // Enable credentials for authenticated requests
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

export default {
  login(email, password) {
    return api.post('/api/login', { email, password })
  },
  register(registerDetails) {
    // console.log("register", email, password, role)
    return api.post('/api/register', registerDetails)
  },
  getUsers() {
    return api.get('/api/admin/users')
  },
  approveProfessional(userId) {
    return api.put(`/api/admin/professionals/${userId}/approve`)
  },
  // getServices() {
  //   return api.get('/api/admin/services')  // Updated to match admin endpoint
  // },
  createService(data) {
    return api.post('/api/admin/services', data)
  },
  getCustomerRequests() {
    return api.get('/api/customer/service-requests')
  },
  createServiceRequest(data) {
    return api.post('/api/customer/service-requests', data)
  },
  closeServiceRequest(requestId) {
    return api.put(`/api/customer/service-requests/${requestId}/close`)
  },
  searchServices(searchParams) {
    return api.get('/api/services/search', {
      params: {
        location: searchParams.location,
        name: searchParams.serviceName
      }
    })
  },
  getProfessionals() {
    return api.get('/api/professionals/approved')  // Ensure this endpoint exists
  },
  getProfessionalDetails(professionalId) {
    return api.get(`/api/professionals/${professionalId}`)
  },
  getAllServices() {
    return api.get('/api/admin/services')  // Updated to match admin endpoint
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
  deleteUsers(userId){
    return api.delete(`/api/delete/user/${userId}`)
  },
  updateUser(userId, data){
    return api.put(`/api/update/user/${userId}`, data)
  },
  addServiceRequest(data){
    return api.post('/api/add/service-request', data)
  },
  getServiceRequest(){
    return api.get('/api/get/service-request')
  },
  updateServiceRequest(id, data){
    return api.put(`/api/update/service-request/${id}`, data)
  },
  getProfessionalServiceRequest(id){
    return api.get(`/api/get/professional-service-request/${id}`)
  },
  updateProfessionalServiceRequest(id, data){
    return api.put(`/api/update/professional-service-request/${id}`, data)
  },
  addReview(data){
    return api.post('/api/get/reviews', data)
  }
}


const dumm = { 
  'email': 
  { 
    'name': 'Sagar Pradhan', 
    'email': 'sagar.pradhan583@gmail.com', 
    'password': 'asdkjflasdf', 'location': 
    'askdjflsjdf', 
    'role': 'customer' 
  } 
}