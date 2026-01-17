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
      </div>
    </header>

    <nav class="wizard-nav">
      <div class="wizard-steps">
        <button
          v-for="step in steps"
          :key="step.id"
          class="wizard-step"
          :class="{
            active: currentStep === step.id,
            completed: isStepComplete(step.id),
            disabled: !canNavigateTo(step.id)
          }"
          :aria-current="currentStep === step.id ? 'step' : undefined"
          :aria-disabled="!canNavigateTo(step.id)"
          @click="handleStepClick(step.id)"
        >
          <span class="wizard-step-indicator">
            <svg v-if="isStepComplete(step.id)" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3">
              <polyline points="20 6 9 17 4 12"/>
            </svg>
            <span v-else>{{ step.id }}</span>
          </span>
          <span class="wizard-step-label">{{ step.title }}</span>
        </button>
      </div>
      <div class="wizard-step-hint" v-if="navHint">{{ navHint }}</div>
    </nav>

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
            Model Selection
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
            <div class="form-hint">一次生成多张图片（1-10）</div>
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
        <transition name="step-fade" mode="out-in">
          <section v-if="currentStep === 1" class="workflow-section">
          <div class="content-panel">
            <div class="panel-header">
              <div class="panel-title">
                <span class="step-indicator">1</span>
                <div>
                  <h3>产品选择</h3>
                  <p class="panel-subtitle">选择产品与参考图，并完善提示词字段</p>
                </div>
              </div>
              <span class="panel-hint" v-if="!selectedProduct">请先从左侧选择产品</span>
            </div>

            <div v-if="selectedProduct" class="product-fields">
              <div class="field-row">
                <label class="field-checkbox">
                  <input type="checkbox" v-model="fieldToggles.name">
                  <span>产品名称</span>
                </label>
                <input
                  type="text"
                  class="form-input"
                  v-model="editableProduct.name"
                  :disabled="!fieldToggles.name"
                  placeholder="例如：保温杯"
                >
              </div>
              <div class="field-row">
                <label class="field-checkbox">
                  <input type="checkbox" v-model="fieldToggles.dimensions">
                  <span>尺寸规格</span>
                </label>
                <input
                  type="text"
                  class="form-input"
                  v-model="editableProduct.dimensions"
                  :disabled="!fieldToggles.dimensions"
                  placeholder="例如：500ml"
                >
              </div>
              <div class="field-row">
                <label class="field-checkbox">
                  <input type="checkbox" v-model="fieldToggles.features">
                  <span>功能特征</span>
                </label>
                <textarea
                  class="form-input"
                  v-model="editableProduct.featuresText"
                  :disabled="!fieldToggles.features"
                  rows="2"
                  placeholder="每行一个特征"
                ></textarea>
              </div>
              <div class="field-row">
                <label class="field-checkbox">
                  <input type="checkbox" v-model="fieldToggles.characteristics">
                  <span>产品特点</span>
                </label>
                <textarea
                  class="form-input"
                  v-model="editableProduct.characteristicsText"
                  :disabled="!fieldToggles.characteristics"
                  rows="2"
                  placeholder="每行一个特点"
                ></textarea>
              </div>
            </div>
            <div v-else class="panel-empty">
              选择产品后将自动填充名称、规格与特征信息。
            </div>
          </div>
        </section>

          <section v-else-if="currentStep === 2" class="workflow-section">
          <div class="content-panel">
            <div class="panel-header">
              <div class="panel-title">
                <span class="step-indicator">2</span>
                <div>
                  <h3>模板配置</h3>
                  <p class="panel-subtitle">点击标签可多选，支持就地编辑</p>
                </div>
              </div>
              <button class="btn btn-ghost btn-sm" @click="resetTemplates">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <polyline points="1 4 1 10 7 10"/>
                  <path d="M3.51 15a9 9 0 1 0 2.13-9.36L1 10"/>
                </svg>
                重置模板
              </button>
            </div>

            <div class="template-modules">
              <CollapsibleGroup
                title="场景选择"
                :summary="getGroupSummary('scene')"
                :open="templateGroupOpen.scene"
                @toggle="toggleGroup('scene')"
              >
                <template #actions>
                  <button class="btn btn-ghost btn-icon-sm" @click.stop="addOption('scene')">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <line x1="12" y1="5" x2="12" y2="19"/>
                      <line x1="5" y1="12" x2="19" y2="12"/>
                    </svg>
                  </button>
                </template>
                <div class="option-chips">
                  <div
                    v-for="option in templates.scene"
                    :key="option.id"
                    class="option-chip"
                    :class="{
                      selected: selectedTemplates.scene.includes(option.id),
                      editing: isEditingOption('scene', option.id)
                    }"
                  >
                    <span
                      v-if="!isEditingOption('scene', option.id)"
                      @click="toggleOption('scene', option.id)"
                    >{{ option.label }}</span>
                    <input
                      v-else
                      type="text"
                      class="option-edit-input"
                      v-model="option.label"
                      :data-option-id="option.id"
                      @blur="finishEditing"
                      @keydown.enter.prevent="finishEditing"
                    >
                    <button
                      class="chip-edit"
                      @click.stop="startEditing('scene', option.id)"
                      v-if="!isEditingOption('scene', option.id)"
                    >
                      <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
                        <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
                      </svg>
                    </button>
                    <button class="chip-delete" @click.stop="removeOption('scene', option.id)">
                      <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <line x1="18" y1="6" x2="6" y2="18"/>
                        <line x1="6" y1="6" x2="18" y2="18"/>
                      </svg>
                    </button>
                  </div>
                </div>
              </CollapsibleGroup>

              <CollapsibleGroup
                title="拍摄角度"
                :summary="getGroupSummary('angle')"
                :open="templateGroupOpen.angle"
                @toggle="toggleGroup('angle')"
              >
                <template #actions>
                  <button class="btn btn-ghost btn-icon-sm" @click.stop="addOption('angle')">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <line x1="12" y1="5" x2="12" y2="19"/>
                      <line x1="5" y1="12" x2="19" y2="12"/>
                    </svg>
                  </button>
                </template>
                <div class="option-chips">
                  <div
                    v-for="option in templates.angle"
                    :key="option.id"
                    class="option-chip"
                    :class="{
                      selected: selectedTemplates.angle.includes(option.id),
                      editing: isEditingOption('angle', option.id)
                    }"
                  >
                    <span
                      v-if="!isEditingOption('angle', option.id)"
                      @click="toggleOption('angle', option.id)"
                    >{{ option.label }}</span>
                    <input
                      v-else
                      type="text"
                      class="option-edit-input"
                      v-model="option.label"
                      :data-option-id="option.id"
                      @blur="finishEditing"
                      @keydown.enter.prevent="finishEditing"
                    >
                    <button
                      class="chip-edit"
                      @click.stop="startEditing('angle', option.id)"
                      v-if="!isEditingOption('angle', option.id)"
                    >
                      <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
                        <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
                      </svg>
                    </button>
                    <button class="chip-delete" @click.stop="removeOption('angle', option.id)">
                      <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <line x1="18" y1="6" x2="6" y2="18"/>
                        <line x1="6" y1="6" x2="18" y2="18"/>
                      </svg>
                    </button>
                  </div>
                </div>
              </CollapsibleGroup>

              <CollapsibleGroup
                title="风格 / 光影"
                :summary="getGroupSummary('style')"
                :open="templateGroupOpen.style"
                @toggle="toggleGroup('style')"
              >
                <template #title-extra>
                  <span class="optional-tag">(可选)</span>
                </template>
                <template #actions>
                  <button class="btn btn-ghost btn-icon-sm" @click.stop="addOption('style')">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <line x1="12" y1="5" x2="12" y2="19"/>
                      <line x1="5" y1="12" x2="19" y2="12"/>
                    </svg>
                  </button>
                </template>
                <div class="option-chips">
                  <div
                    v-for="option in templates.style"
                    :key="option.id"
                    class="option-chip"
                    :class="{
                      selected: selectedTemplates.style.includes(option.id),
                      editing: isEditingOption('style', option.id)
                    }"
                  >
                    <span
                      v-if="!isEditingOption('style', option.id)"
                      @click="toggleOption('style', option.id)"
                    >{{ option.label }}</span>
                    <input
                      v-else
                      type="text"
                      class="option-edit-input"
                      v-model="option.label"
                      :data-option-id="option.id"
                      @blur="finishEditing"
                      @keydown.enter.prevent="finishEditing"
                    >
                    <button
                      class="chip-edit"
                      @click.stop="startEditing('style', option.id)"
                      v-if="!isEditingOption('style', option.id)"
                    >
                      <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
                        <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
                      </svg>
                    </button>
                    <button class="chip-delete" @click.stop="removeOption('style', option.id)">
                      <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <line x1="18" y1="6" x2="6" y2="18"/>
                        <line x1="6" y1="6" x2="18" y2="18"/>
                      </svg>
                    </button>
                  </div>
                </div>
              </CollapsibleGroup>

              <CollapsibleGroup
                title="生成目标"
                :summary="getGroupSummary('target')"
                :open="templateGroupOpen.target"
                @toggle="toggleGroup('target')"
              >
                <template #actions>
                  <button class="btn btn-ghost btn-icon-sm" @click.stop="addOption('target')">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <line x1="12" y1="5" x2="12" y2="19"/>
                      <line x1="5" y1="12" x2="19" y2="12"/>
                    </svg>
                  </button>
                </template>
                <div class="option-chips">
                  <div
                    v-for="option in templates.target"
                    :key="option.id"
                    class="option-chip"
                    :class="{
                      selected: selectedTemplates.target.includes(option.id),
                      editing: isEditingOption('target', option.id)
                    }"
                  >
                    <span
                      v-if="!isEditingOption('target', option.id)"
                      @click="toggleOption('target', option.id)"
                    >{{ option.label }}</span>
                    <input
                      v-else
                      type="text"
                      class="option-edit-input"
                      v-model="option.label"
                      :data-option-id="option.id"
                      @blur="finishEditing"
                      @keydown.enter.prevent="finishEditing"
                    >
                    <button
                      class="chip-edit"
                      @click.stop="startEditing('target', option.id)"
                      v-if="!isEditingOption('target', option.id)"
                    >
                      <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
                        <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
                      </svg>
                    </button>
                    <button class="chip-delete" @click.stop="removeOption('target', option.id)">
                      <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <line x1="18" y1="6" x2="6" y2="18"/>
                        <line x1="6" y1="6" x2="18" y2="18"/>
                      </svg>
                    </button>
                  </div>
                </div>
              </CollapsibleGroup>
            </div>

            <div class="template-editor">
              <div class="template-editor-header">
                <div>
                  <h4>提示词模板</h4>
                  <p class="template-editor-subtitle">系统会自动拼接已选信息，可补充额外描述</p>
                </div>
                <button class="btn btn-ghost btn-sm" @click="resetPromptTemplate">
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <polyline points="1 4 1 10 7 10"/>
                    <path d="M3.51 15a9 9 0 1 0 2.13-9.36L1 10"/>
                  </svg>
                  重置模板
                </button>
              </div>
              <div class="template-editor-section">
                <div class="template-editor-hint">
                  已选场景/角度等会自动生成，例如：场景：客厅，拍摄角度：正面。
                </div>
                <textarea
                  class="form-input template-textarea"
                  v-model="promptTemplate"
                  rows="4"
                  placeholder="补充提示词，如：高清产品摄影"
                  @input="savePromptTemplate"
                ></textarea>
              </div>
            </div>
          </div>
        </section>

          <section v-else-if="currentStep === 3" class="workflow-section">
          <div class="content-panel prompt-preview-panel">
            <div class="panel-header">
              <div class="panel-title">
                <span class="step-indicator">3</span>
                <div>
                  <h3>提示词预览</h3>
                  <p class="panel-subtitle">分段预览并高亮关键信息</p>
                </div>
              </div>
              <span class="panel-hint" v-if="!composedPrompt">完善产品信息与模板后自动生成</span>
            </div>

            <div class="prompt-structured">
              <div class="prompt-row">
                <span class="prompt-label">产品信息</span>
                <div class="prompt-value" :class="{ empty: promptSegments.product.length === 0 }">
                  <template v-if="promptSegments.product.length">
                    <span
                      v-for="(item, idx) in promptSegments.product"
                      :key="`product-${idx}`"
                      class="prompt-chip"
                    >{{ item }}</span>
                  </template>
                  <span v-else class="prompt-empty">未选择或未填写</span>
                </div>
              </div>
              <div class="prompt-row">
                <span class="prompt-label">场景</span>
                <div class="prompt-value" :class="{ empty: promptSegments.scene.length === 0 }">
                  <template v-if="promptSegments.scene.length">
                    <span
                      v-for="(item, idx) in promptSegments.scene"
                      :key="`scene-${idx}`"
                      class="prompt-chip"
                    >{{ item }}</span>
                  </template>
                  <span v-else class="prompt-empty">未选择场景</span>
                </div>
              </div>
              <div class="prompt-row">
                <span class="prompt-label">角度</span>
                <div class="prompt-value" :class="{ empty: promptSegments.angle.length === 0 }">
                  <template v-if="promptSegments.angle.length">
                    <span
                      v-for="(item, idx) in promptSegments.angle"
                      :key="`angle-${idx}`"
                      class="prompt-chip"
                    >{{ item }}</span>
                  </template>
                  <span v-else class="prompt-empty">未选择角度</span>
                </div>
              </div>
              <div class="prompt-row">
                <span class="prompt-label">风格 / 光影</span>
                <div class="prompt-value" :class="{ empty: promptSegments.style.length === 0 }">
                  <template v-if="promptSegments.style.length">
                    <span
                      v-for="(item, idx) in promptSegments.style"
                      :key="`style-${idx}`"
                      class="prompt-chip"
                    >{{ item }}</span>
                  </template>
                  <span v-else class="prompt-empty">未选择风格</span>
                </div>
              </div>
              <div class="prompt-row">
                <span class="prompt-label">生成目标</span>
                <div class="prompt-value" :class="{ empty: promptSegments.target.length === 0 }">
                  <template v-if="promptSegments.target.length">
                    <span
                      v-for="(item, idx) in promptSegments.target"
                      :key="`target-${idx}`"
                      class="prompt-chip"
                    >{{ item }}</span>
                  </template>
                  <span v-else class="prompt-empty">未选择目标</span>
                </div>
              </div>
            </div>

            <div class="prompt-full">
              <div class="prompt-full-header">
                <div>
                  <h4>完整 Prompt</h4>
                  <p class="prompt-full-hint">可直接复制用于生成</p>
                </div>
                <button class="btn btn-ghost btn-sm" @click="copyPrompt" :disabled="!composedPrompt">
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <rect x="9" y="9" width="13" height="13" rx="2" ry="2"/>
                    <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/>
                  </svg>
                  复制
                </button>
              </div>
              <div class="prompt-full-body">
                <p v-if="composedPrompt">{{ composedPrompt }}</p>
                <p v-else class="prompt-placeholder">选择产品和模板选项后，提示词将在这里生成。</p>
              </div>
            </div>
          </div>
        </section>

          <section v-else class="workflow-section">
          <div class="content-panel">
            <div class="panel-header">
              <div class="panel-title">
                <span class="step-indicator">4</span>
                <div>
                  <h3>生成与结果</h3>
                  <p class="panel-subtitle">确认参考图与提示词后开始生成</p>
                </div>
              </div>
              <span class="panel-hint" v-if="generationHint">{{ generationHint }}</span>
            </div>

            <div class="result-area">
              <div class="result-placeholder" v-if="!generating && generatedImages.length === 0">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                  <rect x="3" y="3" width="18" height="18" rx="2"/>
                  <circle cx="8.5" cy="8.5" r="1.5"/>
                  <polyline points="21 15 16 10 5 21"/>
                </svg>
                <h3>准备生成</h3>
                <p>选择产品、参考图片与模板选项，然后点击生成。</p>
              </div>

              <div class="loading-state" v-if="generating">
                <div class="spinner"></div>
                <p>正在生成图片...</p>
              </div>

              <div class="result-container" v-if="generatedImages.length && !generating">
                <img :src="generatedImage" alt="Generated image" class="result-image" @click="openLightbox(generatedImage)">
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
                <div class="result-actions">
                  <button class="btn btn-secondary" @click="() => downloadImage()">
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
              <div class="generate-hint" v-if="generationHint">{{ generationHint }}</div>
            </div>
          </div>
        </section>
        </transition>
      </main>

      <aside class="preview-panel">
        <div class="preview-card">
          <div class="preview-card-header">
            <h4>提示词预览</h4>
            <span class="preview-card-hint" v-if="!composedPrompt">完成前两步后显示</span>
          </div>
          <div class="preview-card-body">
            <p v-if="composedPrompt">{{ composedPrompt }}</p>
            <p v-else class="preview-placeholder">选择产品与模板选项后生成提示词。</p>
          </div>
        </div>

        <div class="preview-card">
          <div class="preview-card-header">
            <h4>生成结果</h4>
          </div>
          <div class="preview-card-body preview-result">
            <div v-if="generating" class="preview-loading">
              <div class="spinner-small"></div>
              <span>正在生成...</span>
            </div>
            <div v-else-if="generatedImage">
              <img :src="generatedImage" alt="Generated preview" class="preview-image" @click="openLightbox(generatedImage)">
            </div>
            <p v-else class="preview-placeholder">生成完成后显示结果。</p>
          </div>
        </div>
      </aside>
    </div>

    <!-- Lightbox -->
    <div class="lightbox-overlay" v-if="lightboxOpen" @click="closeLightbox">
      <div class="lightbox-content" @click.stop>
        <div class="lightbox-header">
          <div class="lightbox-title">放大预览</div>
          <button class="btn btn-ghost btn-icon" type="button" @click="closeLightbox" aria-label="Close preview">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="18" y1="6" x2="6" y2="18"/>
              <line x1="6" y1="6" x2="18" y2="18"/>
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
import { ref, reactive, computed, onMounted, onUnmounted, nextTick, watch } from 'vue';
import CollapsibleGroup from '../../components/CollapsibleGroup.vue';
import { apiFetch, getUserId, supabase } from '@/shared/supabase';

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

