<template>
  <v-card>
    <v-toolbar>
      <v-text-field
        label="Search Alerts"
        v-model="searchQuery"
        @input="filterAlerts"
      />
    </v-toolbar>
    <v-data-table
      :headers="headers"
      :items="filteredAlerts"
      class="elevation-1"
      item-value="id"
    >
      <template #item="{ item }">
        <tr
          @contextmenu.prevent="openContextMenu($event, item)"
          :style="{ backgroundColor: getSeverityColor(item.severity) }"
          style="cursor: context-menu"
        >
          <td>{{ item.id }}</td>
          <td>{{ item.environment }}</td>
          <td>{{ item.status }}</td>
          <td>{{ item.severity }}</td>
          <td>{{ item.text }}</td>
          <td>{{ item.duplicateCount }}</td>
          <!-- Add the duplicateCount here -->
          <a :href="getSolutionUrl(item.text)">Suggest solution</a
          >
        </tr>
      </template>
    </v-data-table>

    <!-- Context Menu -->
    <v-menu
      v-model="contextMenuVisible"
      :position-x="contextMenuPosition.x"
      :position-y="contextMenuPosition.y"
      absolute
      offset-y
    >
      <v-list>
        <v-list-item
          v-for="(option, index) in menuOptions"
          :key="index"
          @click="handleMenuOption(option)"
        >
          <v-list-item-title>{{ option.label }}</v-list-item-title>
        </v-list-item>
      </v-list>
    </v-menu>
  </v-card>
</template>

<script>
export default {
  props: ["alerts"],
  data() {
    return {
      headers: [
        { text: "ID", value: "id" },
        { text: "Environment", value: "environment" },
        { text: "Status", value: "status" },
        { text: "Severity", value: "severity" },
        { text: "Message", value: "text" },
        { text: "Count", value: "duplicateCount" }, // Add Count as a column header
        { text: "More Info", value: "attributes.moreInfo" },
      ],
      searchQuery: "",
      filteredAlerts: [],
      contextMenuVisible: false,
      contextMenuPosition: { x: 0, y: 0 },
      selectedAlert: null,
      menuOptions: [{ label: "Suggest solution", action: "suggestSolution" }],
    };
  },
  watch: {
    alerts: {
      immediate: true,
      handler(newAlerts) {
        this.filteredAlerts = newAlerts; // Initialize filtered alerts
      },
    },
  },
  methods: {
    filterAlerts() {
      const query = this.searchQuery.toLowerCase();
      this.filteredAlerts = this.alerts.filter(
        (alert) =>
          alert.text.toLowerCase().includes(query) ||
          alert.severity.toLowerCase().includes(query) ||
          alert.environment.toLowerCase().includes(query) ||
          String(alert.id).includes(query)
      );
    },
    getSeverityColor(severity) {
      const colors = {
        critical: "rgba(255, 0, 0, 0.2)", // Light red
        warning: "rgba(255, 165, 0, 0.2)", // Light orange
        minor: "rgba(255, 255, 0, 0.2)", // Light yellow
      };
      return colors[severity.toLowerCase()] || "transparent";
    },
    openContextMenu(event, alert) {
      this.contextMenuVisible = true;
      this.contextMenuPosition = { x: event.clientX, y: event.clientY };
      this.selectedAlert = alert;
    },
    handleMenuOption(option) {
      if (option.action === "suggestSolution" && this.selectedAlert) {
        const alertMessage = encodeURIComponent(this.selectedAlert.text);
        const url = `http://localhost:8082/#/${encodeURIComponent(
          this.selectedAlert.text
        )}`;
        window.open(
          url,
          "_blank",
          "width=800,height=600,scrollbars=yes,resizable=yes"
        );
      }
      this.contextMenuVisible = false; // Close the menu
    },
    getSolutionUrl(alertText) {
      const alertMessage = encodeURIComponent(alertText);
      return `http://localhost:8082/#/${alertMessage}`;
    },
  },
};
</script>
