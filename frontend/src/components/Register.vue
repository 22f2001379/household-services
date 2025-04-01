<template>
  <div class="card">
    <div class="card-header">
      <h3>Register</h3>
    </div>
    <div class="card-body">
      <form @submit.prevent="handleRegister">
        <div class="mb-3">
          <label for="name" class="form-label">Name</label>
          <input type="text" class="form-control" id="name" v-model="name" required>
        </div>
        <div class="mb-3">
          <label for="email" class="form-label">Email</label>
          <input type="email" class="form-control" id="email" v-model="email" required>
        </div>
        <div class="mb-3">
          <label for="password" class="form-label">Password</label>
          <input type="password" class="form-control" id="password" v-model="password" required>
        </div>
        <div class="mb-3">
          <label for="location" class="form-label">Location</label>
          <input type="text" class="form-control" id="location" v-model="location" required>
        </div>
        <div class="mb-3" v-if="role === 'professional'">
          <label for="experience" class="form-label">Experience (years)</label>
          <input type="number" class="form-control" id="experience" v-model="experience" required>
        </div>
        <div class="mb-3" v-if="role === 'professional'">
          <label for="role" class="form-label">Service</label>
          <select class="form-control" id="role" v-model="service" required>
            <option v-for="(service, index) in services" :key="index" :value="service.name">
              {{ service.name }}
            </option>
          </select>
        </div>
        <div class="mb-3">
          <label for="role" class="form-label">Role</label>
          <select class="form-control" id="role" v-model="role" required>
            <option value="customer">Customer</option>
            <option value="professional">Service Professional</option>
          </select>
        </div>
        <button type="submit" class="btn btn-primary" :disabled="loading">
          <span v-if="loading" class="spinner-border spinner-border-sm" role="status"></span>
          {{ loading ? 'Registering...' : 'Register' }}
        </button>
        <div v-if="error" class="alert alert-danger mt-3">
          {{ error }}
        </div>
        <div v-if="success" class="alert alert-success mt-3">
          Registration successful! Redirecting...
        </div>
      </form>
    </div>
  </div>
</template>

<script>
import api from '../services/api'

export default {
  name: 'Register',
  data() {
    return {
      name: '',
      email: '',
      password: '',
      location: '',
      experience: '',
      role: 'customer',
      service: '',
      loading: false,
      error: '',
      success: false,
      services: []
    }
  },
  // computed: {
  //   servicesData() {
  //     // console.log("sdkfa", this.$store.state.customerDetails.customerRequests)
  //     return this.$store.state.customerDetails.customers || [] // Assuming Vuex for state management
  //   },
  // },
  mounted(){
    this.fetchServices();
  },
  methods: {
    async handleRegister() {
      this.loading = true
      this.error = ''
      this.success = false

      try {
        const userData = {
          name: this.name,
          email: this.email,
          password: this.password,
          location: this.location,
          service: this.service,
          role: this.role,
          ...(this.role === 'professional' && { experience: this.experience })
        }

        // Call your Flask register endpoint
        const response = await api.register(userData)

        // Handle successful registration
        this.success = true
        
        // Store user data if needed
        localStorage.setItem('auth_token', response.data.token)
        
        // Redirect after short delay
        setTimeout(() => {
          this.$router.push(`/login`)
        }, 1500)
      } catch (error) {
        console.error('Registration error:', error)
        this.error = error.response?.data?.message || 'Registration failed. Please try again.'
      } finally {
        this.loading = false
      }
    },
    async fetchServices() {
      try {
        const response = await api.getServices();
        // Assuming the API returns an object with a 'data' property containing the services array
        const servicesData = response.data || [];
        this.services = servicesData; // Assign to local data property, not prop
      } catch (error) {
        console.error('Error fetching services:', error);
      }
    },
  }
}
</script>

<style scoped>
.card {
  max-width: 500px;
  margin: 0 auto;
}

.spinner-border {
  margin-right: 5px;
}
</style>