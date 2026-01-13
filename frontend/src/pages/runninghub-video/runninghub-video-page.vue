<template>
  <div class="video-page">
    <header class="header">
      <div class="logo">
        <div class="logo-icon">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2">
            <rect x="2" y="2" width="20" height="20" rx="2.18" ry="2.18"></rect>
            <polygon points="10 8 16 12 10 16" fill="white" stroke="none"/>
          </svg>
        </div>
        <span>RunningHub 图生视频</span>
      </div>
      <div class="header-actions">
        <a href="/" class="btn btn-secondary header-link">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M19 12H5M12 19l-7-7 7-7"/>
          </svg>
          返回主页面
        </a>
        <a href="/storage" class="btn btn-ghost btn-icon header-link" title="生成记录">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
            <polyline points="7 10 12 15 17 10"></polyline>
            <line x1="12" y1="15" x2="12" y2="3"></line>
          </svg>
        </a>
      </div>
    </header>

    <div class="main-container">
      <aside class="sidebar">
        <section class="sidebar-section config-section">
          <div
            class="section-title collapsible-header"
            :class="{ collapsed: sidebarCollapsed.config }"
            @click="toggleSidebarCollapsed('config')"
          >
            <span class="section-title-left">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M12 15a3 3 0 1 0 0-6 3 3 0 0 0 0 6Z"/>
                <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4"/>
              </svg>
              配置
            </span>
            <svg class="chevron" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="6 9 12 15 18 9"/>
            </svg>
          </div>
          <div class="collapsible-content" :class="{ collapsed: sidebarCollapsed.config }">
            <div class="config-content-inner">
              <div class="form-group">
                <label class="form-label">RunningHub Token（可选）</label>
                <div class="input-wrapper">
                  <input
                    :type="showToken ? 'text' : 'password'"
                    class="form-input"
                    v-model="config.token"
                    placeholder="后端已配置 RUNNINGHUB_API_KEY 可留空"
                    autocomplete="current-password"
                  >
                  <button class="toggle-visibility" type="button" @click="showToken = !showToken">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
                      <circle cx="12" cy="12" r="3"/>
                    </svg>
                  </button>
                </div>
                <div class="form-hint">请求头：Authorization: Bearer &lt;token&gt;</div>
              </div>
              <div class="form-group">
                <label class="checkbox-item">
                  <input type="checkbox" v-model="config.autoSave">
                  <span>生成成功后自动保存到存储库</span>
                </label>
              </div>
              <div class="form-group">
                <button class="btn btn-secondary btn-block" :disabled="generating" @click="saveConfig">
                  保存配置
                </button>
              </div>
            </div>
          </div>
        </section>

        <section class="sidebar-section config-section">
          <div
            class="section-title collapsible-header"
            :class="{ collapsed: sidebarCollapsed.params }"
            @click="toggleSidebarCollapsed('params')"
          >
            <span class="section-title-left">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <rect x="2" y="2" width="20" height="20" rx="2.18" ry="2.18"></rect>
                <line x1="7" y1="2" x2="7" y2="22"></line>
                <line x1="17" y1="2" x2="17" y2="22"></line>
              </svg>
              参数
            </span>
            <svg class="chevron" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="6 9 12 15 18 9"/>
            </svg>
          </div>
          <div class="collapsible-content" :class="{ collapsed: sidebarCollapsed.params }">
            <div class="config-content-inner">
              <div class="form-group">
                <label class="form-label">分辨率</label>
                <select class="form-select" v-model="form.resolution">
                  <option value="720p">720p</option>
                  <option value="1080p">1080p</option>
                </select>
              </div>
              <div class="form-group">
                <label class="form-label">画幅比例</label>
                <select class="form-select" v-model="form.aspectRatio">
                  <option value="16:9">16:9（横向）</option>
                  <option value="9:16">9:16（纵向）</option>
                </select>
              </div>
              <div class="form-group">
                <label class="form-label">时长（秒）</label>
                <select class="form-select" v-model.number="form.duration">
                  <option :value="4">4</option>
                  <option :value="8">8</option>
                  <option :value="12">12</option>
                </select>
              </div>
            </div>
          </div>
        </section>
      </aside>

      <main class="main-content">
        <div class="input-grid">
          <div class="content-panel">
            <div class="panel-header">
              <h3>输入提示词</h3>
              <span class="panel-hint">{{ form.prompt.length }}/1000 字符</span>
            </div>
            <textarea
              class="prompt-textarea"
              v-model="form.prompt"
              rows="6"
              maxlength="1000"
              placeholder="例如：一位女孩在海边，风吹动头发，写实风格..."
            ></textarea>
          </div>

          <div class="content-panel">
            <div class="panel-header">
              <h3>输入图片</h3>
              <span class="panel-hint">上传后自动填充 URL</span>
            </div>

            <div
              class="upload-zone"
              :class="{ disabled: uploading }"
              @dragenter.prevent
              @dragover.prevent
              @drop.prevent="onImageDrop"
            >
              <input
                ref="fileInputEl"
                class="sr-only"
                type="file"
                accept="image/png,image/jpeg"
                @change="onFileInputChange"
              />
              <div class="upload-zone-body">
                <div class="upload-title">拖拽 PNG/JPEG 到这里</div>
                <div class="upload-actions">
                  <button class="btn btn-secondary" type="button" :disabled="uploading" @click="openFilePicker">
                    {{ uploading ? '上传中…' : '选择图片上传' }}
                  </button>
                  <button class="btn btn-ghost" type="button" :disabled="uploading || !form.imageUrl.trim()" @click="clearImage">
                    清除
                  </button>
                </div>
                <div class="upload-hint">
                  RunningHub 需要可公网访问的 http(s) 地址；如果你的服务在公网，请使用上传生成的链接。
                </div>
              </div>
            </div>

            <div class="form-group image-url-group">
              <label class="form-label">图片 URL</label>
              <input
                class="form-input"
                v-model="form.imageUrl"
                placeholder="https://example.com/input.png"
              >
              <div class="image-tools">
                <button class="btn btn-ghost btn-small" type="button" :disabled="!form.imageUrl.trim()" @click="copyImageUrl">
                  复制链接
                </button>
              </div>
            </div>

            <div v-if="previewImageUrl" class="image-preview">
              <img :src="previewImageUrl" alt="input preview" />
            </div>
          </div>
        </div>

        <div class="result-area">
          <div class="result-placeholder" v-if="!generating && !result">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <rect x="2" y="2" width="20" height="20" rx="2.18" ry="2.18"></rect>
              <polygon points="10 8 16 12 10 16" />
            </svg>
            <h3>准备生成</h3>
            <p>填写提示词与图片 URL 后点击「生成视频」</p>
          </div>

          <div class="loading-state" v-if="generating">
            <div class="spinner"></div>
            <p>正在提交任务...</p>
          </div>

          <div v-if="result && !generating" class="result-container">
            <div class="content-panel result-meta-panel">
              <div class="panel-header">
                <h3>任务状态</h3>
                <span class="panel-hint">{{ result.status }}</span>
              </div>
              <div class="result-meta-grid">
                <div><span class="result-meta-label">task_id：</span>{{ result.task_id }}</div>
                <div v-if="result.prompt_tips"><span class="result-meta-label">prompt_tips：</span>{{ result.prompt_tips }}</div>
                <div v-if="result.error_message" class="result-meta-error"><span class="result-meta-label">error：</span>{{ result.error_message }}</div>
              </div>
            </div>

            <div v-if="videoUrl" class="result-video-container">
              <video :src="videoUrl" controls preload="metadata"></video>
            </div>

            <div class="result-actions" v-if="videoUrl">
              <button class="btn btn-secondary" @click="downloadVideo">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                  <polyline points="7 10 12 15 17 10"/>
                  <line x1="12" y1="15" x2="12" y2="3"/>
                </svg>
                下载
              </button>
              <button class="btn btn-secondary" :disabled="saving" @click="saveToRepository(true)">
                <span v-if="saving" class="loader loader-inline loader-dark" aria-label="saving"></span>
                <svg v-else width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"></path>
                  <polyline points="17 21 17 13 7 13 7 21"></polyline>
                  <polyline points="7 3 7 8 15 8"></polyline>
                </svg>
                {{ saving ? '保存中...' : '保存到存储库' }}
              </button>
            </div>

            <details class="content-panel raw-details">
              <summary class="raw-details-summary">查看原始响应</summary>
              <pre class="raw-details-pre">{{ JSON.stringify(result, null, 2) }}</pre>
            </details>
          </div>
        </div>

        <section class="main-prompt-section action-bar">
          <div class="prompt-footer">
            <div class="status-indicator">
              <span class="status-dot" :class="statusDotClass"></span>
              <span>{{ statusText }}</span>
            </div>
            <button
              class="generate-btn-large"
              :class="{ loading: generating }"
              :disabled="!canGenerate || generating"
              @click="generateVideo"
            >
              <span class="btn-text">生成视频</span>
              <span class="loader"></span>
            </button>
          </div>
        </section>
      </main>
    </div>

    <div class="toast-container">
      <div v-for="toast in toasts" :key="toast.id" class="toast" :class="toast.type">
        {{ toast.message }}
      </div>
    </div>

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
import { computed, onMounted, reactive, ref } from 'vue';
import { readErrorText } from '@/shared/http';
import { apiFetch, getUserId, supabase } from '@/shared/supabase';

