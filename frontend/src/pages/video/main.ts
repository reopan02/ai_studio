import { createApp } from 'vue';
import VideoPage from './video-page.vue';
import '@/styles/app-static.css';
import '@/legacy/video-legacy';

createApp(VideoPage).mount('#app');
