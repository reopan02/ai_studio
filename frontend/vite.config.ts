import { fileURLToPath } from 'node:url';
import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';

export default defineConfig(({ command }) => ({
  base: command === 'serve' ? '/' : '/static/',
  plugins: [vue()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  build: {
    outDir: fileURLToPath(new URL('../app/static', import.meta.url)),
    emptyOutDir: true,
    rollupOptions: {
      input: {
        app: fileURLToPath(new URL('./app.html', import.meta.url)),
        login: fileURLToPath(new URL('./login.html', import.meta.url)),
        video: fileURLToPath(new URL('./video.html', import.meta.url)),
        storage: fileURLToPath(new URL('./storage.html', import.meta.url)),
        admin: fileURLToPath(new URL('./admin.html', import.meta.url)),
        image: fileURLToPath(new URL('./image.html', import.meta.url)),
        products: fileURLToPath(new URL('./products.html', import.meta.url)),
        'ecommerce-image': fileURLToPath(new URL('./ecommerce-image.html', import.meta.url))
      }
    }
  }
}));
