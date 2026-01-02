<template>
  <div class="products-page">
    <div class="container">
      <header class="products-header">
        <div class="header-left">
          <a href="/" class="btn btn-secondary" style="text-decoration: none">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M19 12H5M12 19l-7-7 7-7" />
            </svg>
            返回首页
          </a>
          <div>
            <h1 style="margin: 0; text-align: left">产品库</h1>
            <div class="meta-text">上传产品图片，AI识别后可手动修正</div>
          </div>
        </div>
        <div class="header-actions">
          <a href="/video" class="btn btn-secondary" style="text-decoration: none">视频</a>
          <a href="/image" class="btn btn-secondary" style="text-decoration: none">图片</a>
          <a href="/storage" class="btn btn-secondary" style="text-decoration: none">存储</a>
          <a v-if="isAdmin" href="/admin" class="btn btn-secondary" style="text-decoration: none">Admin</a>
        </div>
      </header>

      <section v-if="errorMessage" class="card error-banner" style="margin-bottom: 18px">
        {{ errorMessage }}
      </section>

      <section v-if="successMessage" class="card success-banner" style="margin-bottom: 18px">
        {{ successMessage }}
      </section>

      <section class="card">
        <div class="card-title-row">
          <h2 style="margin: 0">{{ isEditing ? '编辑产品信息' : '上传新产品' }}</h2>
          <div class="card-actions">
            <button v-if="isEditing" class="btn btn-secondary btn-sm" type="button" @click="resetForm">
              取消编辑
            </button>
          </div>
        </div>

        <div class="form-grid image-grid" style="margin-top: 16px">
          <div class="form-group">
            <label>产品图片</label>
            <div
              class="dropzone"
              :class="{ 'is-dragover': isDragOver, 'is-loading': saving || prefilling, 'is-disabled': isEditing }"
              @click.stop="triggerFilePicker"
              @dragenter.prevent="handleDragEnter"
              @dragover.prevent="handleDragOver"
              @dragleave.prevent="handleDragLeave"
              @drop.prevent="handleDrop"
            >
              <input
                ref="fileInput"
                type="file"
                accept="image/jpeg,image/png"
                multiple
                :disabled="isEditing"
                @change="handleFileChange"
              />
              <div class="dropzone-inner">
                <div class="dropzone-icon">
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                    <polyline points="17 8 12 3 7 8" />
                    <line x1="12" y1="3" x2="12" y2="15" />
                  </svg>
                </div>
                <div>
                  <div class="dropzone-title">拖拽或点击上传多张产品图</div>
                  <div class="dropzone-subtitle">主图用于 AI 识别与列表展示</div>
                </div>
                <div class="dropzone-actions">
                  <button class="btn btn-secondary btn-sm" type="button" :disabled="isEditing" @click.stop="triggerFilePicker">
                    选择图片
                  </button>
                  <button
                    v-if="selectedImages.length > 0"
                    class="btn btn-ghost btn-sm"
                    type="button"
                    @click.stop="clearSelectedImages"
                  >
                    清空
                  </button>
                </div>
              </div>
            </div>
            <div class="form-hint">
              支持 JPG/PNG；可一次上传多张产品图，主图用于 AI 识别（大图会自动压缩用于识别，不影响原图存储）
            </div>
          </div>

          <div class="form-group">
            <label>主图预览</label>
            <div class="preview-box">
              <img v-if="primaryPreviewUrl" :src="primaryPreviewUrl" alt="preview" class="preview-image" />
              <div v-else class="preview-placeholder">未选择图片</div>
            </div>
            <div v-if="recognitionConfidence !== null" class="form-hint">
              AI 置信度：{{ Math.round(recognitionConfidence * 100) }}%
            </div>
          </div>
        </div>

        <div v-if="displayImageCount > 0" class="image-meta">
          <span class="meta-text">已选择 {{ displayImageCount }} 张图片</span>
          <span v-if="isEditing && selectedImages.length === 0" class="meta-text">编辑模式下图片不可替换</span>
        </div>

        <div v-if="selectedImages.length > 0" class="image-preview-grid product-image-grid">
          <div
            v-for="(img, index) in selectedImages"
            :key="img.id"
            class="preview-item"
            :class="{ 'is-primary': index === primaryIndex }"
          >
            <img :src="img.url" :alt="`image-${index + 1}`" class="preview-img" />
            <div v-if="index === primaryIndex" class="preview-badge">主图</div>
            <div class="preview-actions">
              <button
                v-if="index !== primaryIndex"
                class="preview-action-btn"
                type="button"
                @click="setPrimary(index)"
              >
                设为主图
              </button>
              <button class="preview-action-btn danger" type="button" @click="removeSelectedImage(index)">移除</button>
            </div>
          </div>
        </div>

        <div v-else-if="existingImages.length > 0" class="image-preview-grid product-image-grid">
          <div
            v-for="img in existingImages"
            :key="img.id"
            class="preview-item"
            :class="{ 'is-primary': img.is_primary }"
          >
            <img :src="img.image_url" :alt="img.id" class="preview-img" />
            <div v-if="img.is_primary" class="preview-badge">主图</div>
          </div>
        </div>

        <div class="form-grid" style="margin-top: 8px">
          <div class="form-group">
            <label>产品名称</label>
            <input v-model="form.name" type="text" maxlength="200" placeholder="例如：保温杯" />
          </div>
          <div class="form-group">
            <label>尺寸规格</label>
            <input v-model="form.dimensions" type="text" maxlength="100" placeholder="例如：350ml" />
          </div>
        </div>

        <div class="form-group" style="margin-top: 8px">
          <label>无结构化信息（可选）</label>
          <textarea
            v-model="form.rawText"
            rows="3"
            :disabled="isEditing"
            placeholder="粘贴产品信息，例如从商品页面复制的描述文本，AI会结合图片提取结构化信息"></textarea>
          <div class="form-hint">
            提供此信息可帮助AI更准确地识别产品属性
          </div>
        </div>

        <div class="form-grid" style="margin-top: 8px">
          <div class="form-group">
            <label>功能特征（每行一个）</label>
            <textarea v-model="form.featuresText" rows="5" placeholder="例如：&#10;24小时保温&#10;不锈钢内胆"></textarea>
          </div>
          <div class="form-group">
            <label>产品特点（每行一个）</label>
            <textarea v-model="form.characteristicsText" rows="5" placeholder="例如：&#10;便携&#10;大容量"></textarea>
          </div>
        </div>

        <div class="form-actions">
          <button
            v-if="!isEditing"
            class="btn btn-secondary"
            type="button"
            :disabled="saving || prefilling"
            @click="aiPrefillProduct"
          >
            {{ prefilling ? 'AI整理中...' : 'AI整理预填' }}
          </button>
          <button v-if="!isEditing" class="btn btn-primary" type="button" :disabled="saving || prefilling" @click="createProduct">
            {{ saving ? '保存中...' : '保存产品' }}
          </button>
          <button v-else class="btn btn-primary" type="button" :disabled="saving" @click="updateProduct">
            {{ saving ? '保存中...' : '保存修改' }}
          </button>
        </div>
      </section>

      <section class="card">
        <div class="card-title-row">
          <h2 style="margin: 0">我的产品</h2>
          <div class="card-actions">
            <input
              v-model="searchQuery"
              type="text"
              placeholder="搜索名称..."
              style="width: 260px; max-width: 100%"
              @input="debouncedSearch"
            />
          </div>
        </div>

        <div v-if="loading" class="loading">加载中...</div>

        <div v-else>
          <div v-if="products.length === 0" class="empty-state">暂无产品</div>

          <div v-else class="products-grid">
            <div v-for="p in products" :key="p.id" class="product-card">
              <div class="product-thumb">
                <img :src="p.original_image_url" :alt="p.name" />
                <span v-if="p.image_count > 1" class="image-count-badge">{{ p.image_count }} 张</span>
              </div>
              <div class="product-body">
                <div class="product-title">{{ p.name }}</div>
                <div class="product-meta">
                  <span v-if="p.dimensions">{{ p.dimensions }}</span>
                  <span v-if="p.image_count > 1">· {{ p.image_count }} 张</span>
                  <span v-if="p.created_at">· {{ formatDate(p.created_at) }}</span>
                </div>
                <div class="product-meta" v-if="p.recognition_confidence !== null">
                  AI：{{ Math.round((p.recognition_confidence ?? 0) * 100) }}%
                </div>
                <div class="product-actions">
                  <button class="btn btn-secondary btn-sm" type="button" :disabled="saving" @click="editProduct(p.id)">
                    编辑
                  </button>
                  <button
                    class="btn btn-secondary btn-sm danger"
                    type="button"
                    :disabled="saving"
                    @click="deleteProduct(p.id)"
                  >
                    删除
                  </button>
                </div>
              </div>
            </div>
          </div>

          <div v-if="total > limit" class="pagination">
            <button class="btn btn-secondary btn-sm" type="button" :disabled="offset === 0 || saving" @click="prevPage">
              上一页
            </button>
            <span class="meta-text">
              第 {{ Math.floor(offset / limit) + 1 }} / {{ Math.max(1, Math.ceil(total / limit)) }} 页（{{ total }} 条）
            </span>
            <button
              class="btn btn-secondary btn-sm"
              type="button"
              :disabled="offset + limit >= total || saving"
              @click="nextPage"
            >
              下一页
            </button>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue';