type RunningHubResultItem = {
  url: string;
  output_type: string;
};

type RunningHubTaskSubmitResult = {
  task_id: string;
  status: string;
  error_code?: string | null;
  error_message?: string | null;
  results: RunningHubResultItem[];
  client_id?: string | null;
  prompt_tips?: string | null;
};

type ToastType = 'success' | 'error' | 'warning' | 'info';
type Toast = { id: string; message: string; type: ToastType };

const STORAGE_KEYS = {
  token: 'runninghub_token',
  autoSave: 'runninghub_auto_save'
};

const config = reactive({
  token: '',
  autoSave: true
});

const form = reactive({
  prompt: '',
  imageUrl: '',
  resolution: '1080p' as '720p' | '1080p',
  aspectRatio: '16:9' as '16:9' | '9:16',
  duration: 4 as 4 | 8 | 12
});

const showToken = ref(false);
const generating = ref(false);
const saving = ref(false);
const uploading = ref(false);
const result = ref<RunningHubTaskSubmitResult | null>(null);
const videoUrl = ref('');
const errorMessage = ref('');
const toasts = ref<Toast[]>([]);
const fileInputEl = ref<HTMLInputElement | null>(null);

const SIDEBAR_STORAGE_KEYS = {
  config: 'runninghub_sidebar_config_collapsed',
  params: 'runninghub_sidebar_params_collapsed',
} as const;

