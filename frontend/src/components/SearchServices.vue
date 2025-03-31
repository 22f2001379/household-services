<template>
  <div>
    <div class="card mb-4">
      <div class="card-header">
        <h3>Search Services</h3>
      </div>
      <div class="card-body">
        <div class="input-group mb-3">
          <input
            v-model="searchQuery"
            class="form-control"
            placeholder="Search by service name or location"
          />
          <button class="btn btn-primary" @click="search">Search</button>
        </div>
        <ul class="list-group">
          <li
            v-for="(professional, index) in filteredProfessionals"
            :key="index"
            class="list-group-item d-flex justify-content-between align-items-center"
          >
            <div>
              <strong>{{ professional.name }}</strong><br />
              Service: {{ professional.service }}<br />
              Location: {{ professional.location }}<br />
              Experience: {{ professional.experience }}<br />
              Review: {{ professional.review }} stars
            </div>
            <button
              class="btn btn-sm btn-primary"
              @click="openRequestModal(professional ,index)"
            >
              Request
            </button>
          </li>
        </ul>
      </div>
    </div>

    <!-- Modal for Vue 2 with Bootstrap -->
    <div
      class="modal fade"
      :class="{ show: isModalOpen, 'd-block': isModalOpen }"
      tabindex="-1"
      role="dialog"
      aria-labelledby="requestModalLabel"
      aria-hidden="true"
    >
      <div class="modal-dialog" role="document">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title" id="requestModalLabel">
              Request {{ selectedProfessional ? selectedProfessional.name : '' }}
            </h5>
            <button
              type="button"
              class="close"
              aria-label="Close"
              @click="closeModal"
            >
              <span aria-hidden="true">&times;</span>
            </button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="submitRequest">
              <div class="form-group">
                <label class="form-label">Date of Request</label>
                <input
                  v-model="newRequest.dateOfRequest"
                  type="date"
                  class="form-control"
                  required
                />
              </div>
              <div class="form-group">
                <label class="form-label">Date of Completion</label>
                <input
                  v-model="newRequest.dateOfCompletion"
                  type="date"
                  class="form-control"
                  required
                />
              </div>
              <div class="form-group">
                <label class="form-label">Remarks</label>
                <textarea
                  v-model="newRequest.remarks"
                  class="form-control"
                  rows="3"
                ></textarea>
              </div>
              <button type="submit" class="btn btn-primary">Submit</button>
            </form>
          </div>
        </div>
      </div>
    </div>
    <div
      class="modal-backdrop fade"
      :class="{ show: isModalOpen }"
      v-if="isModalOpen"
      @click="closeModal"
    ></div>
  </div>
</template>

<script>
import apis from '../services/api.js'
export default {
  name: 'SearchServices',
  props: {
    professionals: Array,
  },
  // computed: {
  //   professionalsFromStore() {
  //     return this.$store.state.professionals || [] // Assuming Vuex for state management
  //   }
  // },
  data() {
    return {
      searchQuery: '',
      isModalOpen: false,
      newRequest: {
        professionalId: null,
        dateOfRequest: '',
        dateOfCompletion: '',
        remarks: '',
        name: '',
        service: "",
        location: '',
        customerId: ''
      },
      selectedProfessional: null,
    };
  },
  // mounted() {
  //   this.getServiceRequest()
  // },
  computed: {
    filteredProfessionals() {
      console.log("this.professional", this.professionals)
      if (!this.searchQuery) return this.professionals;
      const query = this.searchQuery.toLowerCase();
      return this.professionals.filter(
        (pro) =>
          pro.service.toLowerCase().includes(query) ||
          pro.location.toLowerCase().includes(query)
      );
    },
    userLoggedDetails() {
      console.log("asdfasdfsdf", this.$store.state.userLoggedDetails)
      return this.$store.state.userLoggedDetails || null; // Assuming userName is stored in Vuex
    }
    // professionals() {
    //   return this.$store.state.professionalDetails.professionals || [] // Assuming Vuex for state management
    // }
  },
  methods: {
    search() {
      this.$emit('search', this.filteredProfessionals);
    },
    async getServiceRequest(){
      const {data = []} = await apis.getServiceRequest()
      console.log("data9090900909", data)
      data && this.$store.commit("setServiceRequests", data)
    },
    openRequestModal(data, index) {
      this.selectedProfessional = this.filteredProfessionals[index];
      this.newRequest.professionalId = data.id;
      this.newRequest.location = data.location;
      this.newRequest.name = data.name;
      this.newRequest.service = data.service;
      this.newRequest.customerId = this.userLoggedDetails.id;
      this.isModalOpen = true;
    },
    closeModal() {
      this.isModalOpen = false;
    },
    async submitRequest() {
      const request = {
        professionalId: this.newRequest.professionalId,
        dateOfRequest: this.newRequest.dateOfRequest,
        dateOfCompletion: this.newRequest.dateOfCompletion,
        remarks: this.newRequest.remarks,
        name: this.newRequest.name,
        location: this.newRequest.location,
        service: this.newRequest.service,
        customerId: this.userLoggedDetails.id,
        status: 'requested',
      };
      // this.$emit('request-created', request);
      this.newRequest = {
        professionalId: null,
        dateOfRequest: '',
        dateOfCompletion: '',
        service: "",
        remarks: '',
      };
      // this.isModalOpen = false;

      console.log("request", request)
      const response = await apis.addServiceRequest(request);
      response && this.getServiceRequest()
      response && this.closeModal();
      console.log("service request", response)
      
    },
  },
};
</script>

<style scoped>
/* Custom styles to ensure modal works correctly */
.modal {
  background-color: rgba(0, 0, 0, 0.5);
}
.modal.show {
  display: block;
}
.modal-backdrop {
  position: fixed;
  top: 0;
  bottom: 0;
  left: 0;
  right: 0;
  background-color: rgba(0, 0, 0, 0.5);
  z-index: 1040;
}
.modal {
  z-index: 1050;
}
</style>