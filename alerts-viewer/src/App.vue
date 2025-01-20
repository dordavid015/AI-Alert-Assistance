<template>
  <v-app>
    <v-main>
      <div class="app-container">
        <!-- Gauges Section -->
        <div class="gauges-row">
          <Gauges :alerts="alerts" />
        </div>
        <!-- Alert Table Section -->
        <div class="alert-table">
          <AlertTable :alerts="alerts" />
        </div>
      </div>
    </v-main>
  </v-app>
</template>

<script>
import AlertTable from "./components/AlertTable.vue";
import Gauges from "./components/Gauges.vue";

export default {
  components: {
    AlertTable,
    Gauges,
  },
  data() {
    return {
      alerts: [], // Initialize as empty
    };
  },
  mounted() {
    // Fetch the alerts data from the Alerta API
    const ALERTA_API_KEY = "64_hXcmnYSfGKPvtCnXK6OSlZMSYxljU-MCY3VnC";
    const ALERTA_URL = `./alerts.json`; // Replace with your actual API endpoint

    fetch(ALERTA_URL, {
      headers: {
        Authorization: `Key ${ALERTA_API_KEY}`,
      },
    })
        .then((response) => {
          if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
          }
          return response.json();
        })
        .then((data) => {
          this.alerts = data.alerts; // Assign the alerts to the component's data
        })
        .catch((error) => {
          console.error("Error fetching alerts:", error);
        });
  },
};
</script>

<style scoped>
.app-container {
  display: flex;
  flex-direction: column;
  height: 100vh; /* Full height of the viewport */
  overflow: hidden;
}

.gauges-row {
  height: 30%; /* Gauges section occupies 30% of the screen height */    height: 30%;
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 10px;
  box-sizing: border-box;
  flex-wrap: nowrap; /* Prevent wrapping */
}

.alert-table {
  height: 70%; /* Alert table occupies 70% of the screen height */
  overflow-y: auto;
}

.gauge {
  text-align: center;
  background: rgba(255, 0, 0, 0.1);
  border-radius: 10px;
  padding: 10px;
  flex-grow: 1; /* Allow the gauge to take up space */
  flex-shrink: 1; /* Allow the gauge to shrink */
  flex-basis: 0; /* Allow the gauge to scale down */
  margin: 5px;
  transition: all 0.3s ease;
  min-width: 120px; /* Minimum width */
  max-width: 33.33%; /* Gauge takes up no more than 1/3 of the screen width */
}

.gauge h2 {
  font-size: 1.2em;
}

.gauge h1 {
  font-size: 2em;
}
</style>
