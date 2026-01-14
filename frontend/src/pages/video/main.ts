import { createApp } from 'vue';
import VideoPage from './video-page.vue';
import '@/styles/app-static.css';
import { requireSession } from '@/shared/supabase';

async function bootstrap() {
  await requireSession();
  createApp(VideoPage).mount('#app');
  // Import legacy script AFTER Vue component is mounted so DOM elements exist
  await import('@/legacy/video-legacy');
}

void bootstrap();
