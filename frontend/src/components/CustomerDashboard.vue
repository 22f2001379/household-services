<template>
  <div>
    <search-services
      :professionals="professionals"
      @search="handleSearch"
      @request-created="handleRequestCreated"
    />
    <service-request :requests="requestsFromStore" :professionals="professionals" @close-request="handleCloseRequest" />
  </div>
</template>

<script>
import SearchServices from "./SearchServices.vue";
import ServiceRequest from "./ServiceRequest.vue";
import apis from "../services/api.js"

export default {
  name: "CustomerDashboard",
  components: { SearchServices, ServiceRequest },
  props: {
    services: Array, // Still passed from App.vue, but we'll derive professionals from it
  },
  mounted() {
    // Fetch services when the component is mounted
    // this.getCustomerDetails()
    this.getServiceRequest()
    this.getProfessionalsDetails()
  },
  computed: {
    requestsFromStore() {
      let currentCustRequest = this.$store.state.customerDetails.customerRequests || []

const payload = currentCustRequest.filter(res => res.customer_id == this.userLoggedDetails.id)

      // return this.$store.state.customerDetails.customerRequests || [] 
      return payload || null
    },
    professionals() {
      return this.$store.state.professionalDetails.professionals || [] 
    },
    userLoggedDetails() {
      console.log("asdfasdfsdf", this.$store.state.userLoggedDetails)
      return this.$store.state.userLoggedDetails || null; // Assuming userName is stored in Vuex
    }
  },
  data() {
    return {
      // professionals: [],
      // requests: [],
    };
  },
  // mounted(){
  // },
  methods: {
    async getProfessionalsDetails(){
      const {data = []} = await apis.getProfessionals()
      data && this.$store.commit("setProfessionals", data)
    },
    async getServiceRequest(){
      const {data = []} = await apis.getServiceRequest()
      console.log("data9090900909", data)
      data && this.$store.commit("setServiceRequests", data)
    },
    handleSearch(results) {
      console.log("Search results:", results);
    },
    handleRequestCreated(request) {

      this.$store.commit('setServiceRequests', [...this.requestsFromStore, request])

      // this.requests.push(asdfsdrequest);
    },
    handleCloseRequest(index) {
      this.requests[index].status = "closed";
    },
  },
};
</script>

