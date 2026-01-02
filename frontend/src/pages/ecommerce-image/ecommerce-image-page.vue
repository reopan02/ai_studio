<template>
  <div class="ecommerce-image-page">
    <!-- Header -->
    <header class="header">
      <div class="logo">
        <div class="logo-icon">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2">
            <rect x="3" y="3" width="18" height="18" rx="2"/>
            <circle cx="8.5" cy="8.5" r="1.5"/>
            <polyline points="21 15 16 10 5 21"/>
          </svg>
        </div>
        <span>电商图生成</span>
      </div>
      <div class="header-actions">
        <a href="/" class="btn btn-secondary" style="text-decoration: none; display: flex; align-items: center; gap: 8px;">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M19 12H5M12 19l-7-7 7-7"/>
          </svg>
          返回主页面
        </a>
        <button class="btn btn-ghost btn-icon" @click="showSettings = !showSettings" title="Settings">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="3"/>
            <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/>
          </svg>
        </button>
      </div>
    </header>

    <div class="main-container">
      <!-- Sidebar -->
      <aside class="sidebar">
        <!-- API Config Section (collapsible) -->
        <section class="sidebar-section" v-if="showSettings">
          <div class="section-title">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M12 15a3 3 0 1 0 0-6 3 3 0 0 0 0 6Z"/>
              <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4"/>
            </svg>
            API Configuration
          </div>
          <div class="form-group">
            <label class="form-label">API Key</label>
            <div class="input-wrapper">
              <input :type="showApiKey ? 'text' : 'password'" class="form-input" v-model="apiConfig.apiKey" placeholder="Enter your API key">
              <button class="toggle-visibility" @click="showApiKey = !showApiKey">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
                  <circle cx="12" cy="12" r="3"/>
                </svg>
              </button>
            </div>
          </div>
          <div class="form-group">
            <label class="form-label">Base URL</label>
            <div class="input-wrapper">
              <input :type="showBaseUrl ? 'text' : 'password'" class="form-input" v-model="apiConfig.baseUrl" placeholder="https://api.example.com">
              <button class="toggle-visibility" @click="showBaseUrl = !showBaseUrl">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
                  <circle cx="12" cy="12" r="3"/>
                </svg>
              </button>
            </div>
          </div>
          <div class="btn-group">
            <button class="btn btn-primary btn-sm" @click="saveApiConfig">Save</button>
            <button class="btn btn-secondary btn-sm" @click="resetApiConfig">Reset</button>
          </div>
        </section>

        <!-- Model Selection -->
        <section class="sidebar-section">
          <div class="section-title">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polygon points="12 2 2 7 12 12 22 7 12 2"/>
              <polyline points="2 17 12 22 22 17"/>
              <polyline points="2 12 12 17 22 12"/>
            </svg>
            Model Selection
          </div>
          <select class="form-select" v-model="modelConfig.model">
            <option value="gpt-image-1.5">gpt-image-1.5</option>
            <option value="nano-banana-2-4k">nano-banana-2-4k</option>
            <option value="nano-banana-2-2k">nano-banana-2-2k</option>
            <option value="nano-banana-2">nano-banana-2</option>
            <option value="nano-banana">nano-banana</option>
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
        </section>

        <!-- Product Selector -->
        <section class="sidebar-section">
          <div class="section-title">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M20 7H4a2 2 0 0 0-2 2v10a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V9a2 2 0 0 0-2-2Z"/>
              <path d="M9 2v5"/>
              <path d="M15 2v5"/>
              <path d="M2 9h20"/>
            </svg>
            选择产品
          </div>
          <div class="search-wrapper">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="11" cy="11" r="8"/>
              <line x1="21" y1="21" x2="16.65" y2="16.65"/>
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

          <!-- Pagination -->
          <div class="pagination" v-if="totalProducts > pageSize">
            <button class="btn btn-ghost btn-sm" :disabled="currentPage <= 1" @click="prevPage">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="15 18 9 12 15 6"/>
              </svg>
            </button>
            <span class="page-info">{{ currentPage }} / {{ totalPages }}</span>
            <button class="btn btn-ghost btn-sm" :disabled="currentPage >= totalPages" @click="nextPage">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="9 18 15 12 9 6"/>
              </svg>
            </button>
          </div>
        </section>

        <!-- Reference Images -->
        <section class="sidebar-section" v-if="selectedProduct">
          <div class="section-title">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>
              <circle cx="8.5" cy="8.5" r="1.5"/>
              <polyline points="21 15 16 10 5 21"/>
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
              <img :src="img.image_url" :alt="'Product image'">
              <div class="image-check" v-if="selectedImages.includes(img.id)">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="3">
                  <polyline points="20 6 9 17 4 12"/>
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

      <!-- Main Content -->
      <main class="main-content">
        <!-- Product Info Panel -->
        <div class="content-panel" v-if="selectedProduct">
          <div class="panel-header">
            <h3>产品信息</h3>
            <span class="panel-hint">勾选要包含在 Prompt 中的字段</span>
          </div>
          <div class="product-fields">
            <div class="field-row">
              <label class="field-checkbox">
                <input type="checkbox" v-model="fieldToggles.name">
                <span>产品名称</span>
              </label>
              <input type="text" class="form-input" v-model="editableProduct.name" :disabled="!fieldToggles.name">
            </div>
            <div class="field-row">
              <label class="field-checkbox">
                <input type="checkbox" v-model="fieldToggles.dimensions">
                <span>尺寸规格</span>
              </label>
              <input type="text" class="form-input" v-model="editableProduct.dimensions" :disabled="!fieldToggles.dimensions">
            </div>
            <div class="field-row">
              <label class="field-checkbox">
                <input type="checkbox" v-model="fieldToggles.features">
                <span>功能特征</span>
              </label>
              <textarea class="form-input" v-model="editableProduct.featuresText" :disabled="!fieldToggles.features" rows="2" placeholder="每行一个特征"></textarea>
            </div>
            <div class="field-row">
              <label class="field-checkbox">
                <input type="checkbox" v-model="fieldToggles.characteristics">
                <span>产品特点</span>
              </label>
              <textarea class="form-input" v-model="editableProduct.characteristicsText" :disabled="!fieldToggles.characteristics" rows="2" placeholder="每行一个特点"></textarea>
            </div>
          </div>
        </div>

        <!-- Template Modules -->
        <div class="content-panel">
          <div class="panel-header">
            <h3>Prompt 模板</h3>
            <button class="btn btn-ghost btn-sm" @click="resetTemplates">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="1 4 1 10 7 10"/>
                <path d="M3.51 15a9 9 0 1 0 2.13-9.36L1 10"/>
              </svg>
              重置默认
            </button>
          </div>

          <!-- Scene Selection -->
          <div class="template-module">
            <div class="module-header">
              <span class="module-title">场景选择</span>
              <button class="btn btn-ghost btn-icon-sm" @click="addOption('scene')">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <line x1="12" y1="5" x2="12" y2="19"/>
                  <line x1="5" y1="12" x2="19" y2="12"/>
                </svg>
              </button>
            </div>
            <div class="option-chips">
              <div
                v-for="(option, idx) in templates.scene"
                :key="'scene-' + idx"
                class="option-chip"
                :class="{ selected: selectedTemplates.scene.includes(option) }"
              >
                <span
                  v-if="editingOption.category !== 'scene' || editingOption.index !== idx"
                  @click="toggleOption('scene', option)"
                >{{ option }}</span>
                <input
                  v-else
                  type="text"
                  class="option-edit-input"
                  v-model="templates.scene[idx]"
                  @blur="finishEditing"
                  @keyup.enter="finishEditing"
                  ref="optionInput"
                >
                <button class="chip-edit" @click.stop="startEditing('scene', idx)" v-if="editingOption.category !== 'scene' || editingOption.index !== idx">
                  <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
                    <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
                  </svg>
                </button>
                <button class="chip-delete" @click.stop="removeOption('scene', idx)">
                  <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <line x1="18" y1="6" x2="6" y2="18"/>
                    <line x1="6" y1="6" x2="18" y2="18"/>
                  </svg>
                </button>
              </div>
            </div>
          </div>

          <!-- Shooting Angle -->
          <div class="template-module">
            <div class="module-header">
              <span class="module-title">拍摄角度</span>
              <button class="btn btn-ghost btn-icon-sm" @click="addOption('angle')">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <line x1="12" y1="5" x2="12" y2="19"/>
                  <line x1="5" y1="12" x2="19" y2="12"/>
                </svg>
              </button>
            </div>
            <div class="option-chips">
              <div
                v-for="(option, idx) in templates.angle"
                :key="'angle-' + idx"
                class="option-chip"
                :class="{ selected: selectedTemplates.angle.includes(option) }"
              >
                <span
                  v-if="editingOption.category !== 'angle' || editingOption.index !== idx"
                  @click="toggleOption('angle', option)"
                >{{ option }}</span>
                <input
                  v-else
                  type="text"
                  class="option-edit-input"
                  v-model="templates.angle[idx]"
                  @blur="finishEditing"
                  @keyup.enter="finishEditing"
                >
                <button class="chip-edit" @click.stop="startEditing('angle', idx)" v-if="editingOption.category !== 'angle' || editingOption.index !== idx">
                  <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
                    <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
                  </svg>
                </button>
                <button class="chip-delete" @click.stop="removeOption('angle', idx)">
                  <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <line x1="18" y1="6" x2="6" y2="18"/>
                    <line x1="6" y1="6" x2="18" y2="18"/>
                  </svg>
                </button>
              </div>
            </div>
          </div>

          <!-- Style/Lighting -->
          <div class="template-module">
            <div class="module-header">
              <span class="module-title">风格 / 光影 <span class="optional-tag">(可选)</span></span>
              <button class="btn btn-ghost btn-icon-sm" @click="addOption('style')">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <line x1="12" y1="5" x2="12" y2="19"/>
                  <line x1="5" y1="12" x2="19" y2="12"/>
                </svg>
              </button>
            </div>
            <div class="option-chips">
              <div
                v-for="(option, idx) in templates.style"
                :key="'style-' + idx"
                class="option-chip"
                :class="{ selected: selectedTemplates.style.includes(option) }"
              >
                <span
                  v-if="editingOption.category !== 'style' || editingOption.index !== idx"
                  @click="toggleOption('style', option)"
                >{{ option }}</span>
                <input
                  v-else
                  type="text"
                  class="option-edit-input"
                  v-model="templates.style[idx]"
                  @blur="finishEditing"
                  @keyup.enter="finishEditing"
                >
                <button class="chip-edit" @click.stop="startEditing('style', idx)" v-if="editingOption.category !== 'style' || editingOption.index !== idx">
                  <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
                    <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
                  </svg>
                </button>
                <button class="chip-delete" @click.stop="removeOption('style', idx)">
                  <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <line x1="18" y1="6" x2="6" y2="18"/>
                    <line x1="6" y1="6" x2="18" y2="18"/>
                  </svg>
                </button>
              </div>
            </div>
          </div>

          <!-- Generation Target -->
          <div class="template-module">
            <div class="module-header">
              <span class="module-title">生成目标</span>
              <button class="btn btn-ghost btn-icon-sm" @click="addOption('target')">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <line x1="12" y1="5" x2="12" y2="19"/>
                  <line x1="5" y1="12" x2="19" y2="12"/>
                </svg>
              </button>
            </div>
            <div class="option-chips">
              <div
                v-for="(option, idx) in templates.target"
                :key="'target-' + idx"
                class="option-chip"
                :class="{ selected: selectedTemplates.target.includes(option) }"
              >
                <span
                  v-if="editingOption.category !== 'target' || editingOption.index !== idx"
                  @click="toggleOption('target', option)"
                >{{ option }}</span>
                <input
                  v-else
                  type="text"
                  class="option-edit-input"
                  v-model="templates.target[idx]"
                  @blur="finishEditing"
                  @keyup.enter="finishEditing"
                >
                <button class="chip-edit" @click.stop="startEditing('target', idx)" v-if="editingOption.category !== 'target' || editingOption.index !== idx">
                  <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
                    <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
                  </svg>
                </button>
                <button class="chip-delete" @click.stop="removeOption('target', idx)">
                  <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <line x1="18" y1="6" x2="6" y2="18"/>
                    <line x1="6" y1="6" x2="18" y2="18"/>
                  </svg>
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Prompt Preview -->
        <div class="content-panel prompt-preview-panel">
          <div class="panel-header">
            <h3>Prompt 预览</h3>
            <button class="btn btn-ghost btn-sm" @click="copyPrompt" :disabled="!composedPrompt">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <rect x="9" y="9" width="13" height="13" rx="2" ry="2"/>
                <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/>
              </svg>
              复制
            </button>
          </div>
          <div class="prompt-preview">
            <p v-if="composedPrompt">{{ composedPrompt }}</p>
            <p v-else class="prompt-placeholder">选择产品和模板选项后，Prompt 将在此显示...</p>
          </div>
        </div>

        <!-- Generation Result -->
        <div class="result-area">
          <div class="result-placeholder" v-if="!generating && !generatedImage">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <rect x="3" y="3" width="18" height="18" rx="2"/>
              <circle cx="8.5" cy="8.5" r="1.5"/>
              <polyline points="21 15 16 10 5 21"/>
            </svg>
            <h3>准备生成</h3>
            <p>选择产品、参考图片和模板选项，然后点击生成</p>
          </div>

          <div class="loading-state" v-if="generating">
            <div class="spinner"></div>
            <p>正在生成图片...</p>
          </div>

          <div class="result-container" v-if="generatedImage && !generating">
            <img :src="generatedImage" alt="Generated image" class="result-image">
            <div class="result-actions">
              <button class="btn btn-secondary" @click="downloadImage">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                  <polyline points="7 10 12 15 17 10"/>
                  <line x1="12" y1="15" x2="12" y2="3"/>
                </svg>
                下载
              </button>
              <button class="btn btn-primary" @click="generateImage">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <polyline points="1 4 1 10 7 10"/>
                  <path d="M3.51 15a9 9 0 1 0 2.13-9.36L1 10"/>
                </svg>
                重新生成
              </button>
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
            {{ generating ? '生成中...' : '生成电商图' }}
          </button>
          <div class="generate-hint" v-if="!canGenerate">
            {{ generateHint }}
          </div>
        </div>
      </main>
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
import { ref, reactive, computed, onMounted, watch, nextTick } from 'vue';