import { getCurrentUser } from '@/shared/auth';
import { csrfHeaders } from '@/shared/csrf';

type ProductSummary = {
  id: string;
  user_id: string;
  name: string;
  dimensions: string | null;
  original_image_url: string;
  recognition_confidence: number | null;
  image_size_bytes: number;
  image_count: number;
  created_at: string;
  updated_at: string | null;
};

type ProductImage = {
  id: string;
  image_url: string;
  image_size_bytes: number;
  is_primary: boolean;
  created_at: string;
  updated_at: string | null;
};

type ProductDetail = ProductSummary & {
  features: string[] | null;
  characteristics: string[] | null;
  recognition_metadata?: Record<string, unknown> | null;
  images: ProductImage[];
};

type SelectedImage = {
  id: string;
  file: File;
  url: string;
};

type ProductRecognitionResponse = {
  name: string;
  dimensions: string | null;
  features: string[];
  characteristics: string[];
  confidence: number;
  metadata?: Record<string, unknown> | null;
};

type ProductListResponse = {
  products: ProductSummary[];
  total: number;
  offset: number;
  limit: number;
};

const isAdmin = ref(false);

const products = ref<ProductSummary[]>([]);
const loading = ref(false);
const saving = ref(false);
const errorMessage = ref('');
const successMessage = ref('');