type TemplateCategory = 'scene' | 'angle' | 'style' | 'target';

interface TemplateOption {
  id: string;
  label: string;
}

// Default template options
const DEFAULT_TEMPLATES: Record<TemplateCategory, TemplateOption[]> = {
  scene: [
    { id: 'scene-white', label: '白色背景' },
    { id: 'scene-natural-table', label: '自然光桌面' },
    { id: 'scene-outdoor', label: '户外场景' },
    { id: 'scene-solid', label: '纯色背景' },
    { id: 'scene-life', label: '生活场景' }
  ],
  angle: [
    { id: 'angle-front', label: '正面' },
    { id: 'angle-45', label: '45度侧面' },
    { id: 'angle-top', label: '俯视' },
    { id: 'angle-eye', label: '平视' },
    { id: 'angle-close', label: '特写' }
  ],
  style: [
    { id: 'style-soft', label: '柔和光影' },
    { id: 'style-contrast', label: '高对比度' },
    { id: 'style-natural', label: '自然光' },
    { id: 'style-studio', label: '专业棚拍' },
    { id: 'style-warm', label: '暖色调' }
  ],
  target: [
    { id: 'target-main', label: '主图' },
    { id: 'target-detail', label: '详情页' },
    { id: 'target-poster', label: '海报' },
    { id: 'target-white', label: '白底图' },
    { id: 'target-scene', label: '场景图' }
  ]
};

