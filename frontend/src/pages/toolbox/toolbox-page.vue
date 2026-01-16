<template>
  <div class="toolbox-page">
    <header class="header">
      <div class="logo">
        <div class="logo-icon">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2">
            <rect x="3" y="8" width="18" height="13" rx="2" />
            <path d="M9 8V6a3 3 0 0 1 6 0v2" />
            <path d="M3 12h18" />
          </svg>
        </div>
        <span>工具箱</span>
      </div>
      <div class="header-actions">
        <a href="/" class="btn btn-secondary" style="text-decoration: none; display: flex; align-items: center; gap: 8px;">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M19 12H5M12 19l-7-7 7-7" />
          </svg>
          返回主页面
        </a>
      </div>
    </header>

    <div class="main-container">
      <aside class="sidebar">
        <section class="sidebar-section">
          <div class="section-title">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polygon points="12 2 2 7 12 12 22 7 12 2" />
              <polyline points="2 17 12 22 22 17" />
              <polyline points="2 12 12 17 22 12" />
            </svg>
            模型设置
          </div>
          <select class="form-select" v-model="modelConfig.model">
            <option value="gemini-3-pro-image-preview">gemini-3-pro-image-preview (推荐)</option>
            <option value="gemini-2.5-flash-image">gemini-2.5-flash-image (快速)</option>
          </select>
          <div class="form-group" style="margin-top: 16px;">
            <label class="form-label">Aspect Ratio</label>
            <select class="form-select" v-model="modelConfig.aspectRatio">
              <option value="">Auto</option>
              <option value="1:1">1:1 (Square)</option>
              <option value="16:9">16:9 (Landscape)</option>
              <option value="9:16">9:16 (Portrait)</option>
              <option value="4:3">4:3</option>
              <option value="3:4">3:4</option>
              <option value="3:2">3:2</option>
              <option value="2:3">2:3</option>
              <option value="4:5">4:5</option>
              <option value="5:4">5:4</option>
            </select>
          </div>
          <div class="form-group">
            <label class="form-label">Image Size</label>
            <select class="form-select" v-model="modelConfig.imageSize">
              <option value="">Default</option>
              <option value="1K">1K</option>
              <option value="2K">2K</option>
              <option value="4K">4K</option>
            </select>
          </div>
          <div class="form-group">
            <label class="form-label">并发数量</label>
            <input class="form-input" type="number" min="1" max="10" v-model.number="modelConfig.n">
            <div class="form-hint">一次生成多张四宫格图片（1-10）</div>
          </div>
        </section>

        <section class="sidebar-section">
          <div class="section-title">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M20 7H4a2 2 0 0 0-2 2v10a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V9a2 2 0 0 0-2-2Z" />
              <path d="M9 2v5" />
              <path d="M15 2v5" />
              <path d="M2 9h20" />
            </svg>
            选择产品
          </div>
          <div class="search-wrapper">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="11" cy="11" r="8" />
              <line x1="21" y1="21" x2="16.65" y2="16.65" />
            </svg>
            <input type="text" class="form-input" v-model="productSearch" placeholder="搜索产品..." @input="searchProducts">
          </div>

          <div class="product-list" v-if="!loadingProducts && products.length > 0">
            <div
              v-for="product in products"
              :key="product.id"
              class="product-item"
              :class="{ selected: selectedProduct?.id === product.id }"
              @click="selectProduct(product)"
            >
              <img :src="getProductThumbnail(product)" :alt="product.name" class="product-thumb">
              <div class="product-info">
                <div class="product-name">{{ product.name || '未命名产品' }}</div>
                <div class="product-meta">{{ product.dimensions || '' }}</div>
              </div>
            </div>
          </div>
          <div class="product-list-empty" v-else-if="!loadingProducts && products.length === 0">
            <p>暂无产品</p>
            <a href="/products" class="btn btn-secondary btn-sm">前往产品库</a>
          </div>
          <div class="product-list-loading" v-else>
            <div class="spinner-small"></div>
            <span>加载中...</span>
          </div>

          <div class="pagination" v-if="totalProducts > pageSize">
            <button class="btn btn-ghost btn-sm" :disabled="currentPage <= 1" @click="prevPage">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="15 18 9 12 15 6" />
              </svg>
            </button>
            <span class="page-info">{{ currentPage }} / {{ totalPages }}</span>
            <button class="btn btn-ghost btn-sm" :disabled="currentPage >= totalPages" @click="nextPage">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="9 18 15 12 9 6" />
              </svg>
            </button>
          </div>
        </section>

        <section class="sidebar-section" v-if="selectedProduct">
          <div class="section-title">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <rect x="3" y="3" width="18" height="18" rx="2" ry="2" />
              <circle cx="8.5" cy="8.5" r="1.5" />
              <polyline points="21 15 16 10 5 21" />
            </svg>
            参考图片 ({{ selectedImages.length }}/{{ productImages.length }})
          </div>
          <div class="image-grid" v-if="productImages.length > 0">
            <div
              v-for="img in productImages"
              :key="img.id"
              class="image-item"
              :class="{ selected: selectedImages.includes(img.id) }"
              @click="toggleImageSelection(img.id)"
            >
              <img :src="img.image_url" alt="Product image">
              <div class="image-check" v-if="selectedImages.includes(img.id)">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="3">
                  <polyline points="20 6 9 17 4 12" />
                </svg>
              </div>
              <div class="image-primary" v-if="img.is_primary">主图</div>
            </div>
          </div>
          <div class="no-images" v-else>
            <p>该产品暂无图片</p>
          </div>
        </section>
      </aside>

      <main class="main-content">
        <section class="content-panel">
          <div class="panel-header">
            <div class="panel-title">
              <span class="step-indicator">多</span>
              <div>
                <h3>多视图生成</h3>
                <p class="panel-subtitle">生成白底四宫格多角度商品图</p>
              </div>
            </div>
            <span class="panel-hint" v-if="!selectedProduct">请先从左侧选择产品</span>
          </div>

          <div class="preview-panel">
            <div class="preview-card">
              <div class="preview-card-header">
                <h4>提示词预览</h4>
                <button class="btn btn-ghost btn-sm" @click="copyPrompt" :disabled="!promptPreview">
                  复制
                </button>
              </div>
              <div class="preview-card-body">
                <p v-if="promptPreview">{{ promptPreview }}</p>
                <p v-else class="preview-placeholder">选择产品后自动生成提示词</p>
              </div>
            </div>
          </div>

          <div class="result-area" style="margin-top: 20px;">
            <div class="result-placeholder" v-if="!generating && generatedImages.length === 0">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                <rect x="3" y="3" width="18" height="18" rx="2" />
                <circle cx="8.5" cy="8.5" r="1.5" />
                <polyline points="21 15 16 10 5 21" />
              </svg>
              <h3>准备生成</h3>
              <p>选择产品与参考图后点击生成。</p>
            </div>
            <div class="loading-state" v-if="generating">
              <div class="spinner"></div>
              <p>正在生成多视图...</p>
            </div>
            <div class="result-container" v-if="generatedImages.length && !generating">
              <img :src="generatedImage" alt="Generated grid" class="result-image" @click="openLightbox(generatedImage)">
              <div class="result-actions">
                <button class="btn btn-secondary" type="button" @click="downloadImage(generatedImage)">
                  下载
                </button>
                <button class="btn btn-primary" type="button" @click="generateImages">
                  重新生成
                </button>
              </div>
              <div class="result-grid" v-if="generatedImages.length > 1">
                <button
                  v-for="(img, idx) in generatedImages"
                  :key="`${img}-${idx}`"
                  class="result-thumb"
                  :class="{ active: img === generatedImage }"
                  type="button"
                  @click="generatedImage = img"
                >
                  <img :src="img" :alt="`Generated ${idx + 1}`" loading="lazy" decoding="async">
                  <span class="result-thumb-index">{{ idx + 1 }}</span>
                </button>
              </div>
            </div>
          </div>

          <div class="generate-section">
            <button
              class="generate-btn"
              :disabled="!canGenerate || generating"
              data-test="generate-button"
              @click="generateImages"
            >
              <div v-if="generating" class="spinner-small"></div>
              <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2" />
              </svg>
              {{ generating ? '生成中...' : '生成多视图' }}
            </button>
            <div class="generate-hint" v-if="generationHint">{{ generationHint }}</div>
          </div>
        </section>
      </main>
    </div>

    <div class="lightbox-overlay" v-if="lightboxOpen" @click="closeLightbox">
      <div class="lightbox-content" @click.stop>
        <div class="lightbox-header">
          <div class="lightbox-title">放大预览</div>
          <button class="btn btn-ghost btn-icon" type="button" @click="closeLightbox" aria-label="Close preview">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="18" y1="6" x2="6" y2="18" />
              <line x1="6" y1="6" x2="18" y2="18" />
            </svg>
          </button>
        </div>
        <div class="lightbox-body">
          <img :src="lightboxImage" alt="Full size preview">
        </div>
        <div class="lightbox-footer">
          <div class="lightbox-nav" v-if="generatedImages.length > 1">
            <button class="btn btn-secondary btn-sm" type="button" @click="prevLightbox">上一张</button>
            <span class="lightbox-index">{{ lightboxIndex + 1 }} / {{ generatedImages.length }}</span>
            <button class="btn btn-secondary btn-sm" type="button" @click="nextLightbox">下一张</button>
          </div>
          <div class="lightbox-actions">
            <button class="btn btn-secondary btn-sm" type="button" @click="downloadImage(lightboxImage)">下载</button>
            <button class="btn btn-ghost btn-sm" type="button" @click="closeLightbox">关闭</button>
          </div>
        </div>
      </div>
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
            <circle cx="12" cy="12" r="10" />
            <line x1="12" y1="8" x2="12" y2="12" />
            <line x1="12" y1="16" x2="12.01" y2="16" />
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
import { ref, reactive, computed, onMounted, onUnmounted, watch } from "vue";
import { apiFetch, getUserId, supabase } from "@/shared/supabase";
import { buildMultiviewPrompt } from "./multiview-prompt";

