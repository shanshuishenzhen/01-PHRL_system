import { createApp } from 'vue';
import './style.css';
import App from './App.vue';
import router from './router'; // 这现在应该能正确解析了

const app = createApp(App);

app.use(router);

app.mount('#app');