const sidebarCollapsed = reactive({
  config: true,
  params: false,
});

const canGenerate = computed(() => {
  return Boolean(form.prompt.trim()) && Boolean(form.imageUrl.trim());
});

const generateHint = computed(() => {
  if (!form.prompt.trim()) return '请输入提示词';
  if (!form.imageUrl.trim()) return '请输入图片 URL';
  return '';
});

const previewImageUrl = computed(() => {
  const value = form.imageUrl.trim();
  if (!value) return '';
  if (!/^https?:\/\//i.test(value)) return '';
  return value;
});

const statusText = computed(() => {
  if (generating.value) return '正在提交任务…';
  if (!canGenerate.value) return generateHint.value;
  return '准备就绪';
});

const statusDotClass = computed(() => {
  if (generating.value) return 'generating';
  if (!canGenerate.value) return 'error';
  return 'ready';
});

function loadSidebarState() {
  const savedConfig = localStorage.getItem(SIDEBAR_STORAGE_KEYS.config);
  const savedParams = localStorage.getItem(SIDEBAR_STORAGE_KEYS.params);

  sidebarCollapsed.config = savedConfig === null ? true : savedConfig === 'true';
  sidebarCollapsed.params = savedParams === null ? false : savedParams === 'true';
}

function toggleSidebarCollapsed(section: keyof typeof SIDEBAR_STORAGE_KEYS) {
  sidebarCollapsed[section] = !sidebarCollapsed[section];
  localStorage.setItem(SIDEBAR_STORAGE_KEYS[section], String(sidebarCollapsed[section]));
}

function openFilePicker() {
  fileInputEl.value?.click();
}

async function uploadImage(file: File) {
  uploading.value = true;
  try {
    const body = new FormData();
    body.append('image', file);

    const res = await apiFetch('/api/v1/uploads/runninghub/image', {
      method: 'POST',
      body,
    });
    if (!res.ok) throw new Error(await readErrorText(res));

    const payload = (await res.json()) as { image_url?: string };
    const url = String(payload?.image_url || '').trim();
    if (!url) throw new Error('上传失败：缺少 image_url');

    form.imageUrl = url;
    toast('图片上传成功', 'success');
  } catch (e: any) {
    toast(String(e?.message || e || '上传失败'), 'error');
  } finally {
    uploading.value = false;
  }
}

function onFileInputChange(event: Event) {
  const input = event.target as HTMLInputElement | null;
  const file = input?.files?.[0];
  if (input) input.value = '';
  if (!file) return;
  void uploadImage(file);
}

function onImageDrop(event: DragEvent) {
  const file = event.dataTransfer?.files?.[0];
  if (!file) return;
  void uploadImage(file);
}

function clearImage() {
  form.imageUrl = '';
}

async function copyImageUrl() {
  const value = form.imageUrl.trim();
  if (!value) return;
  try {
    await navigator.clipboard.writeText(value);
    toast('已复制图片链接', 'success');
  } catch {
    toast('复制失败，请手动复制', 'warning');
  }
}

function toast(message: string, type: ToastType = 'info', durationMs = 3000) {
  const id = `${Date.now()}-${Math.random().toString(16).slice(2)}`;
  const t: Toast = { id, message, type };
  toasts.value = [...toasts.value, t];
  window.setTimeout(() => {
    toasts.value = toasts.value.filter((x) => x.id !== id);
  }, durationMs);
}

function loadConfig() {
  config.token = localStorage.getItem(STORAGE_KEYS.token) || '';
  const savedAuto = localStorage.getItem(STORAGE_KEYS.autoSave);
  if (savedAuto === '0') config.autoSave = false;
}

function saveConfig() {
  localStorage.setItem(STORAGE_KEYS.token, config.token);
  localStorage.setItem(STORAGE_KEYS.autoSave, config.autoSave ? '1' : '0');
  toast('配置已保存', 'success');
}

function extractVideoUrl(res: RunningHubTaskSubmitResult): string {
  const url = res?.results?.[0]?.url || '';
  return String(url || '').trim();
}

async function saveToRepository(manual: boolean) {
  if (!videoUrl.value) {
    if (manual) toast('缺少视频链接，无法保存', 'warning');
    return;
  }

  saving.value = true;
  try {
    const requestPayload = {
      title: `RunningHub ${result.value?.task_id || ''}`.trim(),
      model: 'runninghub-video-s',
      prompt: form.prompt.trim(),
      video_url: videoUrl.value,
      status: 'completed',
      metadata: {
        provider: 'runninghub',
        provider_task_id: result.value?.task_id || null,
        resolution: form.resolution,
        aspect_ratio: form.aspectRatio,
        duration: form.duration,
        image_url: form.imageUrl.trim()
      },
      request: {
        prompt: form.prompt.trim(),
        resolution: form.resolution,
        aspect_ratio: form.aspectRatio,
        image_url: form.imageUrl.trim(),
        duration: form.duration
      },
      response: result.value
    };

    const userId = await getUserId();
    if (!userId) throw new Error('Not authenticated');

    const { error: insertError } = await supabase.from('user_videos').insert({
      user_id: userId,
      title: requestPayload.title,
      model: requestPayload.model,
      prompt: requestPayload.prompt,
      status: requestPayload.status,
      video_url: requestPayload.video_url,
      metadata: requestPayload.metadata,
      request: requestPayload.request,
      response: requestPayload.response,
    });
    if (insertError) throw new Error(insertError.message);

    toast('已保存到存储库', 'success');
  } catch (e: any) {
    const msg = String(e?.message || e || '保存失败');
    toast(`保存失败：${msg}`, 'error');
  } finally {
    saving.value = false;
  }
}

async function generateVideo() {
  if (!canGenerate.value || generating.value) return;

  generating.value = true;
  errorMessage.value = '';
  result.value = null;
  videoUrl.value = '';

  try {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    };
    if (config.token.trim()) {
      headers['X-RunningHub-Token'] = config.token.trim();
    }

    const res = await apiFetch('/api/v1/runninghub/image-to-video-realistic', {
      method: 'POST',
      headers,
      body: JSON.stringify({
        prompt: form.prompt.trim(),
        resolution: form.resolution,
        aspect_ratio: form.aspectRatio,
        image_url: form.imageUrl.trim(),
        duration: form.duration
      })
    });

    if (!res.ok) {
      throw new Error(await readErrorText(res));
    }

    const data = (await res.json()) as RunningHubTaskSubmitResult;
    result.value = data;

    const url = extractVideoUrl(data);
    if (url) {
      videoUrl.value = url;
      toast('生成成功', 'success');
      if (config.autoSave) {
        await saveToRepository(false);
      }
      return;
    }

    toast(`已提交任务（状态：${data.status}）`, 'info');
  } catch (e: any) {
    errorMessage.value = String(e?.message || e || '生成失败');
  } finally {
    generating.value = false;
  }
}