// Types
interface Product {
  id: string;
  name: string;
  dimensions: string;
  features: string[];
  characteristics: string[];
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
  type: 'success' | 'error' | 'info';
}

// Default template options
const DEFAULT_TEMPLATES = {
  scene: ['白色背景', '自然光桌面', '户外场景', '纯色背景', '生活场景'],
  angle: ['正面', '45度侧面', '俯视', '平视', '特写'],
  style: ['柔和光影', '高对比度', '自然光', '专业棚拍', '暖色调'],
  target: ['主图', '详情页', '海报', '白底图', '场景图']
};

// State
const showSettings = ref(false);
const showApiKey = ref(false);
const showBaseUrl = ref(false);

const apiConfig = reactive({
  apiKey: '',
  baseUrl: ''
});

const modelConfig = reactive({
  model: 'gpt-image-1.5',
  aspectRatio: '',
  imageSize: ''
});

// Products
const products = ref<Product[]>([]);
const loadingProducts = ref(false);
const productSearch = ref('');
const currentPage = ref(1);
const pageSize = 10;
const totalProducts = ref(0);
const selectedProduct = ref<Product | null>(null);
const productImages = ref<ProductImage[]>([]);
const selectedImages = ref<string[]>([]);

// Editable product fields
const editableProduct = reactive({
  name: '',
  dimensions: '',
  featuresText: '',
  characteristicsText: ''
});

