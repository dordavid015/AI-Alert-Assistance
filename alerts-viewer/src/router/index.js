import Vue from "vue";
import VueRouter from "vue-router";
import Monitor from "@/views/MonitorView.vue";

Vue.use(VueRouter);

const routes = [
  {
    path: "/",
    name: "Monitor",
    component: Monitor,
  },
];

const router = new VueRouter({
  mode: "history",
  base: process.env.BASE_URL,
  routes,
});

export default router;
