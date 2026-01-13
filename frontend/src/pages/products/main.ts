import { createApp } from 'vue';
import ProductsPage from './products-page.vue';
import '@/styles/image-editor.css';
import { requireSession } from '@/shared/supabase';

async function bootstrap() {
  await requireSession();
  createApp(ProductsPage).mount('#app');
}

void bootstrap();
