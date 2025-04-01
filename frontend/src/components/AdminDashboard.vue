<template>
  <div>
    <div class="card mb-4">
      <div class="card-header">
        <h3>Admin Dashboard</h3>
      </div>
      <div class="card-body">
        <!-- Users Table -->
        <!-- <h4>Users</h4> -->
        <!-- <table class="table mb-4">
          <thead>
            <tr>
              <th>Name</th>
              <th>Role</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(user, index) in users" :key="index">
              <td>{{ user.name }}</td>
              <td>{{ user.role }}</td>
              <td>{{ user.status }}</td>
              <td>
                <button class="btn btn-sm btn-danger" @click="blockUser(user)">Block</button>
                <button
                  class="btn btn-sm btn-success"
                  @click="approveUser(user)"
                  v-if="user.role === 'professional' && user.status === 'pending'"
                >Approve</button>
              </td>
            </tr>
          </tbody>
        </table> -->

        <!-- Accordions for Requests -->
        <div class="accordion" id="requestsAccordion">
          <!-- Professional Requests Accordion -->
          <div class="accordion-item">
            <h2 class="accordion-header" id="professionalHeading">
              <button
                class="accordion-button"
                type="button"
                data-bs-toggle="collapse"
                data-bs-target="#professionalCollapse"
                aria-expanded="true"
                aria-controls="professionalCollapse"
              >
                Professionals List
              </button>
            </h2>
            <div
              id="professionalCollapse"
              class="accordion-collapse collapse show"
              aria-labelledby="professionalHeading"
              data-bs-parent="#requestsAccordion"
            >
              <div class="accordion-body">
                <table class="table">
                  <thead>
                    <tr>
                      <th>Name</th>
                      <th>Service</th>
                      <th>Location</th>
                      <th>Experience</th>
                      <th>Status</th>
                      <th>Rating</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="(details, index) in professionalsData" :key="index">
                      <td>{{ details.name }}</td>
                      <td>{{ details.service }}</td>
                      <td>{{ details.location }}</td>
                      <td>
                        {{ details.experience }}
                      </td>
                      <td>{{ !details.approved ? 'Blocked' : 'Approved' }}</td>
                      <td v-if="details.rating">{{ details.rating }}</td>
                      <td v-else>Not yet</td>
                      <td style="width: 100px;">
                        <button 
                          style="width: 80px;" 
                          class="btn btn-sm btn-danger" 
                          @click="deleteRequest('professional', details.id)"
                          title="Delete"
                        >
                          Delete
                          <i class="fas fa-trash"></i>
                        </button>
                        <button 
                          style="width: 80px;" 
                          class="btn btn-sm btn-success mt-2" 
                          @click="approveUser('professional', details.id, details)"
                          :title="details.approved ? 'Block' : 'Approve'"
                        >
                          {{ details.approved ? "Block" : "Approve" }}
                          <i class="fas fa-check"></i>
                        </button>
                        <!-- <button 
                          style="width: 80px;" 
                          class="btn btn-sm btn-warning mt-2" 
                          @click="blockUser('professional', details.id)"
                          title="Block"
                        >
                          Block
                          <i class="fas fa-ban"></i>
                        </button> -->
                      </td>
                    </tr>
                  </tbody>
                  <div v-if="!professionalsData" style="display: flex; justify-content: center; width: 100%;">No data</div>
                </table>
              </div>
            </div>
          </div>

          <!-- Customer Requests Accordion -->
          <div class="accordion-item">
            <h2 class="accordion-header" id="customerHeading">
              <button
                class="accordion-button collapsed"
                type="button"
                data-bs-toggle="collapse"
                data-bs-target="#customerCollapse"
                aria-expanded="false"
                aria-controls="customerCollapse"
              >
                Customer Requests
              </button>
            </h2>
            <div
              id="customerCollapse"
              class="accordion-collapse collapse"
              aria-labelledby="customerHeading"
              data-bs-parent="#requestsAccordion"
            >
              <div class="accordion-body">
                <table class="table">
                  <thead>
                    <tr>
                      <th>Name</th>
                      <th>Email</th>
                      <th>Location</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="(customer, index) in customersData" :key="index">
                      <td>{{ customer.name }}</td>
                      <td>{{ customer.email }}</td>
                      <td>{{ customer.location }}</td>
                      <td style="width: 100px; ">
                          <button style="width: 80px;" class="btn btn-sm btn-danger" @click="deleteRequest('customer', customer.id)"">Delete</button>
                          <!-- <button style="width: 80px;" class="btn btn-sm btn-success mt-2" @click="approveUser('customer', index)"">Approve</button> -->
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>

        <!-- Manage Services Button -->
        <button class="btn btn-primary mt-3" @click="openServiceModal">Manage Services</button>
      </div>
    </div>

    <!-- Manage Services Modal -->
    <div
      class="modal fade"
      :class="{ show: isServiceModalOpen, 'd-block': isServiceModalOpen }"
      tabindex="-1"
      role="dialog"
      aria-labelledby="serviceModalLabel"
      aria-hidden="true"
    >
      <div class="modal-dialog modal-lg" role="document">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title" id="serviceModalLabel">Manage Services</h5>
            <button type="button" class="close" @click="closeServiceModal">
              <span aria-hidden="true">&times;</span>
            </button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="submitRequest" class="mb-4">
              <div class="row" style="gap: 8px;">
                <div class="col-md-3">
                  <input v-model="newService.name" class="form-control" placeholder="Name" required>
                </div>
                <div class="col-md-3">
                  <input v-model.number="newService.price" type="number" class="form-control" placeholder="Price" required>
                </div>
                <div class="col-md-3">
                  <input v-model="newService.timeRequired" class="form-control" placeholder="Time Required" required>
                </div>
                <div class="col-md-3">
                  <button type="submit" class="btn btn-primary">{{ isServiceUpdate ? "Update Service " : "Add Service"}}</button>
                </div>
              </div>
            </form>
            <table class="table">
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Price</th>
                  <th>Time</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(service, index) in services" :key="index">
                  <td>{{ service.name || "" }}</td>
                  <td>{{ service.price || "" }}</td>
                  <td>{{ service.timeRequired || "" }}</td>
                  <td style="display: flex; gap: 4px;">
                    <button class="btn btn-sm btn-warning" @click="editService(index)">Edit</button>
                    <button class="btn btn-sm btn-danger" @click="deleteService(service.id)">Delete</button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
    <div
      class="modal-backdrop fade"
      :class="{ show: isServiceModalOpen }"
      v-if="isServiceModalOpen"
      @click="closeServiceModal"
    ></div>
  </div>
