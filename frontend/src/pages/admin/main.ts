import { createApp } from 'vue';
import AdminPage from './admin-page.vue';
import '@/styles/app-static.css';
import '@/legacy/admin-legacy';

createApp(AdminPage).mount('#app');
