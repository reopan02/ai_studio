<template>
  <div class="container portal-container">
    <!-- SVG Gradient Definitions -->
    <svg width="0" height="0" style="position: absolute;">
      <defs>
        <linearGradient id="grad-video" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stop-color="#8B5CF6"/>
          <stop offset="100%" stop-color="#3B82F6"/>
        </linearGradient>
        <linearGradient id="grad-image-gen" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stop-color="#3B82F6"/>
          <stop offset="100%" stop-color="#06B6D4"/>
        </linearGradient>
        <linearGradient id="grad-ecommerce" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stop-color="#F97316"/>
          <stop offset="100%" stop-color="#EC4899"/>
        </linearGradient>
        <linearGradient id="grad-products" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stop-color="#10B981"/>
          <stop offset="100%" stop-color="#06B6D4"/>
        </linearGradient>
        <linearGradient id="grad-storage" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stop-color="#3B82F6"/>
          <stop offset="100%" stop-color="#8B5CF6"/>
        </linearGradient>
        <linearGradient id="grad-image-edit" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stop-color="#EC4899"/>
          <stop offset="100%" stop-color="#8B5CF6"/>
        </linearGradient>
        <linearGradient id="grad-runninghub-video" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stop-color="#06B6D4"/>
          <stop offset="100%" stop-color="#8B5CF6"/>
        </linearGradient>
        <linearGradient id="grad-admin" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stop-color="#64748B"/>
          <stop offset="100%" stop-color="#3B82F6"/>
        </linearGradient>
      </defs>
    </svg>

    <header class="portal-header">
      <h1>AI 创作工作室</h1>
      <p>请选择功能模块</p>
      <div class="portal-auth-row">
        <span v-if="userEmail" class="portal-user-email">{{ userEmail }}</span>
        <button class="btn btn-secondary" type="button" @click="logout">退出登录</button>
      </div>
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

    <!-- AI 生成 Section -->
    <section class="portal-section">
      <div class="section-header section-header-purple">
        <span class="section-label">AI 生成</span>
      </div>
      <div class="portal-grid">
        <a href="/video" class="card portal-card portal-card-video">
          <svg class="portal-icon" viewBox="0 0 24 24" fill="url(#grad-video)" stroke="none">
            <rect x="2" y="2" width="20" height="20" rx="3"/>
            <polygon points="10 8 16 12 10 16" fill="white"/>
          </svg>
          <div class="portal-title">AI 视频</div>
          <div class="portal-desc">Sora、Veo、Seedance 等模型</div>
        </a>

        <a href="/runninghub-video" class="card portal-card portal-card-runninghub-video">
          <svg class="portal-icon" viewBox="0 0 24 24" fill="url(#grad-runninghub-video)" stroke="none">
            <rect x="2" y="2" width="20" height="20" rx="3"/>
            <path d="M7 16h10l-2 3H9l-2-3z" fill="white" opacity="0.9"/>
            <path d="M8 13l2-5h4l2 5H8z" fill="white"/>
            <circle cx="12" cy="6.5" r="1.5" fill="white" opacity="0.85"/>
          </svg>
          <div class="portal-title">全能视频 S</div>
          <div class="portal-desc">RunningHub 图生视频（支持真人）</div>
        </a>

        <a href="/image-generate" class="card portal-card portal-card-image-gen">
          <svg class="portal-icon" viewBox="0 0 24 24" fill="url(#grad-image-gen)" stroke="none">
            <rect x="2" y="2" width="20" height="20" rx="3"/>
            <circle cx="8" cy="8" r="2" fill="white"/>
            <path d="M22 16l-5-5-8 8h11a2 2 0 0 0 2-2v-1z" fill="white" opacity="0.8"/>
          </svg>
          <div class="portal-title">AI 图像</div>
          <div class="portal-desc">文字描述生成图像</div>
        </a>

        <a href="/ecommerce-image" class="card portal-card portal-card-ecommerce">
          <svg class="portal-icon" viewBox="0 0 24 24" fill="url(#grad-ecommerce)" stroke="none">
            <rect x="2" y="2" width="20" height="20" rx="3"/>
            <rect x="6" y="10" width="12" height="8" rx="1" fill="white"/>
            <circle cx="9" cy="18" r="1.5" fill="white"/>
            <circle cx="15" cy="18" r="1.5" fill="white"/>
            <path d="M8 6h8l1 4H7l1-4z" fill="white"/>
          </svg>
          <div class="portal-title">电商图片</div>
          <div class="portal-desc">基于产品素材快速生成</div>
        </a>
      </div>
    </section>

    <!-- 资产管理 Section -->
    <section class="portal-section">
      <div class="section-header section-header-green">
        <span class="section-label">资产管理</span>
      </div>
      <div class="portal-grid">
        <a href="/products" class="card portal-card portal-card-products">
          <svg class="portal-icon" viewBox="0 0 24 24" fill="url(#grad-products)" stroke="none">
            <rect x="2" y="4" width="20" height="16" rx="3"/>
            <rect x="5" y="8" width="6" height="8" rx="1" fill="white"/>
            <rect x="13" y="8" width="6" height="8" rx="1" fill="white"/>
            <rect x="8" y="2" width="8" height="4" rx="1" fill="white" opacity="0.8"/>
          </svg>
          <div class="portal-title">产品素材库</div>
          <div class="portal-desc">产品图片识别与管理</div>
        </a>

        <a href="/storage" class="card portal-card portal-card-storage">
          <svg class="portal-icon" viewBox="0 0 24 24" fill="url(#grad-storage)" stroke="none">
            <rect x="2" y="2" width="20" height="20" rx="3"/>
            <rect x="5" y="6" width="14" height="3" rx="1" fill="white"/>
            <rect x="5" y="11" width="14" height="3" rx="1" fill="white" opacity="0.7"/>
            <rect x="5" y="16" width="14" height="3" rx="1" fill="white" opacity="0.5"/>
          </svg>
          <div class="portal-title">生成记录</div>
          <div class="portal-desc">查看历史生成内容</div>
        </a>

        <a href="/image" class="card portal-card portal-card-image-edit">
          <svg class="portal-icon" viewBox="0 0 24 24" fill="url(#grad-image-edit)" stroke="none">
            <rect x="2" y="2" width="20" height="20" rx="3"/>
            <circle cx="8" cy="8" r="2" fill="white"/>
            <path d="M22 16l-5-5-8 8h11a2 2 0 0 0 2-2v-1z" fill="white" opacity="0.8"/>
            <path d="M18 4l2 2-8 8-2-2 8-8z" fill="white"/>
          </svg>
          <div class="portal-title">图像编辑</div>
          <div class="portal-desc">多图参考编辑 (Gemini)</div>
        </a>
      </div>
    </section>

  </div>