interface Product {
  id: string;
  name: string;
  dimensions: string;
  original_image_url: string;
  images?: ProductImage[];
  image_count?: number;
}

interface ProductImage {
  id: string;
  image_url: string;
  is_primary: boolean;
}

interface Toast {
  id: number;
  message: string;
  type: "success" | "error" | "info";
}

const apiConfig = reactive({
  apiKey: "",
  baseUrl: "",
});

const modelConfig = reactive({
  model: "gemini-3-pro-image-preview",
  aspectRatio: "",
  imageSize: "1K",
  n: 1,
});

const products = ref<Product[]>([]);
const loadingProducts = ref(false);
const productSearch = ref("");
const currentPage = ref(1);
const pageSize = 10;
const totalProducts = ref(0);
const selectedProduct = ref<Product | null>(null);
const productImages = ref<ProductImage[]>([]);
const selectedImages = ref<string[]>([]);

const generating = ref(false);
const generatedImage = ref("");
const generatedImages = ref<string[]>([]);
const errorMessage = ref("");
const toasts = ref<Toast[]>([]);

const lightboxOpen = ref(false);
const lightboxIndex = ref(0);

const totalPages = computed(() => Math.ceil(totalProducts.value / pageSize));

const promptPreview = computed(() => {
  if (!selectedProduct.value) return "";
  return buildMultiviewPrompt(selectedProduct.value.name || "");
});

