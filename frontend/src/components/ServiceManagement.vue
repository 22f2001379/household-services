<template>
    <div class="card">
      <div class="card-header">
        <h3>Service Management</h3>
      </div>
      <div class="card-body">
        <form @submit.prevent="addService" class="mb-4">
          <div class="row">
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
              <button type="submit" class="btn btn-primary">Add Service</button>
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
              <td>{{ service.name }}</td>
              <td>{{ service.price }}</td>
              <td>{{ service.timeRequired }}</td>
              <td>
                <button class="btn btn-sm btn-warning" @click="editService(index)">Edit</button>
                <button class="btn btn-sm btn-danger" @click="deleteService(index)">Delete</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </template>
  
  <script>
  export default {
    name: 'ServiceManagement',
    data() {
      return {
        newService: { name: '', price: 0, timeRequired: '' },
        services: [
          { name: 'AC Servicing', price: 500, timeRequired: '2 hours' }
        ]
      }
    },
    methods: {
      addService() {
        this.services.push({ ...this.newService })
        this.newService = { name: '', price: 0, timeRequired: '' }
      },
      editService(index) {
        this.newService = { ...this.services[index] }
        this.deleteService(index)
      },
      deleteService(index) {
        this.services.splice(index, 1)
      }
    }
  }
  </script>