</template>

<script setup lang="ts">
import { onMounted, ref, computed } from 'vue';
import { getCurrentUser } from '@/shared/auth';
import { supabase } from '@/shared/supabase';

// Global storage keys used by all pages
const STORAGE_KEYS = {
  apiKey: 'global_api_key',
  baseUrl: 'global_base_url'
};

const error = ref<string>('');
const userEmail = ref<string | null>(null);
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

async function logout() {
  await supabase.auth.signOut();
  window.location.href = '/login';
}

onMounted(async () => {
  const params = new URLSearchParams(window.location.search);
  error.value = params.get('error') || '';

  loadConfig();

  try {
    const me = await getCurrentUser();
    userEmail.value = me?.email ?? null;
  } catch {
    userEmail.value = null;
  }
});
</script>

<style scoped>
/* Portal Container */
.portal-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 40px 24px;
}

/* Portal Header */
.portal-header {
  text-align: center;
  margin-bottom: 32px;
}

.portal-header h1 {
  font-size: 36px;
  font-weight: 700;
  letter-spacing: -0.5px;
  background: linear-gradient(135deg, #8B5CF6, #3B82F6);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-bottom: 8px;
}

.portal-header p {
  color: var(--text-secondary);
  font-size: 16px;
}

.portal-auth-row {
  display: flex;
  justify-content: center;
  gap: 12px;
  margin-top: 12px;
  align-items: center;
}

.portal-user-email {
  font-size: 13px;
  color: var(--text-secondary);
}

/* API Config Section */
.api-config-section {
  margin-bottom: 32px;
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

/* Portal Section */
.portal-section {
  margin-bottom: 40px;
}

.section-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
  padding-left: 16px;
  position: relative;
}

.section-header::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 4px;
  height: 20px;
  border-radius: 2px;
}

