<template>
  <div class="gauges-row">
    <div
        v-for="(count, severity) in severityCounts"
        :key="severity"
        class="gauge"
        v-if="count > 0"
        :style="{ backgroundColor: getBackgroundColor(severity) }"
    >
      <h2>{{ severity.toUpperCase() }}</h2>
      <h1>{{ count }}</h1>
    </div>
  </div>
</template>

<script>
export default {
  props: ["alerts"],
  computed: {
    severityCounts() {
      const counts = {
        security: 0,
        critical: 0,
        major: 0,
        minor: 0,
        warning: 0,
        informational: 0,
        debug: 0,
        trace: 0,
        indeterminate: 0,
        cleared: 0,
        normal: 0,
        ok: 0,
        unknown: 0,
      };
      this.alerts.forEach((alert) => {
        console.log(alert.severity);
        if (counts[alert.severity.toLowerCase()] !== undefined) {
          counts[alert.severity.toLowerCase()]++;
        }
      });
      return counts;
    },
  },
  methods: {
    getBackgroundColor(severity) {
      const colors = {
        security: "#D3D3D3",
        critical: "#FFB3B3",
        major: "#FFCCB3",
        minor: "#FFF3B3",
        warning: "#B3D9FF",
        informational: "#B3E6B3",
        debug: "#E6CCFF",
        trace: "#E6E6E6",
        indeterminate: "#F0F0F0",
        cleared: "#B3E6B3",
        normal: "#B3E6B3",
        ok: "#B3E6B3",
        unknown: "#E0E0E0",
      };
      return colors[severity.toLowerCase()] || "#FFFFFF";
    },
  },
};
</script>

<style scoped>
.gauges-row {
  display: flex;
  justify-content: space-around;
  align-items: center;
  height: 30%;
  padding: 10px;
  box-sizing: border-box;
}

.gauge {
  flex: 1;
  margin: 10px;
  text-align: center;
  border-radius: 10px;
  padding: 15px;
  color: black;
  font-family: Arial, sans-serif;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.gauge:hover {
  transform: scale(1.05);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.gauge h2 {
  margin: 0;
  font-size: 1.2em;
  font-weight: bold;
}

.gauge h1 {
  margin: 0;
  font-size: 2.5em;
}
</style>