const fieldToggles = reactive({
  name: true,
  dimensions: true,
  features: true,
  characteristics: true
});

// Templates
const templates = reactive({
  scene: [...DEFAULT_TEMPLATES.scene],
  angle: [...DEFAULT_TEMPLATES.angle],
  style: [...DEFAULT_TEMPLATES.style],
  target: [...DEFAULT_TEMPLATES.target]
});

const selectedTemplates = reactive({
  scene: [] as string[],
  angle: [] as string[],
  style: [] as string[],
  target: [] as string[]
});

const editingOption = reactive({
  category: '' as string,
  index: -1
});

// Generation
const generating = ref(false);
const generatedImage = ref('');
const errorMessage = ref('');
const toasts = ref<Toast[]>([]);

// Computed
const totalPages = computed(() => Math.ceil(totalProducts.value / pageSize));

const composedPrompt = computed(() => {
  const parts: string[] = [];

  // Product info
  if (selectedProduct.value) {
    if (fieldToggles.name && editableProduct.name) {
      parts.push(editableProduct.name);
    }
    if (fieldToggles.dimensions && editableProduct.dimensions) {
      parts.push(editableProduct.dimensions);
    }
    if (fieldToggles.features && editableProduct.featuresText) {
      const features = editableProduct.featuresText.split('\n').filter(f => f.trim());
      if (features.length > 0) {
        parts.push(features.join('、'));
      }
    }
    if (fieldToggles.characteristics && editableProduct.characteristicsText) {
      const chars = editableProduct.characteristicsText.split('\n').filter(c => c.trim());
      if (chars.length > 0) {
        parts.push(chars.join('、'));
      }
    }
  }

  // Template selections
  if (selectedTemplates.scene.length > 0) {
    parts.push(selectedTemplates.scene.join('、'));
  }
  if (selectedTemplates.angle.length > 0) {
    parts.push(selectedTemplates.angle.join('、'));
  }
  if (selectedTemplates.style.length > 0) {
    parts.push(selectedTemplates.style.join('、'));
  }
  if (selectedTemplates.target.length > 0) {
    const targetDesc = selectedTemplates.target.map(t => {
      if (t === '主图') return '电商主图风格';
      if (t === '详情页') return '详情页展示风格';
      if (t === '海报') return '促销海报风格';
      if (t === '白底图') return '纯白背景产品图';
      if (t === '场景图') return '场景化展示';
      return t;
    });
    parts.push(targetDesc.join('、'));
  }

  return parts.join('，');
});

