<template>
  <nav class="navbar navbar-expand-lg navbar-light bg-light mb-4">
    <div class="container-fluid">
      <a class="navbar-brand" href="#">A-Z Household Services</a>
      <div class="nav-item d-flex align-items-center" v-if="userRole">
        <img
          :src="user_img"
          class="rounded-circle me-2"
          style="height: 20px; width: 20px; margin-top: 4px;"
          alt="User Avatar"
        >
        <span class="nav-link fw-bold">{{ userName || 'User' }}</span>
      </div>
      <button
        class="navbar-toggler"
        type="button"
        data-bs-toggle="collapse"
        data-bs-target="#navbarNav"
      >
        <span class="navbar-toggler-icon"></span>
      </button>
      <div class="collapse navbar-collapse" id="navbarNav">
        <ul class="navbar-nav me-auto">
          <li class="nav-item" v-if="userRole === 'admin'">
            <router-link class="nav-link" to="/admin">Dashboard</router-link>
          </li>
          <li class="nav-item" v-if="userRole === 'professional'">
            <router-link class="nav-link" to="/professional">Dashboard</router-link>
          </li>
          <li class="nav-item" v-if="userRole === 'customer'">
            <router-link class="nav-link" to="/customer">Dashboard</router-link>
          </li>
        </ul>
        <ul class="navbar-nav ms-auto">
          <li class="nav-item" v-if="!userRole">
            <router-link class="nav-link" to="/login">Login</router-link>
          </li>
          <li class="nav-item" v-if="!userRole">
            <router-link class="nav-link" to="/register">Register</router-link>
          </li>
          <li class="nav-item" v-if="userRole">
            <button class="nav-link btn" @click="logout">Logout</button>
          </li>
        </ul>
      </div>
    </div>
  </nav>
</template>

<script>
import USER_IMG from "../assets/logo1.png"
import { clearLocalStorage } from '../utils/localStorage.js'

export default {
  name: 'Navbar',
  computed: {
    userRole() {
      return this.$store.state.userRole || null; // Assuming Vuex for state management
    },
    userName() {
      return this.$store.state.userName || null; // Assuming userName is stored in Vuex
    }
  },
  data() {
    return {
      user_img: USER_IMG
    }
  },
  methods: {
    logout() {
      this.$store.commit('setUserRole', null);
      this.$store.commit('setUserName', null); // Clear userName on logout
      clearLocalStorage()
      this.$router.push('/login');
    }
  }
};
</script>

<style scoped>
.rounded-circle {
  width: 40px;
  height: 40px;
  object-fit: cover;
}

.fw-bold {
  font-weight: bold;
}
</style>