.section-header-purple::before {
  background: linear-gradient(135deg, #8B5CF6, #3B82F6);
}

.section-header-green::before {
  background: linear-gradient(135deg, #10B981, #06B6D4);
}

.section-header-gray::before {
  background: linear-gradient(135deg, #64748B, #3B82F6);
}

.section-label {
  font-size: 14px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 1px;
  color: var(--text-secondary);
}

.section-tag {
  font-size: 11px;
  padding: 2px 8px;
  border-radius: 10px;
  background: rgba(100, 116, 139, 0.2);
  color: var(--text-muted);
}

/* Portal Grid */
.portal-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(360px, 1fr));
  gap: 28px;
}

/* Portal Card */
.portal-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 48px 32px;
  text-align: center;
  cursor: pointer;
  transition: transform 0.25s ease, box-shadow 0.25s ease, background 0.25s ease;
  text-decoration: none;
  color: inherit;
  border-radius: 16px;
  position: relative;
  overflow: hidden;
}

.portal-card::before {
  content: '';
  position: absolute;
  inset: 0;
  opacity: 0;
  transition: opacity 0.25s ease;
  border-radius: 16px;
}

.portal-card-video::before {
  background: linear-gradient(135deg, rgba(139, 92, 246, 0.08), rgba(59, 130, 246, 0.08));
}

.portal-card-image-gen::before {
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.08), rgba(6, 182, 212, 0.08));
}

.portal-card-ecommerce::before {
  background: linear-gradient(135deg, rgba(249, 115, 22, 0.08), rgba(236, 72, 153, 0.08));
}

.portal-card-products::before {
  background: linear-gradient(135deg, rgba(16, 185, 129, 0.08), rgba(6, 182, 212, 0.08));
}

.portal-card-storage::before {
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.08), rgba(139, 92, 246, 0.08));
}

.portal-card-image-edit::before {
  background: linear-gradient(135deg, rgba(236, 72, 153, 0.08), rgba(139, 92, 246, 0.08));
}

.portal-card-runninghub-video::before {
  background: linear-gradient(135deg, rgba(6, 182, 212, 0.08), rgba(139, 92, 246, 0.08));
}

.portal-card-admin::before {
  background: linear-gradient(135deg, rgba(100, 116, 139, 0.08), rgba(59, 130, 246, 0.08));
}

.portal-card:hover {
  transform: translateY(-6px);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
}

.portal-card:hover::before {
  opacity: 1;
}

.portal-icon {
  width: 80px;
  height: 80px;
  margin-bottom: 24px;
  position: relative;
  z-index: 1;
}

.portal-title {
  font-size: 26px;
  font-weight: 600;
  margin-bottom: 10px;
  letter-spacing: 0.5px;
  position: relative;
  z-index: 1;
}

.portal-desc {
  color: var(--text-secondary);
  font-size: 15px;
  position: relative;
  z-index: 1;
}

.error-banner {
  border: 1px solid rgba(255, 59, 48, 0.25);
  background: rgba(255, 59, 48, 0.06);
  color: #b42318;
}

/* Responsive */
@media (max-width: 1199px) {
  .portal-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 767px) {
  .portal-container {
    padding: 24px 16px;
  }

  .portal-header h1 {
    font-size: 28px;
  }

  .portal-grid {
    grid-template-columns: 1fr;
  }

  .portal-card {
    padding: 36px 24px;
  }

  .portal-icon {
    width: 64px;
    height: 64px;
  }

  .portal-title {
    font-size: 22px;
  }

  .section-header {
    padding-left: 12px;
  }

  .section-label {
    font-size: 13px;
  }
}
</style>
