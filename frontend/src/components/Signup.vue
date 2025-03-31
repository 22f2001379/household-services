<template>
    <div class="card">
      <div class="card-header">
        <h3>Signup</h3>
      </div>
      <div class="card-body">
        <form @submit.prevent="handleSignup">
          <div class="mb-3">
            <label for="username" class="form-label">Username</label>
            <input 
              type="text" 
              class="form-control" 
              id="username" 
              v-model="username"
              required
            >
          </div>
          <div class="mb-3">
            <label for="email" class="form-label">Email</label>
            <input 
              type="email" 
              class="form-control" 
              id="email" 
              v-model="email"
              required
            >
          </div>
          <div class="mb-3">
            <label for="password" class="form-label">Password</label>
            <input 
              type="password" 
              class="form-control" 
              id="password" 
              v-model="password"
              required
            >
          </div>
          <button type="submit" class="btn btn-primary">Signup</button>
        </form>
      </div>
    </div>
  </template>
  
  <script>
  export default {
    name: 'Signup',
    data() {
      return {
        username: '',
        email: '',
        password: ''
      }
    },
    methods: {
      handleSignup() {
        // Add your signup logic here
        console.log('Signup attempt:', {
          username: this.username,
          email: this.email,
          password: this.password
        })
      }
    }
  }
  </script>
  
  <style scoped>
  .card {
    max-width: 400px;
    margin: 0 auto;
  }
  </style>