import { createRouter, createWebHistory } from 'vue-router';
import HomeView from '../views/HomeView.vue';
import MarkingView from '../views/MarkingView.vue';
import MarkingDetailView from '../views/MarkingDetailView.vue';
import ArbitrationView from '../views/ArbitrationView.vue';

const routes = [
  {
    path: '/',
    name: 'home',
    component: HomeView
  },
  {
    path: '/marking',
    name: 'marking',
    component: MarkingView
  },
  {
    path: '/marking/:id',
    name: 'marking-detail',
    component: MarkingDetailView
  },
  {
    path: '/arbitration',
    name: 'arbitration',
    component: ArbitrationView
  }
];

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
});

export default router; // 使用默认导出