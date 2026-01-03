<template>
  <div class="container">
    <header>
      <h1>Video API Portal</h1>
      <p style="color: var(--text-secondary); margin-top: 8px">请选择功能模块</p>
    </header>

    <section v-if="error" class="card error-banner" style="margin-bottom: 20px">
      {{ error }}
    </section>

    <!-- Global API Configuration -->
    <section class="card api-config-section">
      <div class="config-header" @click="toggleConfig">
        <div class="config-title">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="3"/>
            <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/>
          </svg>
          <span>全局 API 配置</span>
          <span class="config-status" :class="{ configured: isConfigured }">
            {{ isConfigured ? '已配置' : '未配置' }}
          </span>
        </div>
        <svg class="chevron" :class="{ expanded: showConfig }" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <polyline points="6 9 12 15 18 9"/>
        </svg>
      </div>
      <div class="config-content" v-show="showConfig">
        <p class="config-desc">配置 API Key 和 Base URL，将自动应用到所有功能模块</p>
        <div class="config-form">
          <div class="form-group">
            <label class="form-label">API Key</label>
            <div class="input-wrapper">
              <input
                :type="showApiKey ? 'text' : 'password'"
                class="form-input"
                v-model="apiKey"
                placeholder="输入您的 API Key"
              >
              <button class="toggle-btn" @click="showApiKey = !showApiKey" type="button">
                <svg v-if="!showApiKey" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
                  <circle cx="12" cy="12" r="3"/>
                </svg>
                <svg v-else width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/>
                  <line x1="1" y1="1" x2="23" y2="23"/>
                </svg>
              </button>
            </div>
          </div>
          <div class="form-group">
            <label class="form-label">Base URL</label>
            <div class="input-wrapper">
              <input
                :type="showBaseUrl ? 'text' : 'password'"
                class="form-input"
                v-model="baseUrl"
                placeholder="https://api.example.com"
              >
              <button class="toggle-btn" @click="showBaseUrl = !showBaseUrl" type="button">
                <svg v-if="!showBaseUrl" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
                  <circle cx="12" cy="12" r="3"/>
                </svg>
                <svg v-else width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/>
                  <line x1="1" y1="1" x2="23" y2="23"/>
                </svg>
              </button>
            </div>
          </div>
          <div class="btn-group">
            <button class="btn btn-primary" @click="saveConfig">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"/>
                <polyline points="17 21 17 13 7 13 7 21"/>
                <polyline points="7 3 7 8 15 8"/>
              </svg>
              保存配置
            </button>
            <button class="btn btn-secondary" @click="resetConfig">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="1 4 1 10 7 10"/>
                <path d="M3.51 15a9 9 0 1 0 2.13-9.36L1 10"/>
              </svg>
              清除
            </button>
          </div>
        </div>
        <div v-if="saveMessage" class="save-message" :class="saveMessageType">
          {{ saveMessage }}
        </div>
      </div>
    </section>

    <div class="portal-grid">
      <a href="/video" class="card portal-card">
        <svg class="portal-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <rect x="2" y="2" width="20" height="20" rx="2.18" ry="2.18"></rect>
          <line x1="7" y1="2" x2="7" y2="22"></line>
          <line x1="17" y1="2" x2="17" y2="22"></line>
          <line x1="2" y1="12" x2="22" y2="12"></line>
          <line x1="2" y1="7" x2="7" y2="7"></line>
          <line x1="2" y1="17" x2="7" y2="17"></line>
          <line x1="17" y1="17" x2="22" y2="17"></line>
          <line x1="17" y1="7" x2="22" y2="7"></line>
        </svg>
        <div class="portal-title">视频生成</div>
        <div class="portal-desc">Sora 2, Veo, Seedance 等模型视频生成</div>
      </a>

      <a href="/storage" class="card portal-card">
        <svg class="portal-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
          <polyline points="7 10 12 15 17 10"></polyline>
          <line x1="12" y1="15" x2="12" y2="3"></line>
        </svg>
        <div class="portal-title">存储库</div>
        <div class="portal-desc">查看历史生成记录</div>
      </a>

      <a href="/image" class="card portal-card">
        <svg class="portal-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
          <circle cx="8.5" cy="8.5" r="1.5"></circle>
          <polyline points="21 15 16 10 5 21"></polyline>
        </svg>
        <div class="portal-title">图像处理</div>
        <div class="portal-desc">多图参考的图像编辑 (Gemini)</div>
      </a>

      <a href="/image-generate" class="card portal-card">
        <svg class="portal-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"></polygon>
        </svg>
        <div class="portal-title">图像生成</div>
        <div class="portal-desc">文生图，根据文字描述生成图像</div>
      </a>

      <a href="/products" class="card portal-card">
        <svg class="portal-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <path d="M20 7H4a2 2 0 0 0-2 2v10a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V9a2 2 0 0 0-2-2Z"></path>
          <path d="M9 2v5"></path>
          <path d="M15 2v5"></path>
          <path d="M2 9h20"></path>
        </svg>
        <div class="portal-title">产品库</div>
        <div class="portal-desc">产品图片识别与管理</div>
      </a>

      <a href="/ecommerce-image" class="card portal-card">
        <svg class="portal-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
          <circle cx="8.5" cy="8.5" r="1.5"></circle>
          <polyline points="21 15 16 10 5 21"></polyline>
          <path d="M14 3v4h4"></path>
        </svg>
        <div class="portal-title">电商图生成</div>
        <div class="portal-desc">基于产品库的电商图快速生成</div>
      </a>

      <a v-if="isAdmin" href="/admin" class="card portal-card">
        <svg class="portal-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <path
            d="M12 1l3 5 5 1-3.5 4.2.8 5.8L12 15l-5.3 2.9.8-5.8L4 7l5-1 3-5z"
          ></path>
        </svg>
        <div class="portal-title">Admin</div>
        <div class="portal-desc">User management &amp; system stats</div>
      </a>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref, computed } from 'vue';
