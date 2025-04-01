<template>
  <div>
  <div class="card">
    <div class="card-header">
      <h3>Service Requests</h3>
    </div>
    <div class="card-body">
      <table class="table table-responsive">
        <thead>
          <tr>
            <th>Professional</th>
            <th>Service</th>
            <th>Location</th>
            <th>Date of Request</th>
            <th>Date of Completion</th>
            <th>Status</th>
            <th>Remarks</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(request, index) in requests" :key="index">
            <td>
              <span v-for="pro in professionals" :key="pro.id">
                {{ pro.id == request.professional_id ? pro.name : '' }}
              </span>
            </td>
            <td>
              <span v-for="pro in professionals" :key="pro.id">
                {{ pro.id === request.professional_id ? pro.service : '' }}
              </span>
            </td>
            <td>
              <span v-for="pro in professionals" :key="pro.id">
                {{ pro.id === request.professional_id ? pro.location : '' }}
              </span>
            </td>
            <td>{{ request.date_of_request }}</td>
            <td>{{ request.date_of_completion }}</td>
            <td>{{ request.service_status }}</td>
            <td>{{ request.remarks || '-' }}</td>
            <td>
              <button
                class="btn btn-sm btn-success"
                @click="confirmCloseRequest(request)"
                v-if="request.service_status !== 'closed'"
              >
                Close
              </button>
              <span v-else>Closed</span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>

  <!-- Rating Modal -->
  <div v-if="showModal" class="modal fade show d-block" tabindex="-1">
    <div class="modal-dialog">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">Rate Your Experience</h5>
          <button type="button" class="btn-close" @click="closeModal"></button>
        </div>
        <div class="modal-body text-center">
          <p>Please rate your experience (0 to 5 stars)</p>
          <div>
            <span v-for="star in 5" :key="star" @click="rating = star" class="star" :class="{ 'selected': rating >= star }">★</span>
          </div>
        </div>
        <div style="width: 100%; height: 100px; display: flex; justify-content: center;">
          <!-- <textarea style="width: 100%; margin: 8px;" v-model="reviewText"></textarea> -->
        </div>
        <div class="modal-footer">
          <button class="btn btn-secondary" @click="closeModal">Cancel</button>
          <button class="btn btn-primary" @click="submitRating">Submit</button>
        </div>
      </div>
    </div>
  </div>
  <div v-if="showModal" class="modal-backdrop fade show"></div>
</div>
</template>

<script>
import apis from '../services/api.js';
export default {
  name: "ServiceRequest",
  props: {
    professionals: Array,
    requests: Array,
  },
  data() {
    return {
      showModal: false,
      selectedRequest: null,
      rating: 0,
      reviewText: ""
    };
  },
  computed: {
     userLoggedDetails() {
      console.log("asdfasdfsdf", this.$store.state.userLoggedDetails)
      return this.$store.state.userLoggedDetails || null; // Assuming userName is stored in Vuex
    }
  },
  methods: {
    async updateServiceRequest(id, data) {
      const res = await apis.updateServiceRequest(id, data);
      if (res) {
        await this.getServiceRequest();
      }
      const reviewRes = await apis.addReview({
        service_request_id: data.id,
        rating: data.rating,
        review_text: data.review_text
      })
      console.log("reviewREs", reviewRes)
    },
    async getServiceRequest() {
      const { data = [] } = await apis.getServiceRequest();
      if (data) {
        this.$store.commit("setServiceRequests", data);
      }
    },
    confirmCloseRequest(request) {
      this.selectedRequest = request;
      this.showModal = true;
    },
    closeModal() {
      this.showModal = false;
      this.rating = 0;
      this.reviewText = "";
    },
    submitRating() {
      if (this.selectedRequest) {
        const payload = { ...this.selectedRequest, service_status: "closed", rating: this.rating, reviewText: this.reviewText };
        this.updateServiceRequest(payload.id, payload);
        this.closeModal();
      }
    },
  },
};
</script>

<style>
.modal {
  background: rgba(0, 0, 0, 0.5);
}
.modal-content {
  max-width: 400px;
  margin: auto;
}
.star {
  font-size: 24px;
  cursor: pointer;
  color: gray;
}
.star.selected {
  color: gold;
}
</style>
