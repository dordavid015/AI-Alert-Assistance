<template>
  <v-app>
    <v-main>
      <v-container>
        <!-- Gauges Section -->
        <Gauges :alerts="alerts" />
        <!-- Alert Table -->
        <AlertTable :alerts="alerts" />
      </v-container>
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
    const ALERTA_API_KEY = "uZqtaZdkoMr40Gw9j7TgihS_4vK3DSniUNBDFdUr";
    const ALERTA_URL = `http://localhost:8080/api/alerts?api-key=${ALERTA_API_KEY}`;

    fetch(ALERTA_URL, {
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
