<template>
    <div class="card">
      <div class="card-header">
        <h3>Professional Dashboard</h3>
      </div>
      <div class="card-body">
        <h4>Pending Requests</h4>
        <table class="table">
          <thead>
            <tr>
              <th>Service</th>
              <th>Date</th>
              <th>Customer</th>
              <th>Location</th>
              <th>Rating</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(request, index) in getProfessionalRequests" :key="request.serviceId">
              <td>{{ request.service }}</td>
              <td>{{ new Date(request.date_of_request) }}</td>
              <td>
                <span v-for="cust in customersData" :key="cust.id">
                  {{ cust.id == request.customer_id ? cust.name : '' }}
                </span>
              </td>
              <td>
                <span v-for="cust in customersData" :key="cust.id">
                  {{ cust.id == request.customer_id ? cust.location : '' }}
                </span>
              </td>
              <!-- <td>{{ services[request.serviceId].name }}</td> -->
              <!-- <td>{{ request.customer }}</td>
              <td>{{ request.location }}</td> -->
              <td>{{ request.rating }}</td>
              <td v-if="request.service_status == 'requested'" style="width: 100px;">
                <button style="width: 80px;" class="btn btn-sm btn-success me-2" @click="acceptRequest(request)">Accept</button>
                <button style="width: 80px;" class="btn btn-sm btn-danger mt-2" @click="rejectRequest(request)">Reject</button>
              </td>
              <td  v-if="request.service_status !== 'requested'">
                {{ request.service_status == 'accepted' ? "Accepted" : "Rejected" }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </template>
  
  <script>
  import apis from '../services/api.js'
  export default {
    name: 'ProfessionalDashboard',
    props: {
      services: Array
    },
    mounted(){
      this.allInitialCall()
    },
    computed: {
      getProfessionalRequests() {
        return this.$store.state.professionalDetails.professionalRequests || []
      },
      getProfessionals(){
        return this.$store.state.professionalDetails.professionals || []
      },
      customersData() {
        return this.$store.state.customerDetails.customers || [] // Assuming Vuex for state management
      },
    },
    data() {
      return {
        // requests: [
        //   { serviceId: 0, date: '2025-03-26', customer: 'Jane Smith', status: 'requested' }
        // ]
      }
    },
    methods: {
      allInitialCall(){
        const { id = '' } = this.$store.state.userLoggedDetails || {}
        id && this.professionalRequest(id)
        this.getCustomerDetails()
      },
      async getCustomerDetails(){
        const { data = [] } = await apis.getCustomers();
        data && this.$store.commit("setCustomers", data)
      },
      async professionalRequest(id){
        const {data = []} = await apis.getProfessionalServiceRequest(id);
        data && this.$store.commit('setProfessionalRequests', data)
      },
      async acceptRequest(request) {
        // const req = this.getProfessionalRequests
        // const acceptedRequest = req.map(item => {
        //   if(item.serviceId == requestId) {
        //     return {...item, status: "accepted"}
        //   } else {
        //     return item
        //   }
        // })
        const payload = {...request, service_status: 'accepted'}
        const { data = []} = await apis.updateProfessionalServiceRequest(request.id, payload)
        // data && this.professionalRequest(request.id)
        data && this.allInitialCall()
        console.log("sadflasjdflkasjdf", data)
        // this.$store.commit('setProfessionalRequests', acceptedRequest)
      },
      async rejectRequest(request) {
        // const req = this.getProfessionalRequests
        // const acceptedRequest = req.map(item => {
        //   if(item.serviceId == requestId) {
        //     return {...item, status: "rejected"}
        //   } else {
        //     return item
        //   }
        // })
        // this.$store.commit('setProfessionalRequests', acceptedRequest)
        const payload = {...request, service_status: 'rejected'}
        const { data = []} = await apis.updateProfessionalServiceRequest(request.id, payload)
        // data && this.professionalRequest(request.id)
        data && this.allInitialCall()
        console.log("sadflasjdflkasjdf", data)
        // this.getProfessionalRequests[requestId].status = 'rejected'
        // this.requests.splice(index, 1)
      }
    }
  }
  </script>