const offset = ref(0);
const limit = ref(20);
const total = ref(0);
const searchQuery = ref('');
let searchTimer: number | null = null;

const fileInput = ref<HTMLInputElement | null>(null);
const isDragOver = ref(false);
const selectedImages = ref<SelectedImage[]>([]);
const existingImages = ref<ProductImage[]>([]);
const primaryIndex = ref(0);
const editingProductId = ref<string | null>(null);
const recognitionConfidence = ref<number | null>(null);
const prefilling = ref(false);
const previewRecognitionData = ref<{ confidence: number; metadata: Record<string, unknown> } | null>(null);

const form = reactive({
  name: '',
  dimensions: '',
  featuresText: '',
  characteristicsText: '',
  rawText: '',
});

const isEditing = computed(() => Boolean(editingProductId.value));
const primarySelectedImage = computed(() => selectedImages.value[primaryIndex.value] ?? null);
const primaryExistingImage = computed(
  () => existingImages.value.find((img) => img.is_primary) ?? existingImages.value[0] ?? null
);
const primaryPreviewUrl = computed(
  () => primarySelectedImage.value?.url || primaryExistingImage.value?.image_url || null
);
const displayImageCount = computed(() =>
  selectedImages.value.length > 0 ? selectedImages.value.length : existingImages.value.length
);

function clearMessages() {
  errorMessage.value = '';
  successMessage.value = '';
}

function setError(message: string) {
  errorMessage.value = message;
  successMessage.value = '';
}