const canGenerate = computed(() => {
  return Boolean(selectedProduct.value && selectedImages.value.length > 0);
});

const generationHint = computed(() => {
  if (generating.value) return "正在生成多视图...";
  if (!selectedProduct.value) return "请先选择产品";
  if (selectedImages.value.length === 0) return "请选择至少一张参考图片";
  return "";
});

const lightboxImage = computed(() => {
  const imgs = generatedImages.value;
  if (!imgs.length) return "";
  const idx = Math.min(imgs.length - 1, Math.max(0, lightboxIndex.value));
  return imgs[idx] || "";
});

function normalizeApiKey(value: string): string {
  return String(value || "").trim().replace(/^bearer\s+/i, "").trim();
}

function normalizeBaseUrl(value: string): string | null {
  const raw = String(value || "").trim();
  return raw || null;
}

function extractImageUrls(payload: any): string[] {
  if (!payload || typeof payload !== "object") return [];

  const urls: string[] = [];
  if (Array.isArray(payload.data)) {
    for (const item of payload.data) {
      if (!item || typeof item !== "object") continue;
      if (typeof item.url === "string" && item.url) urls.push(item.url);
      else if (typeof item.b64_json === "string" && item.b64_json) {
        urls.push(`data:image/png;base64,${item.b64_json}`);
      } else if (typeof item.image_url === "string" && item.image_url) {
        urls.push(item.image_url);
      } else if (typeof item.imageUrl === "string" && item.imageUrl) {
        urls.push(item.imageUrl);
      }
    }
  }

  if (typeof payload.url === "string" && payload.url) urls.push(payload.url);
  if (typeof payload.b64_json === "string" && payload.b64_json) {
    urls.push(`data:image/png;base64,${payload.b64_json}`);
  }
  if (typeof payload.image_url === "string" && payload.image_url) urls.push(payload.image_url);
  if (typeof payload.imageUrl === "string" && payload.imageUrl) urls.push(payload.imageUrl);

  return Array.from(new Set(urls));
}

