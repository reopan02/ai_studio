<template>
  <div class="ecommerce-image-page">
    <!-- Header -->
    <header class="header">
      <div class="logo">
        <div class="logo-icon">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2">
            <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/>
          </svg>
        </div>
        <span>图像生成</span>
      </div>
      <div class="header-actions">
        <a href="/" class="btn btn-secondary" style="text-decoration: none; display: flex; align-items: center; gap: 8px;">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M19 12H5M12 19l-7-7 7-7"/>
          </svg>
          返回主页面
        </a>
      </div>
    </header>

    <div class="main-container">
      <!-- Sidebar -->
      <aside class="sidebar">
        <!-- Model Selection -->
        <section class="sidebar-section">
          <div class="section-title">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polygon points="12 2 2 7 12 12 22 7 12 2"/>
              <polyline points="2 17 12 22 22 17"/>
              <polyline points="2 12 12 17 22 12"/>
            </svg>
            模型选择
          </div>
          <select class="form-select" v-model="modelConfig.model">
            <option value="gemini-3-pro-image-preview">gemini-3-pro-image-preview (推荐)</option>
            <option value="gemini-2.5-flash-image">gemini-2.5-flash-image (快速)</option>
          </select>
        </section>

        <!-- Image Settings -->
        <section class="sidebar-section">
          <div class="section-title">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>
              <circle cx="8.5" cy="8.5" r="1.5"/>
              <polyline points="21 15 16 10 5 21"/>
            </svg>
            图像设置
          </div>
          <div class="form-group">
            <label class="form-label">宽高比</label>
            <select class="form-select" v-model="imageSettings.aspectRatio">
              <option value="">自动</option>
              <option value="1:1">1:1 (正方形)</option>
              <option value="16:9">16:9 (横向)</option>
              <option value="9:16">9:16 (纵向)</option>
              <option value="4:3">4:3 (标准)</option>
              <option value="3:4">3:4 (竖版)</option>
              <option value="3:2">3:2 (照片)</option>
              <option value="2:3">2:3 (竖版照片)</option>
            </select>
          </div>
          <div class="form-group">
            <label class="form-label">图像尺寸</label>
            <select class="form-select" v-model="imageSettings.size">
              <option value="1K">1K (默认)</option>
              <option value="2K">2K (高清)</option>
              <option value="4K">4K (超高清)</option>
            </select>
          </div>
          <div class="form-group">
            <label class="form-label">生成数量</label>
            <select class="form-select" v-model="imageSettings.n">
              <option v-for="i in 4" :key="i" :value="i">{{ i }} 张</option>
            </select>
          </div>
        </section>

        <!-- Generation History -->
        <section class="sidebar-section">
          <div class="section-title">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="10"/>
              <polyline points="12 6 12 12 16 14"/>
            </svg>
            生成历史
          </div>
          <div class="product-list" v-if="!loadingHistory && history.length > 0">
            <div
              v-for="item in history"
              :key="item.id"
              class="product-item"
              @click="loadHistoryItem(item)"
            >
              <img :src="item.image_url || placeholderImage" :alt="item.prompt" class="product-thumb">
              <div class="product-info">
                <div class="product-name">{{ truncate(item.prompt, 30) }}</div>
                <div class="product-meta">{{ formatDate(item.created_at) }}</div>
              </div>
            </div>
          </div>
          <div class="product-list-empty" v-else-if="!loadingHistory && history.length === 0">
            <p>暂无生成历史</p>
          </div>
          <div class="product-list-loading" v-else>
            <div class="spinner-small"></div>
            <span>加载中...</span>
          </div>
        </section>
      </aside>

      <!-- Main Content -->
      <main class="main-content">
        <!-- Prompt Input Panel -->
        <div class="content-panel">
          <div class="panel-header">
            <h3>描述您想要生成的图像</h3>
            <span class="panel-hint">{{ prompt.length }}/1000 字符</span>
          </div>
          <textarea
            class="form-input"
            v-model="prompt"
            rows="4"
            maxlength="1000"
            placeholder="请详细描述您想要生成的图像，例如：一只可爱的橘色小猫咪坐在窗台上，阳光透过窗户洒在它身上，背景是模糊的城市天际线..."
            @input="onPromptInput"
          ></textarea>
        </div>

        <!-- Generation Result -->
        <div class="result-area">
          <div class="result-placeholder" v-if="!generating && generatedImages.length === 0">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/>
            </svg>
            <h3>准备生成</h3>
            <p>输入描述后点击生成按钮创建图像</p>
          </div>

          <div class="loading-state" v-if="generating">
            <div class="spinner"></div>
            <p>正在生成图像...</p>
          </div>

          <div class="result-container" v-if="generatedImages.length > 0 && !generating">
            <div class="image-grid" :class="{ 'single-image': generatedImages.length === 1 }">
              <div
                v-for="(img, idx) in generatedImages"
                :key="idx"
                class="generated-image-item"
                @click="openLightbox(img)"
              >
                <img :src="img" alt="Generated image">
                <div class="image-overlay">
                  <button class="btn btn-ghost btn-icon" @click.stop="downloadImage(img, idx)">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                      <polyline points="7 10 12 15 17 10"/>
                      <line x1="12" y1="15" x2="12" y2="3"/>
                    </svg>
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Generate Button -->
        <div class="generate-section">
          <button
            class="generate-btn"
            :disabled="!canGenerate || generating"
            @click="generateImage"
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" v-if="!generating">
              <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/>
            </svg>
            <div class="spinner-small" v-else></div>
            {{ generating ? '生成中...' : '生成图像' }}
          </button>
          <div class="generate-hint" v-if="!canGenerate">
            {{ generateHint }}
          </div>
        </div>
      </main>
    </div>

    <!-- Lightbox -->
    <div class="error-overlay" v-if="lightboxImage" @click="lightboxImage = ''">
      <div class="lightbox-content" @click.stop>
        <img :src="lightboxImage" alt="Full size image">
        <button class="btn btn-secondary" @click="downloadImage(lightboxImage, 0)" style="margin-top: 16px;">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
            <polyline points="7 10 12 15 17 10"/>
            <line x1="12" y1="15" x2="12" y2="3"/>
          </svg>
          下载
        </button>
      </div>
    </div>

    <!-- Toast Container -->
    <div class="toast-container">
      <div v-for="toast in toasts" :key="toast.id" class="toast" :class="toast.type">
        {{ toast.message }}
      </div>
    </div>

    <!-- Error Message -->
    <div class="error-overlay" v-if="errorMessage" @click="errorMessage = ''">
      <div class="error-modal" @click.stop>
        <div class="error-header">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="10"/>
            <line x1="12" y1="8" x2="12" y2="12"/>
            <line x1="12" y1="16" x2="12.01" y2="16"/>
          </svg>
          <h3>生成失败</h3>
        </div>
        <p>{{ errorMessage }}</p>
        <button class="btn btn-primary" @click="errorMessage = ''">确定</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue';

