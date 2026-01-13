import { createApp } from 'vue';
import EcommerceImagePage from './ecommerce-image-page.vue';
import '@/styles/ecommerce-image.css';
import { requireSession } from '@/shared/supabase';

async function bootstrap() {
  await requireSession();
  createApp(EcommerceImagePage).mount('#app');
}

void bootstrap();
