import { createApp } from 'vue';
import '@/styles/app-static.css';
import RunningHubVideoPage from './runninghub-video-page.vue';
import { requireSession } from '@/shared/supabase';

async function bootstrap() {
  await requireSession();
  createApp(RunningHubVideoPage).mount('#app');
}

void bootstrap();