// Default extra prompt text
const DEFAULT_PROMPT_TEMPLATE = '高清产品摄影';

// State
const apiConfig = reactive({
  apiKey: '',
  baseUrl: ''
});

const modelConfig = reactive({
  model: 'gemini-3-pro-image-preview',
  aspectRatio: '',
  imageSize: '1K',
  n: 1
});

const steps = [
  { id: 1, title: '选择产品' },
  { id: 2, title: '配置模板' },
  { id: 3, title: '预览提示词' },
  { id: 4, title: '生成图片' }
];

const currentStep = ref(1);
const navHint = ref('');

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
  scene: DEFAULT_TEMPLATES.scene.map((option) => ({ ...option })),
  angle: DEFAULT_TEMPLATES.angle.map((option) => ({ ...option })),
  style: DEFAULT_TEMPLATES.style.map((option) => ({ ...option })),
  target: DEFAULT_TEMPLATES.target.map((option) => ({ ...option }))
});

const selectedTemplates = reactive({
  scene: [] as string[],
  angle: [] as string[],
  style: [] as string[],
  target: [] as string[]
});

const templateGroupOpen = reactive<Record<TemplateCategory, boolean>>({
  scene: true,
  angle: false,
  style: false,
  target: false
});

const templateGroupTouched = ref(false);