function downloadVideo() {
  if (!videoUrl.value) return;
  const a = document.createElement('a');
  a.href = videoUrl.value;
  a.download = `runninghub-${result.value?.task_id || 'video'}.mp4`;
  a.rel = 'noopener';
  document.body.appendChild(a);
  a.click();
  a.remove();
}

onMounted(() => {
  loadSidebarState();
  loadConfig();
});
</script>

<style scoped>
.input-grid {
  display: grid;
  gap: 16px;
}

@media (min-width: 1024px) {
  .input-grid {
    grid-template-columns: 1fr 1fr;
    align-items: start;
  }
}

.header-link {
  text-decoration: none;
}

.section-title-left {
  display: flex;
  align-items: center;
  gap: 8px;
}

.btn-block {
  width: 100%;
}

.checkbox-item {
  user-select: none;
}

.content-panel {
  background: var(--card-bg);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  padding: 18px 20px;
}

.panel-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
  flex-wrap: wrap;
  margin-bottom: 12px;
}

.panel-header h3 {
  font-size: 15px;
  font-weight: 600;
}

.panel-hint {
  font-size: 12px;
  color: var(--text-secondary);
}

.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}

.upload-zone {
  position: relative;
  border: 1px dashed var(--border-color);
  border-radius: var(--radius-md);
  background: rgba(0, 113, 227, 0.04);
  padding: 14px;
  transition: border-color 0.15s ease, background-color 0.15s ease, opacity 0.15s ease;
}