function setSuccess(message: string) {
  successMessage.value = message;
  errorMessage.value = '';
}

function formatDate(isoString: string): string {
  try {
    return new Date(isoString).toLocaleString();
  } catch {
    return isoString;
  }
}

function toLines(text: string): string[] {
  return text
    .split('\n')
    .map((x) => x.trim())
    .filter(Boolean);
}

function resetRecognitionPreview() {
  recognitionConfidence.value = null;
  previewRecognitionData.value = null;
}

function releaseSelectedImages() {
  for (const image of selectedImages.value) {
    if (image.url.startsWith('blob:')) {
      URL.revokeObjectURL(image.url);
    }
  }
}

function generateImageId(): string {
  if (globalThis.crypto && 'randomUUID' in globalThis.crypto) {
    return globalThis.crypto.randomUUID();
  }
  return `${Date.now()}-${Math.random().toString(16).slice(2)}`;
}

function isSupportedImage(file: File): boolean {
  const type = file.type.toLowerCase();
  if (type === 'image/jpeg' || type === 'image/png') return true;
  const name = file.name.toLowerCase();
  return name.endsWith('.jpg') || name.endsWith('.jpeg') || name.endsWith('.png');
}

function addFiles(fileList: FileList | File[]) {
  if (isEditing.value) {
    setError('编辑模式下无法更换图片');
    return;
  }

  const files = Array.from(fileList);
  if (files.length === 0) return;

  clearMessages();

  let rejected = 0;
  for (const file of files) {
    if (!isSupportedImage(file)) {
      rejected += 1;
      continue;
    }
    const url = URL.createObjectURL(file);
    selectedImages.value.push({
      id: generateImageId(),
      file,
      url,
    });
  }

  if (selectedImages.value.length > 0) {
    primaryIndex.value = Math.min(primaryIndex.value, selectedImages.value.length - 1);
    editingProductId.value = null;
    existingImages.value = [];
    resetRecognitionPreview();
  }

  if (rejected > 0) {
    setError('仅支持 JPG/PNG 图片');
  }
}

function triggerFilePicker() {
  if (isEditing.value) return;
  fileInput.value?.click();
}

function handleDragEnter() {
  if (isEditing.value) return;
  isDragOver.value = true;
}

function handleDragOver() {
  if (isEditing.value) return;
  isDragOver.value = true;
}

function handleDragLeave() {
  isDragOver.value = false;
}

function handleDrop(event: DragEvent) {
  if (isEditing.value) return;
  isDragOver.value = false;
  if (event.dataTransfer?.files) {
    addFiles(event.dataTransfer.files);
  }
}

function clearSelectedImages() {
  releaseSelectedImages();
  selectedImages.value = [];
  primaryIndex.value = 0;
  resetRecognitionPreview();
}

function removeSelectedImage(index: number) {
  const [removed] = selectedImages.value.splice(index, 1);
  if (removed?.url?.startsWith('blob:')) {
    URL.revokeObjectURL(removed.url);
  }

  if (selectedImages.value.length === 0) {
    primaryIndex.value = 0;
  } else if (index === primaryIndex.value) {
    primaryIndex.value = 0;
  } else if (index < primaryIndex.value) {
    primaryIndex.value -= 1;
  }

  resetRecognitionPreview();
}

function setPrimary(index: number) {
  if (index < 0 || index >= selectedImages.value.length) return;
  primaryIndex.value = index;
  resetRecognitionPreview();
}

function handleFileChange(event: Event) {
  const input = event.target as HTMLInputElement;
  if (!input.files) return;
  addFiles(input.files);
  input.value = '';
}

async function readApiError(res: Response): Promise<string> {
  const text = await res.text();
  try {
    const data = JSON.parse(text);
    const detail = data?.detail ?? data?.error ?? data?.message ?? text;
    if (typeof detail === 'string') return detail;
    if (detail && typeof detail === 'object') {
      const msg = (detail as Record<string, unknown>)?.message;
      if (typeof msg === 'string') return msg;
      return JSON.stringify(detail);
    }
    return String(detail || `HTTP ${res.status}`);
  } catch {
    return text || `HTTP ${res.status}`;
  }
}