const editingOption = reactive({
  category: '' as TemplateCategory | '',
  id: ''
});

// Prompt Template
const promptTemplate = ref(DEFAULT_PROMPT_TEMPLATE);

// Generation
const generating = ref(false);
const generatedImage = ref('');
const generatedImages = ref<string[]>([]);
const errorMessage = ref('');
const toasts = ref<Toast[]>([]);

const lightboxOpen = ref(false);
const lightboxIndex = ref(0);

const lightboxImage = computed(() => {
  const imgs = generatedImages.value;
  if (!imgs.length) return '';
  const idx = Math.min(imgs.length - 1, Math.max(0, lightboxIndex.value));
  return imgs[idx] || '';
});

// Computed
const totalPages = computed(() => Math.ceil(totalProducts.value / pageSize));

function generateOptionId(category: TemplateCategory): string {
  if (globalThis.crypto && 'randomUUID' in globalThis.crypto) {
    return `${category}-${globalThis.crypto.randomUUID()}`;
  }
  return `${category}-${Date.now()}-${Math.random().toString(16).slice(2)}`;
}

function splitLines(text: string): string[] {
  return text
    .split('\n')
    .map((line) => line.trim())
    .filter(Boolean);
}

function joinTokens(tokens: string[]): string {
  return tokens.filter(Boolean).join('、');
}

