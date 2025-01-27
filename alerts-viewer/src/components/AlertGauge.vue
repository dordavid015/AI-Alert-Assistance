<template>
  <div class="gauge-container">
    <div
        class="gauge"
        :style="{ backgroundColor: getBackgroundColor(), color: getTextColor() }"
    >
      <h1>{{ count }}</h1>
      <p>{{ severity.toUpperCase() }} Alerts</p>
    </div>
  </div>
</template>

<script>
export default {
  props: ["count", "severity"],
  methods: {
    getBackgroundColor() {
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
      return colors[this.severity.toLowerCase()] || "#FFFFFF";
    },
    getTextColor() {
      const darkTextColors = ["#FFF3B3", "#F0F0F0", "#E6E6E6", "#FFFFFF"];
      const backgroundColor = this.getBackgroundColor();
      return darkTextColors.includes(backgroundColor) ? "#000" : "#333";
    },
  },
};
</script>

<style scoped>
.gauge-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
}

.gauge {
  text-align: center;
  border-radius: 12px;
  padding: 20px;
  width: 120px;
  height: 140px;
  font-family: Arial, sans-serif;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  transition: all 0.3s ease;
}
.gauge:hover {
  transform: scale(1.05);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}
.gauge h1 {
  margin: 0;
  font-size: 2.5em;
}
.gauge p {
  margin: 0;
  font-size: 0.9em;
}
</style>
