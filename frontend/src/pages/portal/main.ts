import { createApp } from 'vue';
import PortalPage from './portal-page.vue';
import '@/styles/app-static.css';
import { requireSession } from '@/shared/supabase';

async function bootstrap() {
  await requireSession();
  createApp(PortalPage).mount('#app');
}

void bootstrap();