function loadApiConfig() {
  apiConfig.apiKey = localStorage.getItem("global_api_key") || localStorage.getItem("video_api_key") || "";
  apiConfig.baseUrl = localStorage.getItem("global_base_url") || localStorage.getItem("video_base_url") || "";
}

async function fetchProducts() {
  loadingProducts.value = true;
  try {
    const start = (currentPage.value - 1) * pageSize;
    const end = start + pageSize - 1;

    let query = supabase
      .from("products")
      .select("id,name,dimensions,original_image_url,created_at", { count: "exact" })
      .order("created_at", { ascending: false })
      .range(start, end);

    if (productSearch.value) {
      query = query.ilike("name", `%${productSearch.value}%`);
    }

    const { data, error, count } = await query;
    if (error) throw error;

    const rows = (data || []) as any[];
    const ids = rows.map((p) => p.id);
    const imagesByProductId = new Map<string, ProductImage[]>();

    if (ids.length) {
      const { data: imgs, error: imgsError } = await supabase
        .from("product_images")
        .select("id,product_id,image_url,is_primary")
        .in("product_id", ids);
      if (imgsError) throw imgsError;

      for (const img of imgs || []) {
        const productId = (img as any).product_id as string;
        const entry: ProductImage = {
          id: (img as any).id as string,
          image_url: (img as any).image_url as string,
          is_primary: Boolean((img as any).is_primary),
        };
        const list = imagesByProductId.get(productId) || [];
        list.push(entry);
        imagesByProductId.set(productId, list);
      }
    }

    products.value = rows.map((p) => {
      const images = imagesByProductId.get(p.id) || [];
      return {
        ...(p as Product),
        images,
        image_count: images.length || 1,
      };
    });
    totalProducts.value = count || 0;
  } catch (e) {
    showToast("加载产品列表失败", "error");
  } finally {
    loadingProducts.value = false;
  }
}

function searchProducts() {
  currentPage.value = 1;
  fetchProducts();
}

function prevPage() {
  if (currentPage.value > 1) {
    currentPage.value--;
    fetchProducts();
  }
}