</template>

<script>
import apis from "../services/api.js"
export default {
  name: 'AdminDashboard',
  props: {
  },
  computed: {
    professionalRequests() {
        return this.$store.state.professionalDetails.professionalRequests || []
      },
    professionalsData() {
        return this.$store.state.professionalDetails.professionals || []
      },
    customerRequests() {
      // console.log("sdkfa", this.$store.state.customerDetails.customerRequests)
      return this.$store.state.customerDetails.customerRequests || [] // Assuming Vuex for state management
    },
    customersData() {
      // console.log("sdkfa", this.$store.state.customerDetails.customerRequests)
      return this.$store.state.customerDetails.customers || [] // Assuming Vuex for state management
    },
  },
  data() {
    return {
      users: [
        { name: 'John Doe', role: 'professional', status: 'pending' },
        { name: 'Jane Smith', role: 'customer', status: 'active' }
      ],
      services: [{
        "description": "",
        "id": "",
        "name": "",
        "price": "",
        "timeRequired": "",
        "user_id": null
      }],
      isServiceUpdate: false,
      // professionalRequests: [
      //   { serviceId: 0, date: '2025-03-26', customer: 'Jane Smith', status: 'requested' }
      // ],
      // customerRequests: [
      //   { serviceId: 1, date: '2025-03-27', customer: 'Jane Smith', status: 'requested' }
      // ],
      isServiceModalOpen: false,
      newService: { name: '', price: 0, timeRequired: '' }
    };
  },
  mounted() {
    // Fetch services when the component is mounted
    this.getCustomerDetails()
    this.getProfessionalsDetails()
  },
  methods: {
    async getCustomerDetails(){
      const { data = [] } = await apis.getCustomers();
      data && this.$store.commit("setCustomers", data)
    },
    async getProfessionalsDetails(){
      const {data = []} = await apis.getProfessionals()
      data && this.$store.commit("setProfessionals", data)
    },
    blockUser(user) {
      user.status = 'blocked';
    },
    // approveUser(user) {
    //   user.status = 'active';
    // },
    async deleteRequest(type, id) {
      const res = await apis.deleteUsers(id)
      if (type === 'professional') {
        this.getProfessionalsDetails()
      } else {
        this.getCustomerDetails()
      }
    },
    async approveUser(type, id, data) {
      console.log("data", data)
      if (type === 'professional') {
        const res = await apis.updateUser(id, {...data, approved: !data.approved})
        res && this.getProfessionalsDetails()
      // } else {
        // this.getCustomerDetails()
      }
    },
    openServiceModal() {
      this.isServiceModalOpen = true;
      this.fetchServices();
    },
    closeServiceModal() {
      this.isServiceModalOpen = false;
      this.isServiceUpdate = false;
    },
    async submitRequest(serviceId, data){
      this.isServiceUpdate ? this.updateServices(serviceId, data) : this.addService()
    }, 
    async addService() {
      // this.services.push({ ...this.newService });
      const response = await apis.addServices({...this.newService})
      const {service = {}} = response.data || {}
      if(Object.keys(service).length > 0){
        this.fetchServices();
        this.newService = {}
      }
    },
    async updateServices() {
      const { id = "" } = this.newService || {}
      try {
        const response = await apis.updateServices(id, this.newService);
        // Assuming the API returns an object with a 'data' property containing the services array
        const servicesData = response.data || [];
        // this.services = servicesData;
        if(Object.keys(servicesData)){
          this.fetchServices();
        }
        console.log("update services", servicesData)
        // Update local state with fetched services
        // this.localServices = servicesData;
        // If you want to update the prop (though props are typically read-only),
        // you might need to emit an event to the parent instead
        // this.$emit('update:services', servicesData);
      } catch (error) {
        console.error('Error fetching services:', error);
      }
    },
    async fetchServices() {
      try {
        const response = await apis.getServices();
        // Assuming the API returns an object with a 'data' property containing the services array
        const servicesData = response.data || [];
        this.services = servicesData; // Assign to local data property, not prop
      } catch (error) {
        console.error('Error fetching services:', error);
      }
    },
    editService(index) {
      this.newService = { ...this.services[index] };
      this.isServiceUpdate = true
      // this.deleteService(index);
    },
    async deleteService(id) {
      // this.services.splice(index, 1);
      try {
        const response = await apis.deleteServices(id)
        const deleteRes = response.data.service_id
        console.log("response", response);
        if(deleteRes){
          this.fetchServices();
        }
      } catch (error){

      }
    }
  }
};
</script>

<style scoped>
/* Modal styles */
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