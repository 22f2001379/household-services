import Vue from 'vue'
import Vuex from 'vuex'
import VueRouter from 'vue-router'
import App from './App.vue'
import AdminDashboard from './components/AdminDashboard.vue'
import Login from './components/Login.vue'
import Register from './components/Register.vue'
import ServiceManagement from './components/ServiceManagement.vue'
import ProfessionalDashboard from './components/ProfessionalDashboard.vue'
import CustomerDashboard from './components/CustomerDashboard.vue'
import { getLocalItem } from './utils/localStorage'

Vue.use(VueRouter)
Vue.use(Vuex)

const store = new Vuex.Store({
  state: {
    userRole: null,
    userName: null,
    userLoggedDetails: null,
    customerDetails: {
      services: [],
      customerRequests: [
      ],
      customers : []
    },
    requests: [],
    professionalDetails: {
      professionals: [],
      professionalRequests: [
        // { serviceId: 0, date: '2025-03-26', customer: 'Jane Smith', location: "New Delhi", rating: '4.3', status: 'requested' },
        // { serviceId: 1, date: '2025-03-16', customer: 'Chinnu Pradhan', location: "Chennai", rating: '3.4', status: 'requested' }
      ]
    }
  },
  mutations: {
    setUserRole(state, role) {
      state.userRole = role
    },
    setUserLoggedDetails(state, details) {
      state.userLoggedDetails = details
    },
    setUserName(state, role) {
      state.userName = role
    },
    setServiceRequests(state, request) {
      state.customerDetails.customerRequests = request
    },
    setProfessionalRequests(state, request) {
      state.professionalDetails.professionalRequests = request
    },
    setRequest(state, requests){
      state.request = requests
    },
    setCustomers(state, customers){
      state.customerDetails.customers = customers || []
    },
    setProfessionals(state, professionals){
      state.professionalDetails.professionals = professionals || []
    }
  }
})

const routes = [
  { path: '/login', component: Login },
  { path: '/register', component: Register },
  { path: '/admin', component: AdminDashboard, meta: { requiresAuth: true } },
  { path: '/service-management', component: ServiceManagement, meta: { requiresAuth: true } },
  { path: '/professional', component: ProfessionalDashboard, meta: { requiresAuth: true } },
  { path: '/customer', component: CustomerDashboard, meta: { requiresAuth: true } },
  { path: '/', redirect: '/login' }
];

const router = new VueRouter({ routes })
// Navigation Guard
router.beforeEach((to, from, next) => {
  const userDetails = getLocalItem('user_details');
  
  // Update Vuex store with user details if available
  if (userDetails) {
    store.commit('setUserRole', userDetails.roles ? userDetails.roles[0] : null);
    store.commit('setUserName', userDetails.email || null);
    store.commit('setUserLoggedDetails', userDetails || null);
  }

  // Check if user is authenticated (has email in userDetails)
  const isAuthenticated = !!userDetails && !!userDetails.email;

  // If the route requires authentication and user is not logged in, redirect to login
  if (to.matched.some(record => record.meta.requiresAuth) && !isAuthenticated) {
    next('/login');
  }
  //  else if (userRole === 'customer' && to.path === '/professional') {
  //   next('/customer');
  // } 
  else {
    next(); // Proceed to the route
  }
});;

new Vue({
  router,
  store,
  render: h => h(App)
}).$mount('#app')