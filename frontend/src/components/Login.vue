<template>
  <div class="card">
    <div class="card-header">
      <h3>Login</h3>
    </div>
    <div class="card-body">
      <form @submit.prevent="handleLogin">
        <div class="mb-3">
          <label for="email" class="form-label">Email</label>
          <input type="email" class="form-control" id="email" v-model="email" required>
        </div>
        <div class="mb-3">
          <label for="password" class="form-label">Password</label>
          <input type="password" class="form-control" id="password" v-model="password" required>
        </div>
        <button type="submit" class="btn btn-primary" :disabled="loading">
          <span v-if="loading" class="spinner-border spinner-border-sm" role="status"></span>
          {{ loading ? 'Logging in...' : 'Login' }}
        </button>
        <div v-if="error" class="alert alert-danger mt-3">
          {{ error }}
        </div>
      </form>
    </div>
  </div>
</template>

<script>
import api from '../services/api.js' // Import your API service
import { setLocalItem } from '../utils/localStorage.js'

export default {
  name: 'Login',
  data() {
    return {
      email: '',
      password: '',
      loading: false,
      error: ''
    }
  },
  methods: {
    async handleLogin() {
      this.loading = true
      this.error = ''
      
      try {
        // Make API call to your Flask login endpoint
        const response = await api.login(this.email, this.password)
        
        // Store the authentication token
        // localStorage.setItem('auth_token', response.data.token)
        
        // Determine user role and redirect
        const userRoles = response.data.user.roles || []
        const userDetails = response.data.user || {}
        userRoles && setLocalItem('user_details', response.data.user)
        userDetails?.email && this.$store.commit('setUserRole', userDetails.roles[0]);
        userDetails?.email && this.$store.commit('setUserName', userDetails.email); // Clear userName on logout
        let redirectPath = '/'
        if (userRoles.includes('admin')) {
          redirectPath = '/admin'
        } else if (userRoles.includes('professional')) {
          redirectPath = '/professional'
        } else if (userRoles.includes('customer')) {
          redirectPath = '/customer'
        }
        
        this.$router.push(redirectPath)
      } catch (res) {
        console.error('Login error:', res)
        this.error = res.response?.data?.error || 'Login failed. Please check your credentials.'
      } finally {
        this.loading = false
      }
    }
  }
}
</script>

<style scoped>
.card {
  max-width: 400px;
  margin: 0 auto;
}

.spinner-border {
  margin-right: 5px;
}
</style>