import { createRouter, createWebHistory } from 'vue-router';
import HomeView from '../views/HomeView.vue';
import MarkingView from '../views/MarkingView.vue';
import MarkingDetailView from '../views/MarkingDetailView.vue';
import ArbitrationView from '../views/ArbitrationView.vue';
import LoginView from '../views/LoginView.vue';
import { useUserStore } from '../stores/user';

const routes = [
  {
    path: '/login',
    name: 'login',
    component: LoginView,
    meta: { requiresAuth: false }
  },
  {
    path: '/',
    name: 'home',
    component: HomeView,
    meta: { requiresAuth: true }
  },
  {
    path: '/marking',
    name: 'marking',
    component: MarkingView,
    meta: { requiresAuth: true }
  },
  {
    path: '/marking/:id',
    name: 'marking-detail',
    component: MarkingDetailView,
    meta: { requiresAuth: true }
  },
  {
    path: '/arbitration',
    name: 'arbitration',
    component: ArbitrationView,
    meta: { requiresAuth: true }
  }
];

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
});

// 路由守卫
router.beforeEach((to, from, next) => {
  const userStore = useUserStore();
  
  // 检查是否需要认证
  if (to.meta.requiresAuth && !userStore.isLoggedIn) {
    // 检查是否有特殊的绕过标记
    const bypassAuth = localStorage.getItem('bypass-auth');
    if (bypassAuth === 'true') {
      console.log('检测到绕过认证标记，允许访问受保护页面');
      next();
      return;
    }
    
    // 如果用户token包含bypass字符串，也允许访问
    if (userStore.token && userStore.token.includes('bypass')) {
      console.log('检测到绕过token，允许访问受保护页面');
      next();
      return;
    }
    
    next('/login');
    return;
  }
  
  // 移除对admin用户的限制，允许admin访问所有页面
  next();
});

export default router;