const canGenerate = computed(() => {
  return selectedProduct.value &&
         selectedImages.value.length > 0 &&
         composedPrompt.value.length > 0;
});

const generateHint = computed(() => {
  if (!selectedProduct.value) return '请先选择一个产品';
  if (selectedImages.value.length === 0) return '请选择至少一张参考图片';
  if (!composedPrompt.value) return '请选择模板选项或填写产品信息';
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

function extractImageUrl(payload: any): string | null {
  if (!payload || typeof payload !== 'object') return null;
  if (Array.isArray(payload.data) && payload.data[0]) {
    const item = payload.data[0];
    if (item?.url) return item.url;
    if (item?.b64_json) return `data:image/png;base64,${item.b64_json}`;
  }
  if (payload.url) return payload.url;
  if (payload.b64_json) return `data:image/png;base64,${payload.b64_json}`;
  if (payload.image_url) return payload.image_url;
  return null;
}

async function fetchProducts() {
  loadingProducts.value = true;
  try {
    const params = new URLSearchParams({
      offset: String((currentPage.value - 1) * pageSize),
      limit: String(pageSize)
    });
    if (productSearch.value) {
      params.set('name', productSearch.value);
    }

    const res = await fetch(`/api/v1/products?${params}`, {
      credentials: 'include'
    });

    if (!res.ok) {
      throw new Error('Failed to fetch products');
    }

    const data = await res.json();
    products.value = data.products || [];
    totalProducts.value = data.total || 0;
  } catch (e) {
    showToast('加载产品列表失败', 'error');
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
    const primary = product.images.find(img => img.is_primary);
    return primary ? primary.image_url : product.images[0].image_url;
  }
  return product.original_image_url || '/static/placeholder.png';
}

async function selectProduct(product: Product) {
  selectedProduct.value = product;

  // Load full product details
  try {
    const res = await fetch(`/api/v1/products/${product.id}`, {
      credentials: 'include'
    });

    if (!res.ok) {
      throw new Error('Failed to load product details');
    }

    const detail = await res.json();

    // Update editable fields
    editableProduct.name = detail.name || '';
    editableProduct.dimensions = detail.dimensions || '';
    editableProduct.featuresText = (detail.features || []).join('\n');
    editableProduct.characteristicsText = (detail.characteristics || []).join('\n');

    // Load images
    productImages.value = detail.images || [];
    if (productImages.value.length === 0 && detail.original_image_url) {
      productImages.value = [{
        id: detail.id,
        image_url: detail.original_image_url,
        is_primary: true
      }];
    }

    // Select primary image by default
    const primaryImg = productImages.value.find(img => img.is_primary);
    if (primaryImg) {
      selectedImages.value = [primaryImg.id];
    } else if (productImages.value.length > 0) {
      selectedImages.value = [productImages.value[0].id];
    } else {
      selectedImages.value = [];
    }
  } catch (e) {
    showToast('加载产品详情失败', 'error');
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

function toggleOption(category: keyof typeof selectedTemplates, option: string) {
  const list = selectedTemplates[category];
  const index = list.indexOf(option);
  if (index === -1) {
    list.push(option);
  } else {
    list.splice(index, 1);
  }
  saveTemplates();
}

function addOption(category: keyof typeof templates) {
  const newOption = '新选项';
  templates[category].push(newOption);
  saveTemplates();

  // Start editing immediately
  nextTick(() => {
    startEditing(category, templates[category].length - 1);
  });
}

function removeOption(category: keyof typeof templates, index: number) {
  const option = templates[category][index];
  templates[category].splice(index, 1);

  // Remove from selected if present
  const selectedIndex = selectedTemplates[category].indexOf(option);
  if (selectedIndex !== -1) {
    selectedTemplates[category].splice(selectedIndex, 1);
  }

  saveTemplates();
}

function startEditing(category: string, index: number) {
  editingOption.category = category;
  editingOption.index = index;
}

function finishEditing() {
  editingOption.category = '';
  editingOption.index = -1;
  saveTemplates();
}

function resetTemplates() {
  templates.scene = [...DEFAULT_TEMPLATES.scene];
  templates.angle = [...DEFAULT_TEMPLATES.angle];
  templates.style = [...DEFAULT_TEMPLATES.style];
  templates.target = [...DEFAULT_TEMPLATES.target];

  selectedTemplates.scene = [];
  selectedTemplates.angle = [];
  selectedTemplates.style = [];
  selectedTemplates.target = [];

  localStorage.removeItem('ecommerce-image-templates');
  showToast('模板已重置为默认值', 'success');
}

function saveTemplates() {
  localStorage.setItem('ecommerce-image-templates', JSON.stringify(templates));
}

function loadTemplates() {
  const saved = localStorage.getItem('ecommerce-image-templates');
  if (saved) {
    try {
      const parsed = JSON.parse(saved);
      if (parsed.scene) templates.scene = parsed.scene;
      if (parsed.angle) templates.angle = parsed.angle;
      if (parsed.style) templates.style = parsed.style;
      if (parsed.target) templates.target = parsed.target;
    } catch (e) {
      // Ignore parse errors
    }
  }
}

function saveApiConfig() {
  localStorage.setItem('ecommerce-image-api-config', JSON.stringify(apiConfig));
  showToast('API 配置已保存', 'success');
}

function resetApiConfig() {
  apiConfig.apiKey = '';
  apiConfig.baseUrl = '';
  localStorage.removeItem('ecommerce-image-api-config');
  showToast('API 配置已重置', 'success');
}

function loadApiConfig() {
  const saved = localStorage.getItem('ecommerce-image-api-config');
  if (saved) {
    try {
      const parsed = JSON.parse(saved);
      if (parsed.apiKey) apiConfig.apiKey = parsed.apiKey;
      if (parsed.baseUrl) apiConfig.baseUrl = parsed.baseUrl;
    } catch (e) {
      // Ignore parse errors
    }
  }
}

async function copyPrompt() {
  if (!composedPrompt.value) return;

  try {
    await navigator.clipboard.writeText(composedPrompt.value);
    showToast('Prompt 已复制到剪贴板', 'success');
  } catch (e) {
    showToast('复制失败', 'error');
  }
}

async function generateImage() {
  if (!canGenerate.value || generating.value) return;

  generating.value = true;
  errorMessage.value = '';

  try {
    // Prepare form data
    const formData = new FormData();
    formData.append('prompt', composedPrompt.value);
    formData.append('model', modelConfig.model);
    formData.append('response_format', 'url');

    if (modelConfig.aspectRatio) {
      formData.append('aspect_ratio', modelConfig.aspectRatio);
    }
    if (modelConfig.imageSize) {
      formData.append('image_size', modelConfig.imageSize);
    }

    // Add selected images
    for (const imageId of selectedImages.value) {
      const img = productImages.value.find(i => i.id === imageId);
      if (img) {
        // Fetch the image and add it to form data
        try {
          const imgRes = await fetch(img.image_url);
          const imgBlob = await imgRes.blob();
          formData.append('image', imgBlob, `ref-${imageId}.jpg`);
        } catch (e) {
          console.warn('Failed to fetch reference image:', img.image_url);
        }
      }
    }

    const headers: Record<string, string> = {
      'X-CSRF-Token': getCsrfToken()
    };
    const apiKey = normalizeApiKey(apiConfig.apiKey);
    if (apiKey) headers['X-API-Key'] = apiKey;
    const baseUrl = normalizeBaseUrl(apiConfig.baseUrl);
    if (baseUrl) headers['X-Base-Url'] = baseUrl;

    const res = await fetch('/api/v1/images/edits', {
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
    const imageUrl = extractImageUrl(payload) || extractImageUrl(data);

    if (imageUrl) {
      generatedImage.value = imageUrl;
    } else {
      throw new Error('Invalid response format');
    }

    showToast('图片生成成功', 'success');
  } catch (e: any) {
    errorMessage.value = e.message || '生成失败，请重试';
  } finally {
    generating.value = false;
  }
}

function downloadImage() {
  if (!generatedImage.value) return;

  const link = document.createElement('a');
  link.href = generatedImage.value;
  link.download = `ecommerce-${Date.now()}.png`;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
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
  loadTemplates();
  loadApiConfig();
  fetchProducts();
});
</script>
