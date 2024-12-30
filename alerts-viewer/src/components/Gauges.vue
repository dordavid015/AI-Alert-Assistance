<template>
  <v-row justify="space-around">
    <v-col cols="4">
      <div class="gauge" style="text-align: center; background: rgba(255, 0, 0, 0.1); border-radius: 10px; padding: 10px;">
        <h2>Critical</h2>
        <h1>{{ criticalCount }}</h1>
      </div>
    </v-col>
    <v-col cols="4">
      <div class="gauge" style="text-align: center; background: rgba(255, 165, 0, 0.1); border-radius: 10px; padding: 10px;">
        <h2>Warning</h2>
        <h1>{{ warningCount }}</h1>
      </div>
    </v-col>
    <v-col cols="4">
      <div class="gauge" style="text-align: center; background: rgba(255, 255, 0, 0.1); border-radius: 10px; padding: 10px;">
        <h2>Minor</h2>
        <h1>{{ minorCount }}</h1>
      </div>
    </v-col>
  </v-row>
</template>

<script>
export default {
  props: ["alerts"],
  computed: {
    criticalCount() {
      return this.alerts.filter((alert) => alert.severity === "critical").length;
    },
    warningCount() {
      return this.alerts.filter((alert) => alert.severity === "warning").length;
    },
    minorCount() {
      return this.alerts.filter((alert) => alert.severity === "minor").length;
    },
  },
};
</script>

<style scoped>
.gauge {
  font-family: Arial, sans-serif;
}
</style>