async function apiFetch(input: RequestInfo | URL, init: RequestInit = {}) {
  const method = (init.method || 'GET').toUpperCase();
  const headers = new Headers(init.headers || {});
  if (!['GET', 'HEAD', 'OPTIONS'].includes(method)) {
    for (const [k, v] of Object.entries(csrfHeaders())) headers.set(k, v);
  }
  return fetch(input, {
    ...init,
    headers,
    credentials: 'include',
  });
}

async function loadProducts() {
  loading.value = true;
  try {
    const params = new URLSearchParams();
    params.set('offset', String(offset.value));
    params.set('limit', String(limit.value));
    if (searchQuery.value.trim()) params.set('name', searchQuery.value.trim());

    const res = await apiFetch(`/api/v1/products?${params.toString()}`);
    if (!res.ok) throw new Error(await readApiError(res));

    const data = (await res.json()) as ProductListResponse;
    products.value = data.products;
    total.value = data.total;
    offset.value = data.offset;
    limit.value = data.limit;
  } catch (e) {
    setError((e as Error).message || String(e));
  } finally {
    loading.value = false;
  }
}

async function loadProductDetail(productId: string): Promise<ProductDetail> {
  const res = await apiFetch(`/api/v1/products/${productId}`);
  if (!res.ok) throw new Error(await readApiError(res));
  return (await res.json()) as ProductDetail;
}

function resetForm() {
  clearMessages();
  releaseSelectedImages();
  selectedImages.value = [];
  existingImages.value = [];
  primaryIndex.value = 0;
  isDragOver.value = false;
  editingProductId.value = null;
  resetRecognitionPreview();
  form.name = '';
  form.dimensions = '';
  form.featuresText = '';
  form.characteristicsText = '';
  form.rawText = '';
}

async function aiPrefillProduct() {
  clearMessages();

  if (!primarySelectedImage.value) {
    setError('请先选择图片');
    return;
  }

  prefilling.value = true;
  try {
    const fd = new FormData();
    fd.append('image', primarySelectedImage.value.file);
    const rawText = form.rawText.trim();
    if (rawText) fd.append('raw_text', rawText);

    const res = await apiFetch('/api/v1/products/recognize', { method: 'POST', body: fd });
    if (!res.ok) throw new Error(await readApiError(res));

    const recognized = (await res.json()) as ProductRecognitionResponse;

    // Prefill form fields with AI recognition results
    form.name = recognized.name || '';
    form.dimensions = recognized.dimensions || '';
    form.featuresText = (recognized.features || []).join('\n');
    form.characteristicsText = (recognized.characteristics || []).join('\n');

    // Store preview recognition data for later use in save
    recognitionConfidence.value = recognized.confidence;
    previewRecognitionData.value = {
      confidence: recognized.confidence,
      metadata: recognized.metadata || {},
    };

    setSuccess(
      `AI整理完成（置信度：${Math.round(recognized.confidence * 100)}%），可编辑后保存`
    );
  } catch (e) {
    setError((e as Error).message || String(e));
  } finally {
    prefilling.value = false;
  }
}

