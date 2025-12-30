import { createApp } from 'vue';
import StoragePage from './storage-page.vue';
import '@/styles/app-static.css';
import '@/legacy/storage-legacy';

// The legacy storage module registers an init hook; call it before DOMContentLoaded.
// eslint-disable-next-line @typescript-eslint/no-explicit-any
const legacy = (globalThis as any).StoragePage;
if (legacy?.init) legacy.init();

createApp(StoragePage).mount('#app');
