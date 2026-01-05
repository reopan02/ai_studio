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
            <label class="form-label">生成数量</label>
            <select class="form-select" v-model="modelConfig.generateCount">
              <option v-for="n in 4" :key="n" :value="n">{{ n }} 张</option>
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
              :class="{
                selected: selectedProduct?.id === product.id,
                loading: selectingProductId === product.id
              }"
              @click="selectProduct(product)"
            >
              <div class="product-thumb-wrap">
                <img :src="getProductThumbnail(product)" :alt="product.name" class="product-thumb">
                <span v-if="product.image_count > 1" class="product-count-badge">{{ product.image_count }}</span>
              </div>
              <div class="product-info">
                <div class="product-name">{{ product.name || '未命名产品' }}</div>
                <div class="product-meta">
                  <span v-if="product.dimensions">{{ product.dimensions }}</span>
                  <span v-if="product.dimensions && product.image_count">·</span>
                  <span v-if="product.image_count">{{ product.image_count }} 张</span>
                </div>
              </div>
              <div
                class="product-select-indicator"
                :class="{ active: selectedProduct?.id === product.id }"
              >
                <div v-if="selectingProductId === product.id" class="spinner-small"></div>
                <svg v-else-if="selectedProduct?.id === product.id" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3">
                  <polyline points="20 6 9 17 4 12"/>
                </svg>
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
                :summary="selectedTargetType ? selectedTargetType.name : '未选择'"
                :open="templateGroupOpen.target"
                @toggle="toggleGroup('target')"
              >
                <div class="target-type-selector">
                  <div class="target-type-options">
                    <label
                      v-for="target in targetTypes"
                      :key="target.id"
                      class="target-type-radio"
                      :class="{ selected: selectedTargetTypeId === target.id }"
                    >
                      <input
                        type="radio"
                        name="target-type"
                        :value="target.id"
                        v-model="selectedTargetTypeId"
                        @change="selectTargetType(target.id)"
                      >
                      <span class="target-type-label">{{ target.name }}</span>
                    </label>
                  </div>
                  <div class="target-description-input" v-if="selectedTargetTypeId">
                    <!-- Saved descriptions dropdown -->
                    <div class="saved-descriptions-section" v-if="savedDescriptions.length > 0">
                      <label class="target-description-label">已保存的描述</label>
                      <div class="saved-descriptions-list">
                        <div
                          v-for="saved in savedDescriptions"
                          :key="saved.id"
                          class="saved-description-item"
                          :class="{ active: currentSavedDescriptionId === saved.id }"
                        >
                          <button
                            class="saved-description-btn"
                            @click="loadSavedDescription(saved)"
                          >
                            {{ saved.name }}
                          </button>
                          <button
                            class="saved-description-delete"
                            @click.stop="deleteSavedDescription(saved.id)"
                            title="删除"
                          >
                            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                              <line x1="18" y1="6" x2="6" y2="18"/>
                              <line x1="6" y1="6" x2="18" y2="18"/>
                            </svg>
                          </button>
                        </div>
                      </div>
                    </div>

                    <label class="target-description-label">目标描述</label>
                    <textarea
                      class="form-input target-textarea"
                      v-model="targetDescription"
                      :placeholder="targetPlaceholder"
                      :disabled="targetDescriptionLoading || targetDescriptionSaving"
                      rows="3"
                    ></textarea>
                    <div class="target-description-actions">
                      <button
                        class="btn btn-secondary btn-sm"
                        type="button"
                        @click="showSaveDialog = true"
                        :disabled="!targetDescription.trim() || targetDescriptionSaving"
                      >
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                          <path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"/>
                          <polyline points="17 21 17 13 7 13 7 21"/>
                          <polyline points="7 3 7 8 15 8"/>
                        </svg>
                        保存描述
                      </button>
                      <button
                        class="btn btn-ghost btn-sm"
                        type="button"
                        @click="resetToDefaultTemplate"
                        :disabled="!selectedTargetType"
                      >
                        重置为默认
                      </button>
                    </div>
                    <p class="target-description-hint">
                      描述将作为生成提示词的一部分，请详细描述您期望的效果
                    </p>
                  </div>
                  <div class="target-loading" v-if="loadingTargetTypes">
                    <div class="spinner-small"></div>
                    <span>加载目标类型...</span>
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
              placeholder="补充提示词"
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
                <div class="prompt-value" :class="{ empty: !targetDescription }">
                  <template v-if="targetDescription">
                    <span class="prompt-chip target-chip">
                      <span class="target-chip-name" v-if="selectedTargetType">{{ selectedTargetType.name }}：</span>
                      {{ targetDescription }}
                    </span>
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
                <p v-if="generationProgress.total > 1">正在生成图片 ({{ generationProgress.current }}/{{ generationProgress.total }})...</p>
                <p v-else>正在生成图片...</p>
              </div>

              <div class="result-container" v-if="generatedImages.length > 0 && !generating">
                <div class="result-grid" :class="{ 'single-image': generatedImages.length === 1 }">
                  <div
                    v-for="(img, idx) in generatedImages"
                    :key="idx"
                    class="result-image-item"
                  >
                    <img :src="img" alt="Generated image" class="result-image">
                    <div class="result-image-overlay">
                      <button class="btn btn-ghost btn-icon" @click="downloadSingleImage(img, idx)" title="下载">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                          <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                          <polyline points="7 10 12 15 17 10"/>
                          <line x1="12" y1="15" x2="12" y2="3"/>
                        </svg>
                      </button>
                    </div>
                  </div>
                </div>
                <div class="result-actions">
                  <button class="btn btn-secondary" @click="downloadAllImages" v-if="generatedImages.length > 1">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                      <polyline points="7 10 12 15 17 10"/>
                      <line x1="12" y1="15" x2="12" y2="3"/>
                    </svg>
                    下载全部 ({{ generatedImages.length }})
                  </button>
                  <button class="btn btn-secondary" @click="downloadSingleImage(generatedImages[0], 0)" v-else>
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

            <!-- Generation History -->
            <div class="history-section" v-if="generationHistory.length > 0 || loadingHistory">
              <div class="history-header">
                <h4>
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <circle cx="12" cy="12" r="10"/>
                    <polyline points="12 6 12 12 16 14"/>
                  </svg>
                  生成历史
                </h4>
                <span class="history-count" v-if="generationHistory.length > 0">({{ generationHistory.length }})</span>
              </div>
              <div class="history-grid" v-if="!loadingHistory && generationHistory.length > 0">
                <div
                  v-for="item in generationHistory"
                  :key="item.id"
                  class="history-item"
                  @click="loadHistoryItem(item)"
                >
                  <img :src="item.image_url || placeholderImage" :alt="item.prompt" class="history-thumb">
                  <div class="history-info">
                    <div class="history-prompt">{{ truncateText(item.prompt, 40) }}</div>
                    <div class="history-meta">{{ formatHistoryDate(item.created_at) }}</div>
                  </div>
                </div>
              </div>
              <div class="history-loading" v-else-if="loadingHistory">
                <div class="spinner-small"></div>
                <span>加载中...</span>
              </div>
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
            <span v-if="generatedImages.length > 1" class="preview-count">({{ generatedImages.length }})</span>
          </div>
          <div class="preview-card-body preview-result">
            <div v-if="generating" class="preview-loading">
              <div class="spinner-small"></div>
              <span v-if="generationProgress.total > 1">{{ generationProgress.current }}/{{ generationProgress.total }}</span>
              <span v-else>正在生成...</span>
            </div>
            <div v-else-if="generatedImages.length > 0" class="preview-images-grid">
              <img
                v-for="(img, idx) in generatedImages.slice(0, 4)"
                :key="idx"
                :src="img"
                alt="Generated preview"
                class="preview-image"
              >
            </div>
            <p v-else class="preview-placeholder">生成完成后显示结果。</p>
          </div>
        </div>
      </aside>
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

    <!-- Save Description Dialog -->
    <div class="save-dialog-overlay" v-if="showSaveDialog" @click="showSaveDialog = false">
      <div class="save-dialog-modal" @click.stop>
        <div class="save-dialog-header">
          <h3>保存目标描述</h3>
          <button class="save-dialog-close" @click="showSaveDialog = false">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="18" y1="6" x2="6" y2="18"/>
              <line x1="6" y1="6" x2="18" y2="18"/>
            </svg>
          </button>
        </div>
        <div class="save-dialog-body">
          <div class="form-group">
            <label class="form-label">描述名称</label>
            <input
              type="text"
              class="form-input"
              v-model="saveDescriptionName"
              placeholder="例如：清新自然风格"
              maxlength="100"
            >
          </div>
          <div class="form-group">
            <label class="form-label">描述内容</label>
            <textarea
              class="form-input"
              :value="targetDescription"
              readonly
              rows="3"
            ></textarea>
          </div>
        </div>
        <div class="save-dialog-footer">
          <button class="btn btn-secondary" @click="showSaveDialog = false">取消</button>
          <button
            class="btn btn-primary"
            @click="saveNewDescription"
            :disabled="!saveDescriptionName.trim() || targetDescriptionSaving"
          >
            {{ targetDescriptionSaving ? '保存中...' : '保存' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, nextTick, watch } from 'vue';
import CollapsibleGroup from '../../components/CollapsibleGroup.vue';

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

interface TargetType {
  id: string;
  name: string;
  placeholder: string | null;
  default_template: string | null;
  sort_order: number;
}

interface SavedTargetDescription {
  id: string;
  user_id: string;
  target_type_id: string;
  name: string;
  description: string;
  created_at: string;
  updated_at: string | null;
}

interface HistoryItem {
  id: string;
  prompt: string;
  image_url: string | null;
  model: string;
  created_at: string;
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

// Default target types (fallback when API fails)
const DEFAULT_TARGET_TYPES: TargetType[] = [
  { id: 'target-main', name: '主图', placeholder: '请描述主图的展示重点，如产品摆放方式、突出的卖点...', default_template: '适合电商主图展示的产品图，突出产品整体外观，简洁大方', sort_order: 0 },
  { id: 'target-detail', name: '详情页', placeholder: '请描述详情页需要展示的产品细节或使用场景...', default_template: '适合详情页的产品展示图，展现产品细节和使用场景', sort_order: 1 },
  { id: 'target-poster', name: '海报', placeholder: '请描述海报的主题和风格，如促销活动、节日氛围...', default_template: '具有视觉冲击力的营销海报风格，适合活动推广', sort_order: 2 },
  { id: 'target-white', name: '白底图', placeholder: '请描述白底图的拍摄角度和展示方式...', default_template: '纯白色背景的产品图，适合平台商品展示', sort_order: 3 },
  { id: 'target-scene', name: '场景图', placeholder: '请描述期望的使用场景和环境氛围...', default_template: '产品在真实使用场景中的展示图，增强代入感', sort_order: 4 }
];

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
const DEFAULT_PROMPT_TEMPLATE = '';

// State
const apiConfig = reactive({
  apiKey: '',
  baseUrl: ''
});

const modelConfig = reactive({
  model: 'gemini-3-pro-image-preview',
  aspectRatio: '',
  imageSize: '1K',
  generateCount: 1
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
const selectingProductId = ref<string | null>(null);

// Generation History
const generationHistory = ref<HistoryItem[]>([]);
const loadingHistory = ref(false);
const placeholderImage = 'data:image/svg+xml;charset=utf-8,' + encodeURIComponent(`
<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100" viewBox="0 0 100 100">
  <rect width="100" height="100" fill="#1a1a2e"/>
  <rect x="25" y="25" width="50" height="50" rx="4" fill="none" stroke="#4a4a6a" stroke-width="2"/>
  <circle cx="38" cy="38" r="5" fill="#4a4a6a"/>
  <path d="M25 65 L45 45 L55 55 L75 35 L75 75 L25 75 Z" fill="#4a4a6a" opacity="0.5"/>
</svg>
`);

// Editable product fields
const editableProduct = reactive({
  name: '',
  dimensions: '',
  featuresText: '',
  characteristicsText: ''
});

// Target types
const targetTypes = ref<TargetType[]>([]);
const loadingTargetTypes = ref(false);
const selectedTargetTypeId = ref<string | null>(null);
const targetDescription = ref('');
const targetDescriptionLoading = ref(false);
const targetDescriptionSaving = ref(false);
const savedDescriptions = ref<SavedTargetDescription[]>([]);
const showSaveDialog = ref(false);
const currentSavedDescriptionId = ref<string | null>(null);
const saveDescriptionName = ref('');

const selectedTargetType = computed(() => {
  if (!selectedTargetTypeId.value) return null;
  return targetTypes.value.find(t => t.id === selectedTargetTypeId.value) || null;
});

const targetPlaceholder = computed(() => {
  return selectedTargetType.value?.placeholder || '请描述您期望的生成效果...';
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
const generatedImages = ref<string[]>([]);
const generationProgress = ref({ current: 0, total: 0 });
const errorMessage = ref('');
const toasts = ref<Toast[]>([]);

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
    !!selectedTargetTypeId.value;
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
  target: targetDescription.value ? [targetDescription.value] : []
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

  // Add target description directly (without the target type name)
  const targetDesc = targetDescription.value.trim();
  if (targetDesc) segments.push(targetDesc);

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
    return generatedImages.value.length > 0;
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

function extractImageUrl(payload: any, imageId?: string): string | null {
  if (!payload || typeof payload !== 'object') return null;
  if (Array.isArray(payload.data) && payload.data[0]) {
    const item = payload.data[0];
    // If we have imageId, use API endpoint
    if (imageId) return `/api/v1/images/${imageId}/data/0`;
    if (item?.saved_url) return item.saved_url;
    if (item?.url) return item.url;
    if (item?.b64_json) return `data:image/png;base64,${item.b64_json}`;
  }
  if (imageId && payload.b64_json) return `/api/v1/images/${imageId}/data/0`;
  if (payload.saved_url) return payload.saved_url;
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

// Generation History functions
async function fetchHistory() {
  loadingHistory.value = true;
  try {
    const res = await fetch('/api/v1/images?limit=20', {
      credentials: 'include'
    });
    if (!res.ok) throw new Error('Failed to fetch history');
    const data = await res.json();
    const items: HistoryItem[] = data || [];

    // For items without image_url, try to fetch the full record to get the image
    const itemsWithMissingImages = items.filter(item => !item.image_url);
    if (itemsWithMissingImages.length > 0) {
      // Fetch details for items missing image_url (in parallel, max 5)
      const fetchPromises = itemsWithMissingImages.slice(0, 5).map(async (item) => {
        try {
          const detailRes = await fetch(`/api/v1/images/${item.id}`, {
            credentials: 'include'
          });
          if (detailRes.ok) {
            const detail = await detailRes.json();
            const imageUrl = extractImageUrl(detail.response, item.id);
            if (imageUrl) {
              item.image_url = imageUrl;
            }
          }
        } catch (e) {
          console.warn('Failed to fetch image detail:', e);
        }
      });
      await Promise.all(fetchPromises);
    }

    generationHistory.value = items;
  } catch (e) {
    console.error('Failed to load history:', e);
  } finally {
    loadingHistory.value = false;
  }
}

async function loadHistoryItem(item: HistoryItem) {
  // If we already have the image URL (API endpoint), use it directly
  if (item.image_url) {
    generatedImages.value = [item.image_url];
    currentStep.value = 4;
    return;
  }

  // Otherwise, fetch the full record to get the image from response
  try {
    const res = await fetch(`/api/v1/images/${item.id}`, {
      credentials: 'include'
    });
    if (!res.ok) throw new Error('Failed to fetch image detail');

    const detail = await res.json();
    const imageUrl = extractImageUrl(detail.response, item.id);

    if (imageUrl) {
      generatedImages.value = [imageUrl];
      // Update the cache
      item.image_url = imageUrl;
      currentStep.value = 4;
    } else {
      showToast('无法加载图片数据', 'error');
    }
  } catch (e) {
    showToast('加载图片失败', 'error');
  }
}

function truncateText(text: string, length: number): string {
  if (!text) return '';
  if (text.length <= length) return text;
  return text.substring(0, length) + '...';
}

function formatHistoryDate(dateStr: string): string {
  if (!dateStr) return '';
  const date = new Date(dateStr);
  return date.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' });
}

async function fetchTargetTypes() {
  loadingTargetTypes.value = true;
  try {
    const res = await fetch('/api/v1/target-types', {
      credentials: 'include'
    });

    if (!res.ok) {
      throw new Error('Failed to fetch target types');
    }

    const data = await res.json();
    targetTypes.value = data.target_types || [];
  } catch (e) {
    console.warn('Failed to load target types from API, using defaults');
    targetTypes.value = [...DEFAULT_TARGET_TYPES];
  } finally {
    loadingTargetTypes.value = false;
  }
}

async function loadSavedDescriptions(targetId: string) {
  if (!targetId) {
    savedDescriptions.value = [];
    return;
  }
  try {
    const res = await fetch(`/api/v1/target-descriptions?target_type_id=${encodeURIComponent(targetId)}`, {
      credentials: 'include'
    });

    if (!res.ok) {
      throw new Error('Failed to fetch saved descriptions');
    }

    const data = await res.json();
    savedDescriptions.value = data.descriptions || [];
  } catch (e) {
    console.warn('Failed to load saved descriptions:', e);
    savedDescriptions.value = [];
  }
}

function loadSavedDescription(saved: SavedTargetDescription) {
  targetDescription.value = saved.description;
  currentSavedDescriptionId.value = saved.id;
}

async function saveNewDescription() {
  const targetId = selectedTargetTypeId.value;
  const name = saveDescriptionName.value.trim();
  const desc = targetDescription.value.trim();

  if (!targetId || !name || !desc) {
    showToast('请填写名称和描述', 'error');
    return;
  }

  targetDescriptionSaving.value = true;
  try {
    const payload = {
      target_type_id: targetId,
      name: name,
      description: desc
    };

    const res = await fetch('/api/v1/target-descriptions', {
      method: 'POST',
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRF-Token': getCsrfToken()
      },
      body: JSON.stringify(payload)
    });

    if (!res.ok) {
      const errData = await res.json().catch(() => ({}));
      throw new Error(errData.detail || `HTTP ${res.status}`);
    }

    const newDesc: SavedTargetDescription = await res.json();
    savedDescriptions.value.unshift(newDesc);
    currentSavedDescriptionId.value = newDesc.id;
    showSaveDialog.value = false;
    saveDescriptionName.value = '';
    showToast('描述已保存', 'success');
  } catch (e: any) {
    showToast(e.message || '保存描述失败', 'error');
  } finally {
    targetDescriptionSaving.value = false;
  }
}

async function deleteSavedDescription(descriptionId: string) {
  if (!confirm('确定要删除这个保存的描述吗？')) return;

  try {
    const res = await fetch(`/api/v1/target-descriptions/${descriptionId}`, {
      method: 'DELETE',
      credentials: 'include',
      headers: {
        'X-CSRF-Token': getCsrfToken()
      }
    });

    if (!res.ok) {
      const errData = await res.json().catch(() => ({}));
      throw new Error(errData.detail || `HTTP ${res.status}`);
    }

    savedDescriptions.value = savedDescriptions.value.filter(d => d.id !== descriptionId);
    if (currentSavedDescriptionId.value === descriptionId) {
      currentSavedDescriptionId.value = null;
    }
    showToast('描述已删除', 'success');
  } catch (e: any) {
    showToast(e.message || '删除描述失败', 'error');
  }
}

function resetToDefaultTemplate() {
  const target = selectedTargetType.value;
  if (target) {
    targetDescription.value = target.default_template || '';
    currentSavedDescriptionId.value = null;
  }
}

async function selectTargetType(targetId: string) {
  const prev = selectedTargetTypeId.value;
  selectedTargetTypeId.value = targetId;

  // Auto-fill default template when selecting a new target type
  if (prev !== targetId) {
    currentSavedDescriptionId.value = null;
    const target = targetTypes.value.find(t => t.id === targetId);
    targetDescription.value = target?.default_template || '';
    await loadSavedDescriptions(targetId);
  }
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
  if (!product?.id) return;
  if (selectedProduct.value?.id === product.id) return;
  if (selectingProductId.value) return;

  selectingProductId.value = product.id;

  // Load full product details
  try {
    const res = await fetch(`/api/v1/products/${product.id}`, {
      credentials: 'include'
    });

    if (!res.ok) {
      throw new Error('Failed to load product details');
    }

    const detail = await res.json();
    selectedProduct.value = detail;

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
  } finally {
    selectingProductId.value = null;
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
  // Load from global config keys (set in portal page)
  apiConfig.apiKey = localStorage.getItem('global_api_key') || localStorage.getItem('video_api_key') || '';
  apiConfig.baseUrl = localStorage.getItem('global_base_url') || localStorage.getItem('video_base_url') || '';
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
  generatedImages.value = [];

  const count = modelConfig.generateCount;
  generationProgress.value = { current: 0, total: count };

  try {
    // Prepare base form data elements
    const baseHeaders: Record<string, string> = {
      'X-CSRF-Token': getCsrfToken()
    };
    const apiKey = normalizeApiKey(apiConfig.apiKey);
    if (apiKey) baseHeaders['X-API-Key'] = apiKey;
    const baseUrl = normalizeBaseUrl(apiConfig.baseUrl);
    if (baseUrl) baseHeaders['X-Base-Url'] = baseUrl;

    // Fetch reference images once
    const imageBlobs: { id: string; blob: Blob }[] = [];
    for (const imageId of selectedImages.value) {
      const img = productImages.value.find(i => i.id === imageId);
      if (img) {
        try {
          const imgRes = await fetch(img.image_url);
          const imgBlob = await imgRes.blob();
          imageBlobs.push({ id: imageId, blob: imgBlob });
        } catch (e) {
          console.warn('Failed to fetch reference image:', img.image_url);
        }
      }
    }

    // Create generation promise for a single image
    const generateOne = async (): Promise<string | null> => {
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

      // Add reference images
      for (const { id, blob } of imageBlobs) {
        formData.append('image', blob, `ref-${id}.jpg`);
      }

      const res = await fetch('/api/v1/images/edits', {
        method: 'POST',
        credentials: 'include',
        headers: baseHeaders,
        body: formData
      });

      if (!res.ok) {
        const errData = await res.json().catch(() => ({}));
        throw new Error(errData.detail || `HTTP ${res.status}`);
      }

      const data = await res.json();
      const imageId = data.id;  // Get the image ID from response
      const payload = data && typeof data === 'object' && data.response ? data.response : data;
      const imageUrl = extractImageUrl(payload, imageId) || extractImageUrl(data, imageId);

      generationProgress.value.current++;
      return imageUrl;
    };

    // Run generations concurrently
    const promises = Array.from({ length: count }, () => generateOne());
    const results = await Promise.allSettled(promises);

    const successfulImages: string[] = [];
    const errors: string[] = [];

    for (const result of results) {
      if (result.status === 'fulfilled' && result.value) {
        successfulImages.push(result.value);
      } else if (result.status === 'rejected') {
        errors.push(result.reason?.message || '生成失败');
      }
    }

    if (successfulImages.length > 0) {
      generatedImages.value = successfulImages;
      showToast(`成功生成 ${successfulImages.length} 张图片`, 'success');
      // Refresh history to show the new images
      fetchHistory();
    } else if (errors.length > 0) {
      throw new Error(errors[0]);
    } else {
      throw new Error('Invalid response format');
    }
  } catch (e: any) {
    errorMessage.value = e.message || '生成失败，请重试';
  } finally {
    generating.value = false;
    generationProgress.value = { current: 0, total: 0 };
  }
}

function downloadSingleImage(imageUrl: string, index: number) {
  if (!imageUrl) return;

  const link = document.createElement('a');
  link.href = imageUrl;
  link.download = `ecommerce-${Date.now()}-${index + 1}.png`;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}

async function downloadAllImages() {
  if (generatedImages.value.length === 0) return;

  for (let i = 0; i < generatedImages.value.length; i++) {
    downloadSingleImage(generatedImages.value[i], i);
    // Small delay between downloads to avoid browser issues
    if (i < generatedImages.value.length - 1) {
      await new Promise(resolve => setTimeout(resolve, 300));
    }
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
  fetchTargetTypes();
  fetchHistory();
  initializeTemplateGroups(true);
});
</script>
