import { createApp } from 'vue';
import { createPinia } from 'pinia';
import './style.css';
import App from './App.vue';
import router from './router'; // 这现在应该能正确解析了
import { useUserStore } from './stores/user';

const app = createApp(App);
const pinia = createPinia();

app.use(pinia);
app.use(router);

// 初始化用户状态
const userStore = useUserStore();
userStore.initFromStorage();

app.mount('#app');