function getSelectedLabels(category: TemplateCategory): string[] {
  const selected = new Set(selectedTemplates[category]);
  return templates[category]
    .filter((option) => selected.has(option.id))
    .map((option) => option.label.trim())
    .filter(Boolean);
}

function isEditingOption(category: TemplateCategory, optionId: string): boolean {
  return editingOption.category === category && editingOption.id === optionId;
}

const selectedLabels = computed(() => ({
  scene: getSelectedLabels('scene'),
  angle: getSelectedLabels('angle'),
  style: getSelectedLabels('style'),
  target: getSelectedLabels('target')
}));

const hasTemplateSelection = computed(() => {
  return selectedTemplates.scene.length > 0 ||
    selectedTemplates.angle.length > 0 ||
    selectedTemplates.style.length > 0 ||
    selectedTemplates.target.length > 0;
});

function getGroupSummary(category: TemplateCategory): string {
  const labels = selectedLabels.value[category];
  if (!labels.length) return '未选择';
  if (labels.length <= 2) return labels.join('、');
  return `${labels[0]}、${labels[1]} 等${labels.length}项`;
}

function toggleGroup(category: TemplateCategory) {
  templateGroupOpen[category] = !templateGroupOpen[category];
  templateGroupTouched.value = true;
}

function initializeTemplateGroups(force: boolean = false) {
  if (templateGroupTouched.value && !force) return;
  const categories: TemplateCategory[] = ['scene', 'angle', 'style', 'target'];
  let opened = false;
  categories.forEach((category) => {
    if (!opened && selectedTemplates[category].length === 0) {
      templateGroupOpen[category] = true;
      opened = true;
    } else {
      templateGroupOpen[category] = false;
    }
  });
  templateGroupTouched.value = false;
}

const productTokens = computed(() => {
  const tokens: string[] = [];
  const name = editableProduct.name.trim();
  const dimensions = editableProduct.dimensions.trim();

  if (fieldToggles.name && name) tokens.push(name);
  if (fieldToggles.dimensions && dimensions) tokens.push(dimensions);
  if (fieldToggles.features) tokens.push(...splitLines(editableProduct.featuresText));
  if (fieldToggles.characteristics) tokens.push(...splitLines(editableProduct.characteristicsText));

  return tokens;
});

const promptSegments = computed(() => ({
  product: productTokens.value,
  scene: selectedLabels.value.scene,
  angle: selectedLabels.value.angle,
  style: selectedLabels.value.style,
  target: selectedLabels.value.target
}));

function formatKeyedSegment(label: string, values: string[]): string {
  if (!values.length) return '';
  return `${label}：${joinTokens(values)}`;
}

function normalizePrompt(text: string): string {
  return text
    // Clean up multiple consecutive separators (，、)
    .replace(/[，、]{2,}/g, '，')
    // Clean up leading/trailing separators
    .replace(/^[，、\s]+/, '')
    .replace(/[，、\s]+$/, '')
    // Clean up spaces around separators
    .replace(/\s*[，、]\s*/g, '，')
    .trim();
}

function sanitizePromptTemplate(template: string): string {
  if (!template) return '';
  const trimmed = template.trim();
  if (!trimmed.includes('{{')) return trimmed;
  const withoutVariables = trimmed.replace(/\{\{(\w+)(?:\|([^}]*))?\}\}/g, (_match, _varName, defaultValue) => {
    return defaultValue ?? '';
  });
  return normalizePrompt(withoutVariables);
}

