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
    // Fetch the alerts data from the local file
    fetch("/alerts.json")
        .then((response) => response.json())
        .then((data) => {
          this.alerts = data.alerts; // Assign the alerts to the component's data
        })
        .catch((error) => {
          console.error("Error fetching alerts:", error);
        });
  },
};
</script>
