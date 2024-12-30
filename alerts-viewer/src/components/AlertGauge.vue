<template>
  <div class="gauge-container">
    <div
        class="gauge"
        :style="{ backgroundColor: getBackgroundColor() }"
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
        critical: "red",
        warning: "orange",
        minor: "yellow",
      };
      return colors[this.severity] || "#ccc";
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
  border-radius: 8px;
  padding: 20px;
  width: 100px;
  height: 120px;
  color: black;
  font-family: Arial, sans-serif;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
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