// Types
interface HistoryItem {
  id: string;
  prompt: string;
  image_url: string;
  created_at: string;
}

interface Toast {
  id: number;
  message: string;
  type: 'success' | 'error' | 'info';
}

// State
const apiConfig = reactive({
  apiKey: '',
  baseUrl: ''
});

// Placeholder image as data URI
const placeholderImage = 'data:image/svg+xml;charset=utf-8,' + encodeURIComponent(`
<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100" viewBox="0 0 100 100">
  <rect width="100" height="100" fill="#1a1a2e"/>
  <rect x="25" y="25" width="50" height="50" rx="4" fill="none" stroke="#4a4a6a" stroke-width="2"/>
  <circle cx="38" cy="38" r="5" fill="#4a4a6a"/>
  <path d="M25 65 L45 45 L55 55 L75 35 L75 75 L25 75 Z" fill="#4a4a6a" opacity="0.5"/>
</svg>
`);

const modelConfig = reactive({
  model: 'gemini-3-pro-image-preview'
});

const imageSettings = reactive({
  n: 1,
  size: '1K',
  aspectRatio: ''
});

const prompt = ref('');
const generating = ref(false);
const generatedImages = ref<string[]>([]);
const errorMessage = ref('');
const toasts = ref<Toast[]>([]);
const lightboxImage = ref('');

// History
const history = ref<HistoryItem[]>([]);
const loadingHistory = ref(false);

// Computed
const canGenerate = computed(() => {
  return prompt.value.trim().length > 0;
});

const generateHint = computed(() => {
  if (!prompt.value.trim()) return '请输入图像描述';
  return '';
});

// Methods
function getCsrfToken(): string {
  const match = document.cookie.match(/csrf_token=([^;]+)/);
  return match ? match[1] : '';
}

function normalizeApiKey(value: string): string {
  return String(value || '').trim().replace(/^bearer\s+/i, '').trim();
}

function normalizeBaseUrl(value: string): string | null {
  const raw = String(value || '').trim();
  return raw || null;
}

function extractImageUrls(payload: any): string[] {
  if (!payload || typeof payload !== 'object') return [];
  const urls: string[] = [];

  if (Array.isArray(payload.data)) {
    for (const item of payload.data) {
      if (item?.url) urls.push(item.url);
      else if (item?.b64_json) urls.push(`data:image/png;base64,${item.b64_json}`);
    }
  }
  if (payload.url) urls.push(payload.url);
  if (payload.b64_json) urls.push(`data:image/png;base64,${payload.b64_json}`);
  if (payload.image_url) urls.push(payload.image_url);

  return urls;
}

