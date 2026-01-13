import { createApp } from 'vue';
import StoragePage from './storage-page.vue';
import '@/styles/app-static.css';
import { requireSession } from '@/shared/supabase';

async function bootstrap() {
  await requireSession();
  createApp(StoragePage).mount('#app');
}

void bootstrap();