.upload-zone:hover {
  border-color: rgba(0, 113, 227, 0.45);
  background: rgba(0, 113, 227, 0.06);
}

.upload-zone.disabled {
  opacity: 0.65;
  pointer-events: none;
}

.upload-title {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 10px;
}

.upload-actions {
  display: flex;
  gap: 10px;
  align-items: center;
  flex-wrap: wrap;
}

.upload-hint {
  margin-top: 10px;
  font-size: 12px;
  color: var(--text-secondary);
  line-height: 1.45;
}

.image-url-group {
  margin-top: 12px;
}

.image-preview {
  margin-top: 12px;
}

.image-preview img {
  max-width: 100%;
  border-radius: 12px;
  display: block;
}

.image-tools {
  display: flex;
  justify-content: flex-end;
  margin-top: 8px;
}

.btn-small {
  padding: 6px 10px;
  font-size: 12px;
}

.result-meta-panel {
  margin-bottom: 16px;
}

.result-meta-grid {
  display: grid;
  gap: 8px;
  font-size: 13px;
  color: var(--text-secondary);
}

.result-meta-label {
  color: var(--text-muted);
}

.result-meta-error {
  color: #ef4444;
}

.raw-details {
  margin-top: 16px;
}

.raw-details-summary {
  cursor: pointer;
  font-weight: 500;
}

.raw-details-pre {
  white-space: pre-wrap;
  margin-top: 12px;
  font-size: 12px;
  color: var(--text-secondary);
  background: var(--bg-color);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-sm);
  padding: 12px;
  max-height: 260px;
  overflow: auto;
}

.loader.loader-inline {
  display: inline-block;
}

.loader-dark {
  border-color: var(--text-secondary);
  border-bottom-color: transparent;
}

.error-overlay {
  position: fixed;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
  background: rgba(0, 0, 0, 0.45);
  z-index: 1000;
}

.error-modal {
  width: min(520px, 100%);
  background: var(--card-bg);
  border: 1px solid rgba(209, 209, 214, 0.65);
  border-radius: var(--radius-md);
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.25);
  padding: 18px 18px 16px;
}

.error-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
}

.error-header h3 {
  font-size: 16px;
  font-weight: 700;
}

.error-modal p {
  margin: 0 0 14px;
  color: var(--text-secondary);
  line-height: 1.5;
}
</style>
