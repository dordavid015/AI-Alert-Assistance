import Vue from 'vue';
import Router from 'vue-router';
import Chat from '@/components/Chat.vue';

Vue.use(Router);

export default new Router({
  routes: [
    {
      path: '/:chatId?',
      name: 'chat',
      component: Chat,
      props: true, // Pass the chatId as a prop
    },
  ],
});