import { getCurrentUser } from '@/shared/auth';

// Global storage keys used by all pages
const STORAGE_KEYS = {
  apiKey: 'global_api_key',
  baseUrl: 'global_base_url'
};

const error = ref<string>('');
const isAdmin = ref(false);
const showConfig = ref(false);
const apiKey = ref('');
const baseUrl = ref('');
const showApiKey = ref(false);
const showBaseUrl = ref(false);
const saveMessage = ref('');
const saveMessageType = ref<'success' | 'error'>('success');

const isConfigured = computed(() => {
  return !!(apiKey.value || baseUrl.value);
});

function toggleConfig() {
  showConfig.value = !showConfig.value;
}

function normalizeApiKey(value: string): string {
  const raw = String(value || '').trim();
  return raw.replace(/^bearer\s+/i, '').trim();
}

function normalizeBaseUrl(value: string): string | null {
  const raw = String(value || '').trim();
  if (!raw) return null;

  try {
    const u = new URL(raw);
    if (u.protocol !== 'https:' && u.protocol !== 'http:') {
      throw new Error('Base URL must use HTTP or HTTPS');
    }
    return u.origin;
  } catch {
    throw new Error('Invalid URL format');
  }
}

function loadConfig() {
  apiKey.value = localStorage.getItem(STORAGE_KEYS.apiKey) || '';
  baseUrl.value = localStorage.getItem(STORAGE_KEYS.baseUrl) || '';

  // Also check legacy keys and migrate if needed
  if (!apiKey.value) {
    apiKey.value = localStorage.getItem('video_api_key') || localStorage.getItem('apiKey') || '';
  }
  if (!baseUrl.value) {
    baseUrl.value = localStorage.getItem('video_base_url') || localStorage.getItem('baseUrl') || '';
  }
}

function saveConfig() {
  try {
    const normalizedApiKey = normalizeApiKey(apiKey.value);
    const normalizedBaseUrl = normalizeBaseUrl(baseUrl.value);

    apiKey.value = normalizedApiKey;
    baseUrl.value = normalizedBaseUrl || '';

    // Save to global keys
    localStorage.setItem(STORAGE_KEYS.apiKey, apiKey.value);
    localStorage.setItem(STORAGE_KEYS.baseUrl, baseUrl.value);

    // Also save to legacy keys for backward compatibility
    localStorage.setItem('video_api_key', apiKey.value);
    localStorage.setItem('video_base_url', baseUrl.value);
    localStorage.setItem('apiKey', apiKey.value);
    localStorage.setItem('baseUrl', baseUrl.value);

    saveMessage.value = '配置已保存，将应用到所有功能模块';
    saveMessageType.value = 'success';
    setTimeout(() => { saveMessage.value = ''; }, 3000);
  } catch (e: any) {
    saveMessage.value = e.message || '保存失败';
    saveMessageType.value = 'error';
    setTimeout(() => { saveMessage.value = ''; }, 3000);
  }
}

