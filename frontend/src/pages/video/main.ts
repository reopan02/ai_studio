import { createApp } from 'vue';
import VideoPage from './video-page.vue';
import '@/styles/app-static.css';
import { requireSession } from '@/shared/supabase';

async function bootstrap() {
  await requireSession();
  await import('@/legacy/video-legacy');
  createApp(VideoPage).mount('#app');
}

void bootstrap();