async function createProduct() {
  clearMessages();

  if (selectedImages.value.length === 0) {
    setError('请先选择图片');
    return;
  }

  saving.value = true;
  try {
    const fd = new FormData();
    for (const image of selectedImages.value) {
      fd.append('images', image.file);
    }
    fd.append('primary_index', String(primaryIndex.value));
    const name = form.name.trim();
    if (name) fd.append('name', name);
    if (form.dimensions.trim()) fd.append('dimensions', form.dimensions.trim());

    const features = toLines(form.featuresText);
    const characteristics = toLines(form.characteristicsText);
    if (features.length) fd.append('features', JSON.stringify(features));
    if (characteristics.length) fd.append('characteristics', JSON.stringify(characteristics));

    // If we have preview recognition data, use prefill mode
    // Otherwise, use manual mode to skip AI (user may have filled fields manually)
    if (previewRecognitionData.value) {
      fd.append('recognition_mode', 'prefill');
      fd.append('recognition_confidence', String(previewRecognitionData.value.confidence));
      fd.append('recognition_metadata_json', JSON.stringify(previewRecognitionData.value.metadata));
    } else {
      fd.append('recognition_mode', 'manual');
    }

    const res = await apiFetch('/api/v1/products', { method: 'POST', body: fd });
    if (!res.ok) throw new Error(await readApiError(res));

    const created = (await res.json()) as ProductDetail;
    setSuccess(
      `创建成功（AI：${Math.round(((created.recognition_confidence ?? 0) as number) * 100)}%），可继续编辑后保存`
    );

    editingProductId.value = created.id;
    recognitionConfidence.value = created.recognition_confidence ?? 0.0;
    previewRecognitionData.value = null;
    releaseSelectedImages();
    selectedImages.value = [];
    primaryIndex.value = 0;
    existingImages.value = created.images || [];

    form.name = created.name || '';
    form.dimensions = created.dimensions || '';
    form.featuresText = (created.features || []).join('\n');
    form.characteristicsText = (created.characteristics || []).join('\n');

    await loadProducts();
  } catch (e) {
    setError((e as Error).message || String(e));
  } finally {
    saving.value = false;
  }
}