function nextPage() {
  if (currentPage.value < totalPages.value) {
    currentPage.value++;
    fetchProducts();
  }
}

function getProductThumbnail(product: Product): string {
  if (product.images && product.images.length > 0) {
    const primary = product.images.find((img) => img.is_primary);
    return primary ? primary.image_url : product.images[0].image_url;
  }
  return product.original_image_url || "/static/placeholder.png";
}

async function selectProduct(product: Product) {
  selectedProduct.value = product;

  try {
    const { data: detail, error } = await supabase
      .from("products")
      .select("*")
      .eq("id", product.id)
      .single();
    if (error) throw error;

    const { data: imgs, error: imgsError } = await supabase
      .from("product_images")
      .select("id,image_url,is_primary")
      .eq("product_id", product.id)
      .order("is_primary", { ascending: false });
    if (imgsError) throw imgsError;

    productImages.value = ((imgs as any[]) || []) as ProductImage[];
    const originalUrl = (detail as any).original_image_url as string | null | undefined;
    if (productImages.value.length === 0 && originalUrl) {
      productImages.value = [{
        id: (detail as any).id,
        image_url: originalUrl,
        is_primary: true,
      }];
    }

    const primaryImg = productImages.value.find((img) => img.is_primary);
    if (primaryImg) {
      selectedImages.value = [primaryImg.id];
    } else if (productImages.value.length > 0) {
      selectedImages.value = [productImages.value[0].id];
    } else {
      selectedImages.value = [];
    }
  } catch (e) {
    showToast("加载产品详情失败", "error");
  }
}

function toggleImageSelection(imageId: string) {
  const index = selectedImages.value.indexOf(imageId);
  if (index === -1) {
    selectedImages.value.push(imageId);
  } else {
    selectedImages.value.splice(index, 1);
  }
}

async function copyPrompt() {
  if (!promptPreview.value) return;
  try {
    await navigator.clipboard.writeText(promptPreview.value);
    showToast("提示词已复制", "success");
  } catch (e) {
    showToast("复制失败", "error");
  }
}

async function generateImages() {
  if (!canGenerate.value || generating.value) return;

  generating.value = true;
  errorMessage.value = "";
  closeLightbox();

  try {
    const batchCount = Math.min(10, Math.max(1, Math.floor(Number(modelConfig.n) || 1)));
    modelConfig.n = batchCount;
    if (batchCount >= 6) {
      const ok = confirm(`将并发生成 ${batchCount} 张四宫格图片，确认继续？`);
      if (!ok) {
        generating.value = false;
        return;
      }
    }

    const formData = new FormData();
    formData.append("prompt", promptPreview.value);
    formData.append("model", modelConfig.model);
    formData.append("n", String(batchCount));
    formData.append("response_format", "url");

    if (modelConfig.aspectRatio) {
      formData.append("aspect_ratio", modelConfig.aspectRatio);
    }
    if (modelConfig.imageSize) {
      formData.append("image_size", modelConfig.imageSize);
    }

    for (const imageId of selectedImages.value) {
      const img = productImages.value.find((i) => i.id === imageId);
      if (img) {
        try {
          const imgRes = await fetch(img.image_url);
          const imgBlob = await imgRes.blob();
          formData.append("image", imgBlob, `ref-${imageId}.jpg`);
        } catch (e) {
          console.warn("Failed to fetch reference image:", img.image_url);
        }
      }
    }

    const headers: Record<string, string> = {};
    const apiKey = normalizeApiKey(apiConfig.apiKey);
    if (apiKey) headers["X-API-Key"] = apiKey;
    const baseUrl = normalizeBaseUrl(apiConfig.baseUrl);
    if (baseUrl) headers["X-Base-Url"] = baseUrl;

    const res = await apiFetch("/api/v1/images/edits", {
      method: "POST",
      headers,
      body: formData,
    });

    if (!res.ok) {
      const errData = await res.json().catch(() => ({}));
      throw new Error(errData.detail || `HTTP ${res.status}`);
    }

    const data = await res.json();
    const payload = data && typeof data === "object" && data.response ? data.response : data;
    const urls = extractImageUrls(payload).length ? extractImageUrls(payload) : extractImageUrls(data);

    if (urls.length) {
      generatedImages.value = urls;
      generatedImage.value = urls[0] || "";
    } else {
      throw new Error("Invalid response format");
    }

    showToast(urls.length > 1 ? `多视图生成成功（${urls.length}张）` : "多视图生成成功", "success");

    const userId = await getUserId();
    if (userId) {
      const rows = urls.map((url, idx) => ({
        user_id: userId,
        title: selectedProduct.value?.name ? `多视图 - ${selectedProduct.value.name}` : null,
        model: modelConfig.model,
        prompt: promptPreview.value,
        status: "completed",
        image_url: url,
        metadata: {
          source: "toolbox-multiview",
          product_id: selectedProduct.value?.id || null,
          selected_images: selectedImages.value,
          aspect_ratio: modelConfig.aspectRatio || null,
          image_size: modelConfig.imageSize || null,
          index: idx,
        },
        request: data && typeof data === "object" && (data as any).request ? (data as any).request : null,
        response: data && typeof data === "object" && (data as any).response ? (data as any).response : data,
      }));

      const { error: insertError } = await supabase.from("user_images").insert(rows);
      if (insertError) console.warn("Failed to save images to repository:", insertError);
    }
  } catch (e: any) {
    errorMessage.value = e.message || "生成失败，请重试";
  } finally {
    generating.value = false;
  }
}