function resetConfig() {
  apiKey.value = '';
  baseUrl.value = '';

  // Clear all keys
  localStorage.removeItem(STORAGE_KEYS.apiKey);
  localStorage.removeItem(STORAGE_KEYS.baseUrl);
  localStorage.removeItem('video_api_key');
  localStorage.removeItem('video_base_url');
  localStorage.removeItem('apiKey');
  localStorage.removeItem('baseUrl');

  saveMessage.value = '配置已清除';
  saveMessageType.value = 'success';
  setTimeout(() => { saveMessage.value = ''; }, 3000);
}

onMounted(async () => {
  const params = new URLSearchParams(window.location.search);
  error.value = params.get('error') || '';

  loadConfig();

  try {
    const me = await getCurrentUser();
    isAdmin.value = Boolean(me?.is_admin);
  } catch {
    isAdmin.value = false;
  }
});
</script>

<style scoped>
.api-config-section {
  margin-bottom: 24px;
  padding: 0;
  overflow: hidden;
}

.config-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  cursor: pointer;
  user-select: none;
  transition: background 0.2s;
}

.config-header:hover {
  background: var(--bg-hover, rgba(255, 255, 255, 0.05));
}

.config-title {
  display: flex;
  align-items: center;
  gap: 12px;
  font-weight: 500;
}

.config-status {
  font-size: 12px;
  padding: 2px 8px;
  border-radius: 12px;
  background: var(--bg-secondary, rgba(255, 255, 255, 0.1));
  color: var(--text-secondary);
}

.config-status.configured {
  background: rgba(34, 197, 94, 0.2);
  color: #22c55e;
}

.chevron {
  transition: transform 0.2s;
}

.chevron.expanded {
  transform: rotate(180deg);
}

.config-content {
  padding: 0 20px 20px;
  border-top: 1px solid var(--border-color, rgba(255, 255, 255, 0.1));
}

.config-desc {
  color: var(--text-secondary);
  font-size: 14px;
  margin: 16px 0;
}

.config-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.form-label {
  font-size: 13px;
  font-weight: 500;
  color: var(--text-secondary);
}

.input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.form-input {
  flex: 1;
  padding: 10px 40px 10px 12px;
  border: 1px solid var(--border-color, rgba(255, 255, 255, 0.15));
  border-radius: 8px;
  background: var(--bg-input, rgba(255, 255, 255, 0.05));
  color: var(--text-primary, #fff);
  font-size: 14px;
  transition: border-color 0.2s, box-shadow 0.2s;
}

.form-input:focus {
  outline: none;
  border-color: var(--accent-color, #3b82f6);
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.15);
}

.form-input::placeholder {
  color: var(--text-muted, rgba(255, 255, 255, 0.4));
}

.toggle-btn {
  position: absolute;
  right: 8px;
  padding: 6px;
  background: none;
  border: none;
  color: var(--text-secondary);
  cursor: pointer;
  opacity: 0.6;
  transition: opacity 0.2s;
}

.toggle-btn:hover {
  opacity: 1;
}

.btn-group {
  display: flex;
  gap: 12px;
  margin-top: 8px;
}

.btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  border: none;
}

.btn-primary {
  background: var(--accent-color, #3b82f6);
  color: white;
}

.btn-primary:hover {
  background: var(--accent-hover, #2563eb);
}

.btn-secondary {
  background: var(--bg-secondary, rgba(255, 255, 255, 0.1));
  color: var(--text-primary, #fff);
  border: 1px solid var(--border-color, rgba(255, 255, 255, 0.15));
}

.btn-secondary:hover {
  background: var(--bg-hover, rgba(255, 255, 255, 0.15));
}

.save-message {
  margin-top: 12px;
  padding: 10px 12px;
  border-radius: 6px;
  font-size: 13px;
}

.save-message.success {
  background: rgba(34, 197, 94, 0.15);
  color: #22c55e;
  border: 1px solid rgba(34, 197, 94, 0.3);
}

.save-message.error {
  background: rgba(239, 68, 68, 0.15);
  color: #ef4444;
  border: 1px solid rgba(239, 68, 68, 0.3);
}

.portal-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 24px;
  margin-top: 40px;
}

.portal-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px;
  text-align: center;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
  text-decoration: none;
  color: inherit;
}

.portal-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-md);
}

.portal-icon {
  width: 64px;
  height: 64px;
  margin-bottom: 20px;
  color: var(--accent-color);
}

.portal-title {
  font-size: 24px;
  font-weight: 600;
  margin-bottom: 8px;
}

.portal-desc {
  color: var(--text-secondary);
}

.error-banner {
  border: 1px solid rgba(255, 59, 48, 0.25);
  background: rgba(255, 59, 48, 0.06);
  color: #b42318;
}
</style>