const composedPrompt = computed(() => {
  if (!selectedProduct.value) return '';
  const segments: string[] = [];

  if (productTokens.value.length) {
    segments.push(joinTokens(productTokens.value));
  }

  const sceneSegment = formatKeyedSegment('场景', selectedLabels.value.scene);
  if (sceneSegment) segments.push(sceneSegment);

  const angleSegment = formatKeyedSegment('拍摄角度', selectedLabels.value.angle);
  if (angleSegment) segments.push(angleSegment);

  const styleSegment = formatKeyedSegment('风格', selectedLabels.value.style);
  if (styleSegment) segments.push(styleSegment);

  const targetSegment = formatKeyedSegment('生成目标', selectedLabels.value.target);
  if (targetSegment) segments.push(targetSegment);

  const extraText = sanitizePromptTemplate(promptTemplate.value);
  if (extraText) segments.push(extraText);

  return normalizePrompt(segments.join('，'));
});

const canGenerate = computed(() => {
  return selectedProduct.value &&
         selectedImages.value.length > 0 &&
         composedPrompt.value.length > 0;
});

const generationHint = computed(() => {
  if (generating.value) return '正在生成图片...';
  if (!selectedProduct.value) return '请先在左侧选择产品';
  if (selectedImages.value.length === 0) return '请选择至少一张参考图片';
  if (!composedPrompt.value) return '请完善模板选项或产品信息';
  return '';
});

function isStepComplete(stepId: number): boolean {
  if (stepId === 1) {
    return !!selectedProduct.value && selectedImages.value.length > 0;
  }
  if (stepId === 2) {
    return hasTemplateSelection.value;
  }
  if (stepId === 3) {
    return composedPrompt.value.length > 0;
  }
  if (stepId === 4) {
    return generatedImage.value.length > 0;
  }
  return false;
}

const maxNavigableStep = computed(() => {
  if (!isStepComplete(1)) return 1;
  if (!isStepComplete(2)) return 2;
  if (!isStepComplete(3)) return 3;
  return 4;
});

function canNavigateTo(stepId: number): boolean {
  return stepId <= maxNavigableStep.value;
}

function getBlockedHint(): string {
  if (!isStepComplete(1)) return '请先完成步骤1：选择产品并勾选参考图';
  if (!isStepComplete(2)) return '请先完成步骤2：至少选择一个模板选项';
  if (!isStepComplete(3)) return '请先完成步骤3：完善提示词预览';
  return '请先完成前置步骤';
}

function handleStepClick(stepId: number) {
  if (canNavigateTo(stepId)) {
    currentStep.value = stepId;
    navHint.value = '';
    return;
  }
  navHint.value = getBlockedHint();
}

// Methods
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
      if (!item || typeof item !== 'object') continue;
      if (typeof item.url === 'string' && item.url) urls.push(item.url);
      else if (typeof item.b64_json === 'string' && item.b64_json) urls.push(`data:image/png;base64,${item.b64_json}`);
      else if (typeof item.image_url === 'string' && item.image_url) urls.push(item.image_url);
      else if (typeof item.imageUrl === 'string' && item.imageUrl) urls.push(item.imageUrl);
    }
  }

  if (typeof payload.url === 'string' && payload.url) urls.push(payload.url);
  if (typeof payload.b64_json === 'string' && payload.b64_json) urls.push(`data:image/png;base64,${payload.b64_json}`);
  if (typeof payload.image_url === 'string' && payload.image_url) urls.push(payload.image_url);
  if (typeof payload.imageUrl === 'string' && payload.imageUrl) urls.push(payload.imageUrl);

  return Array.from(new Set(urls));
}

function extractImageUrl(payload: any): string | null {
  return extractImageUrls(payload)[0] ?? null;
}

