<template>
  <v-card>
    <v-data-table
        :headers="headers"
        :items="filteredAlerts"
        class="elevation-1"
        item-value="id"
    >
      <!-- Table Toolbar with Search Bar -->
      <template #top>
        <v-toolbar flat>
          <v-toolbar-title>Alerts</v-toolbar-title>
          <v-spacer></v-spacer>
          <v-text-field
              label="Search Alerts"
              v-model="searchQuery"
              @input="filterAlerts"
              solo
              append-icon="mdi-magnify"
              hide-details
              dense
              class="search-bar"
          />
        </v-toolbar>
      </template>

      <!-- Table rows -->
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
          <a @click.prevent="getSolutionUrl(item.text)">Suggest solution</a>
        </tr>
      </template>
    </v-data-table>
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
      return colors[severity.toLowerCase()] || "transparent";
    },
    getSolutionUrl(alertText) {
      const alertMessage = encodeURIComponent(alertText);
      // Open a new window (not just a new tab)
      const chatUrl = `${process.env.VUE_APP_CHAT_URL}${alertMessage}`;
      window.open(chatUrl, "chatWindow", "width=800,height=600,scrollbars=yes,resizable=yes");
    },
  }
};
</script>

<style scoped>
.search-bar {
  max-width: 400px; /* Make sure it does not take too much width */
}

.v-toolbar-title {
  font-weight: bold;
}

.v-spacer {
  flex-grow: 1;
}

.v-data-table {
  margin-top: 20px;
}
</style>
