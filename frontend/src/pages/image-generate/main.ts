import { createApp } from 'vue';
import ImageGeneratePage from './image-generate-page.vue';
import '@/styles/ecommerce-image.css';
import { requireSession } from '@/shared/supabase';

async function bootstrap() {
  await requireSession();
  createApp(ImageGeneratePage).mount('#app');
}

void bootstrap();
