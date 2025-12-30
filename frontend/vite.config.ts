import { resolve } from 'node:path';
import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';

export default defineConfig({
  base: '/static/',
  plugins: [vue()],
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src')
    }
  },
  build: {
    outDir: resolve(__dirname, '../app/static'),
    emptyOutDir: true,
    rollupOptions: {
      input: {
        app: resolve(__dirname, 'app.html'),
        login: resolve(__dirname, 'login.html'),
        video: resolve(__dirname, 'video.html'),
        storage: resolve(__dirname, 'storage.html'),
        admin: resolve(__dirname, 'admin.html'),
        image: resolve(__dirname, 'image.html'),
        products: resolve(__dirname, 'products.html')
      }
    }
  }
});
