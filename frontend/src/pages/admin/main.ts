import { createApp } from 'vue';
import AdminPage from './admin-page.vue';
import '@/styles/app-static.css';
import { requireSession } from '@/shared/supabase';

async function bootstrap() {
  await requireSession();
  await import('@/legacy/admin-legacy');
  createApp(AdminPage).mount('#app');
}

void bootstrap();
