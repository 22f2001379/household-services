<template>
  <div class="container mt-5">
    <navbar />
    <router-view :services="services"></router-view>
  </div>
</template>

<script>
import Navbar from './components/Navbar.vue'

export default {
  name: 'App',
  components: { Navbar },
  computed: {
    adminRequests() {
      return this.$store.state.requests || [] // Assuming Vuex for state management
    }
  },
  data() {
    return {
      services: [
        { name: 'AC Servicing', price: 500, timeRequired: '2 hours' },
        { name: 'Plumbing', price: 300, timeRequired: '1 hour' }
      ]
    }
  }
}
</script>