async function fetchProducts() {
  loadingProducts.value = true;
  try {
    const start = (currentPage.value - 1) * pageSize;
    const end = start + pageSize - 1;

    let query = supabase
      .from('products')
      .select('id,name,dimensions,features,characteristics,original_image_url,created_at', { count: 'exact' })
      .order('created_at', { ascending: false })
      .range(start, end);

    if (productSearch.value) {
      query = query.ilike('name', `%${productSearch.value}%`);
    }

    const { data, error, count } = await query;
    if (error) throw error;

    const rows = (data || []) as any[];
    const ids = rows.map((p) => p.id);
    const imagesByProductId = new Map<string, ProductImage[]>();

    if (ids.length) {
      const { data: imgs, error: imgsError } = await supabase
        .from('product_images')
        .select('id,product_id,image_url,is_primary')
        .in('product_id', ids);
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
    const { data: detail, error } = await supabase.from('products').select('*').eq('id', product.id).single();
    if (error) throw error;

    const { data: imgs, error: imgsError } = await supabase
      .from('product_images')
      .select('id,image_url,is_primary')
      .eq('product_id', product.id)
      .order('is_primary', { ascending: false });
    if (imgsError) throw imgsError;

    // Update editable fields
    editableProduct.name = (detail as any).name || '';
    editableProduct.dimensions = (detail as any).dimensions || '';
    editableProduct.featuresText = ((detail as any).features || []).join('\n');
    editableProduct.characteristicsText = ((detail as any).characteristics || []).join('\n');

    // Load images
    productImages.value = ((imgs as any[]) || []) as ProductImage[];
    const originalUrl = (detail as any).original_image_url as string | null | undefined;
    if (productImages.value.length === 0 && originalUrl) {
      productImages.value = [{
        id: (detail as any).id,
        image_url: originalUrl,
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

function findOption(category: TemplateCategory, optionId: string): TemplateOption | null {
  return templates[category].find((option) => option.id === optionId) ?? null;
}

function focusOptionInput(optionId: string) {
  nextTick(() => {
    const input = document.querySelector<HTMLInputElement>(`.option-edit-input[data-option-id="${optionId}"]`);
    if (input) {
      input.focus();
      input.select();
    }
  });
}

function toggleOption(category: TemplateCategory, optionId: string) {
  const list = selectedTemplates[category];
  const index = list.indexOf(optionId);
  if (index === -1) {
    list.push(optionId);
  } else {
    list.splice(index, 1);
  }
}

function addOption(category: TemplateCategory) {
  const newOption = {
    id: generateOptionId(category),
    label: '新选项'
  };
  templates[category].push(newOption);
  saveTemplates();
  startEditing(category, newOption.id);
}

function removeOption(category: TemplateCategory, optionId: string) {
  const index = templates[category].findIndex((option) => option.id === optionId);
  if (index === -1) return;
  templates[category].splice(index, 1);

  const selectedIndex = selectedTemplates[category].indexOf(optionId);
  if (selectedIndex !== -1) {
    selectedTemplates[category].splice(selectedIndex, 1);
  }

  if (editingOption.category === category && editingOption.id === optionId) {
    editingOption.category = '';
    editingOption.id = '';
  }

  saveTemplates();
}

function startEditing(category: TemplateCategory, optionId: string) {
  editingOption.category = category;
  editingOption.id = optionId;
  focusOptionInput(optionId);
}

function finishEditing() {
  if (!editingOption.category || !editingOption.id) return;
  const category = editingOption.category;
  const optionId = editingOption.id;
  editingOption.category = '';
  editingOption.id = '';

  const option = findOption(category, optionId);
  if (!option) return;

  const trimmed = option.label.trim();
  if (!trimmed) {
    removeOption(category, optionId);
    return;
  }

  option.label = trimmed;
  saveTemplates();
}

function resetTemplates() {
  templates.scene = DEFAULT_TEMPLATES.scene.map((option) => ({ ...option }));
  templates.angle = DEFAULT_TEMPLATES.angle.map((option) => ({ ...option }));
  templates.style = DEFAULT_TEMPLATES.style.map((option) => ({ ...option }));
  templates.target = DEFAULT_TEMPLATES.target.map((option) => ({ ...option }));

  selectedTemplates.scene = [];
  selectedTemplates.angle = [];
  selectedTemplates.style = [];
  selectedTemplates.target = [];
  editingOption.category = '';
  editingOption.id = '';
  templateGroupTouched.value = false;
  initializeTemplateGroups(true);

  localStorage.removeItem('ecommerce-image-templates');
  showToast('模板已重置为默认值', 'success');
}

function saveTemplates() {
  const payload = {
    version: 2,
    templates: {
      scene: templates.scene.map((option) => ({ id: option.id, label: option.label })),
      angle: templates.angle.map((option) => ({ id: option.id, label: option.label })),
      style: templates.style.map((option) => ({ id: option.id, label: option.label })),
      target: templates.target.map((option) => ({ id: option.id, label: option.label }))
    }
  };
  localStorage.setItem('ecommerce-image-templates', JSON.stringify(payload));
}

function normalizeTemplateList(raw: unknown, category: TemplateCategory): TemplateOption[] | null {
  if (!Array.isArray(raw)) return null;
  const options: TemplateOption[] = [];
  for (const entry of raw) {
    if (typeof entry === 'string') {
      const label = entry.trim();
      if (label) options.push({ id: generateOptionId(category), label });
      continue;
    }
    if (entry && typeof entry === 'object') {
      const label = typeof (entry as { label?: unknown }).label === 'string'
        ? (entry as { label: string }).label.trim()
        : '';
      if (!label) continue;
      const id = typeof (entry as { id?: unknown }).id === 'string'
        ? String((entry as { id: string }).id)
        : generateOptionId(category);
      options.push({ id, label });
    }
  }
  return options.length ? options : null;
}

function loadTemplates() {
  const saved = localStorage.getItem('ecommerce-image-templates');
  if (!saved) return;
  try {
    const parsed = JSON.parse(saved);
    const source = parsed?.templates || parsed;
    const scene = normalizeTemplateList(source?.scene, 'scene');
    const angle = normalizeTemplateList(source?.angle, 'angle');
    const style = normalizeTemplateList(source?.style, 'style');
    const target = normalizeTemplateList(source?.target, 'target');
    if (scene) templates.scene = scene;
    if (angle) templates.angle = angle;
    if (style) templates.style = style;
    if (target) templates.target = target;
  } catch {
    // Ignore parse errors
  }
}

// Prompt template functions
function savePromptTemplate() {
  const sanitized = sanitizePromptTemplate(promptTemplate.value);
  if (sanitized !== promptTemplate.value) {
    promptTemplate.value = sanitized;
  }
  localStorage.setItem('ecommerce-image-prompt-template', sanitized);
}

function loadPromptTemplate() {
  const saved = localStorage.getItem('ecommerce-image-prompt-template');
  if (saved) {
    promptTemplate.value = sanitizePromptTemplate(saved);
  }
}

function resetPromptTemplate() {
  promptTemplate.value = DEFAULT_PROMPT_TEMPLATE;
  localStorage.removeItem('ecommerce-image-prompt-template');
  showToast('提示词模板已重置为默认值', 'success');
}

function loadApiConfig() {
  // Load from global config keys (set in portal page), fallback to env vars
  apiConfig.apiKey = localStorage.getItem('global_api_key') || localStorage.getItem('video_api_key') || import.meta.env.VITE_IMAGE_GEN_API_KEY || '';
  apiConfig.baseUrl = localStorage.getItem('global_base_url') || localStorage.getItem('video_base_url') || import.meta.env.VITE_IMAGE_GEN_API_URL || '';
}

async function copyPrompt() {
  if (!composedPrompt.value) return;

  try {
    await navigator.clipboard.writeText(composedPrompt.value);
    showToast('提示词已复制到剪贴板', 'success');
  } catch (e) {
    showToast('复制失败', 'error');
  }
}

async function generateImage() {
  if (!canGenerate.value || generating.value) return;

  generating.value = true;
  errorMessage.value = '';
  closeLightbox();

  try {
    const batchCount = Math.min(10, Math.max(1, Math.floor(Number(modelConfig.n) || 1)));
    modelConfig.n = batchCount;
    if (batchCount >= 6) {
      const ok = confirm(`将并发生成 ${batchCount} 张图片，确认继续？`);
      if (!ok) return;
    }

    // Prepare form data
    const formData = new FormData();
    formData.append('prompt', composedPrompt.value);
    formData.append('model', modelConfig.model);
    formData.append('n', String(batchCount));
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

    const headers: Record<string, string> = {};
    const apiKey = normalizeApiKey(apiConfig.apiKey);
    if (apiKey) headers['X-API-Key'] = apiKey;
    const baseUrl = normalizeBaseUrl(apiConfig.baseUrl);
    if (baseUrl) headers['X-Base-Url'] = baseUrl;

    const res = await apiFetch('/api/v1/images/edits', {
      method: 'POST',
      headers,
      body: formData
    });

    if (!res.ok) {
      const errData = await res.json().catch(() => ({}));
      throw new Error(errData.detail || `HTTP ${res.status}`);
    }

    const data = await res.json();
    const payload = data && typeof data === 'object' && data.response ? data.response : data;
    const urls = extractImageUrls(payload).length ? extractImageUrls(payload) : extractImageUrls(data);

    if (urls.length) {
      generatedImages.value = urls;
      generatedImage.value = urls[0] || '';
    } else {
      throw new Error('Invalid response format');
    }

    showToast(urls.length > 1 ? `图片生成成功（${urls.length}张）` : '图片生成成功', 'success');

    const userId = await getUserId();
    if (userId) {
      const rows = urls.map((url, idx) => ({
        user_id: userId,
        title: selectedProduct.value?.name ? `电商图 - ${selectedProduct.value.name}` : null,
        model: modelConfig.model,
        prompt: composedPrompt.value,
        status: 'completed',
        image_url: url,
        metadata: {
          source: 'ecommerce-image',
          product_id: selectedProduct.value?.id || null,
          selected_templates: {
            scene: [...selectedTemplates.scene],
            angle: [...selectedTemplates.angle],
            style: [...selectedTemplates.style],
            target: [...selectedTemplates.target],
          },
          selected_images: selectedImages.value,
          aspect_ratio: modelConfig.aspectRatio || null,
          image_size: modelConfig.imageSize || null,
          index: idx,
        },
        request: (data && typeof data === 'object' && (data as any).request) ? (data as any).request : null,
        response: (data && typeof data === 'object' && (data as any).response) ? (data as any).response : data,
      }));

      const { error: insertError } = await supabase.from('user_images').insert(rows);
      if (insertError) console.warn('Failed to save images to repository:', insertError);
    }
  } catch (e: any) {
    errorMessage.value = e.message || '生成失败，请重试';
  } finally {
    generating.value = false;
  }
}

function downloadImage(url?: string) {
  const imageUrl = url || generatedImage.value;
  if (!imageUrl) return;

  const link = document.createElement('a');
  link.href = imageUrl;
  link.download = `ecommerce-${Date.now()}.png`;
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

  if (e.key === 'Escape') {
    e.preventDefault();
    closeLightbox();
    return;
  }
  if (e.key === 'ArrowLeft') {
    e.preventDefault();
    prevLightbox();
    return;
  }
  if (e.key === 'ArrowRight') {
    e.preventDefault();
    nextLightbox();
  }
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

watch(currentStep, (step) => {
  navHint.value = '';
  if (step === 2) {
    initializeTemplateGroups();
  }
});

watch(maxNavigableStep, (step) => {
  if (currentStep.value > step) {
    currentStep.value = step;
  }
});

// Lifecycle
onMounted(() => {
  loadTemplates();
  loadPromptTemplate();
  loadApiConfig();
  fetchProducts();
  initializeTemplateGroups(true);
  document.addEventListener('keydown', handleLightboxKeydown);
});

onUnmounted(() => {
  document.removeEventListener('keydown', handleLightboxKeydown);
});

watch(lightboxOpen, (open) => {
  document.body.style.overflow = open ? 'hidden' : '';
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