async function fetchHistory() {
  loadingHistory.value = true;
  try {
    const res = await fetch('/api/v1/images?limit=20', {
      credentials: 'include'
    });
    if (!res.ok) throw new Error('Failed to fetch history');
    const data = await res.json();
    history.value = data || [];
  } catch (e) {
    console.error('Failed to load history:', e);
  } finally {
    loadingHistory.value = false;
  }
}

function loadHistoryItem(item: HistoryItem) {
  prompt.value = item.prompt || '';
  if (item.image_url) {
    generatedImages.value = [item.image_url];
  }
}

function truncate(text: string, length: number): string {
  if (!text) return '';
  if (text.length <= length) return text;
  return text.substring(0, length) + '...';
}

function formatDate(dateStr: string): string {
  if (!dateStr) return '';
  const date = new Date(dateStr);
  return date.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' });
}

function onPromptInput() {
  // Could add debounced save to localStorage here
}

function loadApiConfig() {
  // Load from global config keys (set in portal page)
  apiConfig.apiKey = localStorage.getItem('global_api_key') || localStorage.getItem('video_api_key') || '';
  apiConfig.baseUrl = localStorage.getItem('global_base_url') || localStorage.getItem('video_base_url') || '';
}

async function generateImage() {
  if (!canGenerate.value || generating.value) return;

  generating.value = true;
  errorMessage.value = '';

  try {
    const formData = new FormData();
    formData.append('prompt', prompt.value);
    formData.append('model', modelConfig.model);
    formData.append('n', String(imageSettings.n));
    formData.append('size', imageSettings.size);
    formData.append('response_format', 'url');
    if (imageSettings.aspectRatio) {
      formData.append('aspect_ratio', imageSettings.aspectRatio);
    }

    const headers: Record<string, string> = {
      'X-CSRF-Token': getCsrfToken()
    };
    const apiKey = normalizeApiKey(apiConfig.apiKey);
    if (apiKey) headers['X-API-Key'] = apiKey;
    const baseUrl = normalizeBaseUrl(apiConfig.baseUrl);
    if (baseUrl) headers['X-Base-Url'] = baseUrl;

    const res = await fetch('/api/v1/images/generations', {
      method: 'POST',
      credentials: 'include',
      headers,
      body: formData
    });

    if (!res.ok) {
      const errData = await res.json().catch(() => ({}));
      throw new Error(errData.detail || `HTTP ${res.status}`);
    }

    const data = await res.json();
    const payload = data && typeof data === 'object' && data.response ? data.response : data;
    const urls = extractImageUrls(payload);

    if (urls.length === 0) {
      // Try extracting from top level
      const topUrls = extractImageUrls(data);
      if (topUrls.length > 0) {
        generatedImages.value = topUrls;
      } else {
        throw new Error('未能获取生成的图像');
      }
    } else {
      generatedImages.value = urls;
    }

    showToast('图像生成成功', 'success');
    // Refresh history
    fetchHistory();
  } catch (e: any) {
    errorMessage.value = e.message || '生成失败，请重试';
  } finally {
    generating.value = false;
  }
}

function downloadImage(url: string, index: number) {
  const link = document.createElement('a');
  link.href = url;
  link.download = `generated-${Date.now()}-${index}.png`;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}

function openLightbox(url: string) {
  lightboxImage.value = url;
}

let toastId = 0;
function showToast(message: string, type: Toast['type'] = 'info') {
  const id = toastId++;
  toasts.value.push({ id, message, type });

  setTimeout(() => {
    const index = toasts.value.findIndex(t => t.id === id);
    if (index !== -1) {
      toasts.value.splice(index, 1);
    }
  }, 3000);
}

// Lifecycle
onMounted(() => {
  loadApiConfig();
  fetchHistory();
});
</script>

<style scoped>
.generated-image-item {
  position: relative;
  border-radius: var(--radius-md);
  overflow: hidden;
  cursor: pointer;
  transition: transform 0.2s;
}

.generated-image-item:hover {
  transform: scale(1.02);
}

.generated-image-item img {
  width: 100%;
  height: auto;
  display: block;
}

.image-overlay {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 12px;
  background: linear-gradient(transparent, rgba(0,0,0,0.6));
  display: flex;
  justify-content: flex-end;
  opacity: 0;
  transition: opacity 0.2s;
}

.generated-image-item:hover .image-overlay {
  opacity: 1;
}

.image-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  width: 100%;
}

.image-grid.single-image {
  max-width: 512px;
  margin: 0 auto;
}

.lightbox-content {
  background: var(--bg-secondary);
  padding: 20px;
  border-radius: var(--radius-lg);
  max-width: 90vw;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.lightbox-content img {
  max-width: 100%;
  max-height: 70vh;
  border-radius: var(--radius-md);
}
</style>
