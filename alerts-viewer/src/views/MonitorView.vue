<template>
  <v-container>
    <v-row>
      <!-- Gauges -->
      <v-col cols="12" sm="4" v-for="(count, severity) in alertCounts" :key="severity">
        <div>
          <h3>{{ severity.toUpperCase() }} Alerts</h3>
          <alert-gauge :count="count" :severity="severity" />
        </div>
      </v-col>
    </v-row>

    <!-- Table -->
    <v-row>
      <v-col cols="12">
        <alert-table :alerts="filteredAlerts" :onSearch="handleSearch" />
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import AlertGauge from "@/components/AlertGauge.vue";
import AlertTable from "@/components/AlertTable.vue";

export default {
  components: { AlertGauge, AlertTable },
  data() {
    return {
      alerts: [],
      searchQuery: "",
    };
  },
  computed: {
    alertCounts() {
      const counts = { critical: 0, warning: 0, minor: 0 };
      this.alerts.forEach((alert) => {
        counts[alert.severity] = (counts[alert.severity] || 0) + 1;
      });
      return counts;
    },
    filteredAlerts() {
      return this.alerts.filter((alert) =>
          alert.message.toLowerCase().includes(this.searchQuery.toLowerCase())
      );
    },
  },
  methods: {
    async fetchAlerts() {
      const response = await fetch("/demo-alerts.json");
      this.alerts = await response.json();
    },
    handleSearch(query) {
      this.searchQuery = query;
    },
  },
  created() {
    this.fetchAlerts();
  },
};
</script>
