import { createApp } from 'vue';
import ImagePage from './image-page.vue';
import '@/styles/image-editor.css';
import { requireSession } from '@/shared/supabase';

async function bootstrap() {
  await requireSession();
  createApp(ImagePage).mount('#app');
  // Load legacy behavior after Vue has rendered the DOM.
  await import('@/legacy/image-legacy');
}

void bootstrap();