function downloadImage(url?: string) {
  const imageUrl = url || generatedImage.value;
  if (!imageUrl) return;

  const link = document.createElement("a");
  link.href = imageUrl;
  link.download = `multiview-${Date.now()}.png`;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}

function openLightbox(url: string) {
  const imgs = generatedImages.value;
  if (!imgs.length) return;
  const idx = url ? imgs.indexOf(url) : -1;
  lightboxIndex.value = idx >= 0 ? idx : 0;
  lightboxOpen.value = true;
}

function closeLightbox() {
  lightboxOpen.value = false;
}

function prevLightbox() {
  const total = generatedImages.value.length;
  if (total <= 1) return;
  lightboxIndex.value = (lightboxIndex.value - 1 + total) % total;
}

function nextLightbox() {
  const total = generatedImages.value.length;
  if (total <= 1) return;
  lightboxIndex.value = (lightboxIndex.value + 1) % total;
}

function handleLightboxKeydown(e: KeyboardEvent) {
  if (!lightboxOpen.value) return;

  if (e.key === "Escape") {
    e.preventDefault();
    closeLightbox();
    return;
  }
  if (e.key === "ArrowLeft") {
    e.preventDefault();
    prevLightbox();
    return;
  }
  if (e.key === "ArrowRight") {
    e.preventDefault();
    nextLightbox();
  }
}

let toastId = 0;
function showToast(message: string, type: Toast["type"] = "info") {
  const id = toastId++;
  toasts.value.push({ id, message, type });

  setTimeout(() => {
    const index = toasts.value.findIndex((t) => t.id === id);
    if (index !== -1) {
      toasts.value.splice(index, 1);
    }
  }, 3000);
}

onMounted(() => {
  loadApiConfig();
  fetchProducts();
  document.addEventListener("keydown", handleLightboxKeydown);
});

onUnmounted(() => {
  document.removeEventListener("keydown", handleLightboxKeydown);
});

watch(lightboxOpen, (open) => {
  document.body.style.overflow = open ? "hidden" : "";
});

watch(generatedImages, (imgs) => {
  if (!imgs.length) {
    closeLightbox();
    return;
  }
  if (lightboxIndex.value >= imgs.length) {
    lightboxIndex.value = 0;
  }
});
</script>