async function updateProduct() {
  clearMessages();
  if (!editingProductId.value) return;

  if (!form.name.trim()) {
    setError('产品名称不能为空');
    return;
  }

  saving.value = true;
  try {
    const payload = {
      name: form.name.trim(),
      dimensions: form.dimensions.trim() || null,
      features: toLines(form.featuresText),
      characteristics: toLines(form.characteristicsText),
    };

    const res = await apiFetch(`/api/v1/products/${editingProductId.value}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    if (!res.ok) throw new Error(await readApiError(res));

    const updated = (await res.json()) as ProductDetail;
    recognitionConfidence.value = updated.recognition_confidence;
    existingImages.value = updated.images || existingImages.value;
    setSuccess('已保存修改');
    await loadProducts();
  } catch (e) {
    setError((e as Error).message || String(e));
  } finally {
    saving.value = false;
  }
}

async function editProduct(productId: string) {
  clearMessages();
  saving.value = true;
  try {
    const detail = await loadProductDetail(productId);
    editingProductId.value = detail.id;
    recognitionConfidence.value = detail.recognition_confidence ?? null;

    releaseSelectedImages();
    selectedImages.value = [];
    primaryIndex.value = 0;
    existingImages.value = detail.images || [];
    previewRecognitionData.value = null;

    form.name = detail.name || '';
    form.dimensions = detail.dimensions || '';
    form.featuresText = (detail.features || []).join('\n');
    form.characteristicsText = (detail.characteristics || []).join('\n');

    setSuccess('已加载产品信息，可编辑后保存');
  } catch (e) {
    setError((e as Error).message || String(e));
  } finally {
    saving.value = false;
  }
}

async function deleteProduct(productId: string) {
  clearMessages();
  if (!confirm('确定要删除该产品吗？删除后将释放存储空间。')) return;

  saving.value = true;
  try {
    const res = await apiFetch(`/api/v1/products/${productId}`, { method: 'DELETE' });
    if (!res.ok && res.status !== 204) throw new Error(await readApiError(res));

    if (editingProductId.value === productId) resetForm();
    setSuccess('已删除产品');

    if (offset.value > 0 && products.value.length === 1) {
      offset.value = Math.max(0, offset.value - limit.value);
    }
    await loadProducts();
  } catch (e) {
    setError((e as Error).message || String(e));
  } finally {
    saving.value = false;
  }
}

function prevPage() {
  offset.value = Math.max(0, offset.value - limit.value);
  void loadProducts();
}

function nextPage() {
  if (offset.value + limit.value >= total.value) return;
  offset.value = offset.value + limit.value;
  void loadProducts();
}

function debouncedSearch() {
  if (searchTimer) window.clearTimeout(searchTimer);
  searchTimer = window.setTimeout(() => {
    offset.value = 0;
    void loadProducts();
  }, 250);
}

onMounted(async () => {
  try {
    const me = await getCurrentUser();
    isAdmin.value = Boolean(me?.is_admin);
  } catch {
    isAdmin.value = false;
  }
  await loadProducts();
});
</script>

<style scoped>
.products-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  margin: 8px 0 20px;
  flex-wrap: wrap;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 14px;
}

.header-actions {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  justify-content: flex-end;
}

.meta-text {
  color: var(--text-secondary);
  font-size: 12px;
  margin-top: 4px;
}

.error-banner {
  border: 1px solid rgba(255, 59, 48, 0.25);
  background: rgba(255, 59, 48, 0.06);
  color: #b42318;
}

.success-banner {
  border: 1px solid rgba(52, 199, 89, 0.28);
  background: rgba(52, 199, 89, 0.08);
  color: #0f7a2a;
}

.card-title-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  flex-wrap: wrap;
}

.card-actions {
  display: flex;
  gap: 10px;
  align-items: center;
}

.form-actions {
  margin-top: 14px;
  display: flex;
  justify-content: flex-end;
}

.image-grid {
  align-items: start;
}

.dropzone {
  position: relative;
}

.dropzone input[type='file'] {
  position: absolute;
  inset: 0;
  opacity: 0;
  pointer-events: none;
}

.dropzone.is-disabled {
  opacity: 0.6;
  pointer-events: none;
}

.preview-box {
  border: 1px solid rgba(209, 209, 214, 0.65);
  border-radius: var(--radius-md);
  overflow: hidden;
  background: rgba(0, 0, 0, 0.03);
  height: 220px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.preview-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.preview-placeholder {
  font-size: 13px;
  color: var(--text-secondary);
}

.product-image-grid {
  margin-top: 12px;
}

.preview-item {
  position: relative;
}

.preview-item.is-primary {
  border-color: rgba(0, 113, 227, 0.55);
  box-shadow: 0 6px 18px rgba(0, 113, 227, 0.18);
}

.preview-badge {
  position: absolute;
  left: 8px;
  top: 8px;
  background: rgba(255, 255, 255, 0.9);
  color: var(--accent-color);
  border: 1px solid rgba(0, 113, 227, 0.25);
  border-radius: 999px;
  padding: 2px 8px;
  font-size: 11px;
  font-weight: 600;
}

.preview-action-btn {
  border: 1px solid rgba(209, 209, 214, 0.8);
  background: rgba(255, 255, 255, 0.92);
  color: var(--text-primary);
  border-radius: 999px;
  padding: 4px 8px;
  font-size: 11px;
  cursor: pointer;
  transition: all 0.15s ease;
}

.preview-action-btn:hover {
  border-color: rgba(0, 113, 227, 0.45);
  color: var(--accent-color);
}

.preview-action-btn.danger {
  border-color: rgba(255, 59, 48, 0.35);
  color: #b42318;
}

.preview-action-btn.danger:hover {
  border-color: rgba(255, 59, 48, 0.6);
  color: #d92d20;
}

.loading {
  text-align: center;
  padding: 20px 0;
  color: var(--text-secondary);
}

.empty-state {
  text-align: center;
  padding: 30px 0;
  color: var(--text-secondary);
}

.products-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 14px;
  margin-top: 14px;
}

.product-card {
  background: #fff;
  border: 1px solid rgba(209, 209, 214, 0.65);
  border-radius: var(--radius-lg);
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  display: flex;
  flex-direction: column;
}

.product-thumb {
  position: relative;
  height: 160px;
  background: rgba(0, 0, 0, 0.03);
}

.product-thumb img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.product-body {
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.product-title {
  font-weight: 700;
  font-size: 14px;
  line-height: 1.2;
}

.product-meta {
  font-size: 12px;
  color: var(--text-secondary);
}

.image-count-badge {
  position: absolute;
  right: 8px;
  top: 8px;
  background: rgba(0, 0, 0, 0.55);
  color: #fff;
  border-radius: 999px;
  padding: 2px 8px;
  font-size: 11px;
  font-weight: 600;
  backdrop-filter: blur(4px);
}

.product-actions {
  display: flex;
  gap: 8px;
  margin-top: 4px;
  flex-wrap: wrap;
}

.pagination {
  margin-top: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
}
</style>
