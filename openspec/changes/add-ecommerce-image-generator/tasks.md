## 1. Frontend Setup

- [x] 1.1 Create `frontend/ecommerce-image.html` entry file
- [x] 1.2 Create `frontend/src/pages/ecommerce-image/main.ts` entry point
- [x] 1.3 Create `frontend/src/pages/ecommerce-image/ecommerce-image-page.vue` main component
- [x] 1.4 Update `frontend/vite.config.ts` to add `ecommerce-image` MPA entry
- [x] 1.5 Verify frontend builds correctly with `npm run build`

## 2. Portal Integration

- [x] 2.1 Add "电商图生成" card to `frontend/src/pages/portal/portal-page.vue`
- [x] 2.2 Add route in `app/main.py` to serve `/ecommerce-image` page

## 3. Product Selector Component

- [x] 3.1 Create product selector component with search/filter UI
- [x] 3.2 Implement product list fetching via `GET /api/v1/products`
- [x] 3.3 Implement pagination support for product list
- [x] 3.4 Display product thumbnails and names in grid/list view
- [x] 3.5 Implement product selection with detail loading

## 4. Product Info Panel

- [x] 4.1 Create product info panel component
- [x] 4.2 Auto-populate fields (name, dimensions, features, characteristics) on product selection
- [x] 4.3 Add toggle checkboxes for each field to include/exclude from prompt
- [x] 4.4 Add inline editing capability for field values
- [x] 4.5 Wire field changes to prompt preview update

## 5. Reference Image Selector

- [x] 5.1 Create reference image grid component
- [x] 5.2 Display all images from selected product
- [x] 5.3 Implement image selection/deselection with visual feedback
- [x] 5.4 Track selected images for generation API call
- [x] 5.5 Validate at least one image is selected before generation

## 6. Prompt Template System

- [x] 6.1 Create template module component (reusable for each category)
- [x] 6.2 Define preset options for Scene (场景选择)
- [x] 6.3 Define preset options for Angle (拍摄角度)
- [x] 6.4 Define preset options for Style/Lighting (风格/光影)
- [x] 6.5 Define preset options for Target (生成目标)
- [x] 6.6 Implement multi-select within modules
- [x] 6.7 Implement option editing (inline text edit)
- [x] 6.8 Implement add custom option
- [x] 6.9 Implement delete option
- [x] 6.10 Implement localStorage persistence for custom templates
- [x] 6.11 Implement "Reset to defaults" action

## 7. Prompt Preview

- [x] 7.1 Create prompt preview component
- [x] 7.2 Implement real-time prompt concatenation from product info + template selections
- [x] 7.3 Format prompt according to spec: "[产品名称] [产品特征], [场景描述], [拍摄角度], [风格/光影], [生成目标风格要求]"
- [x] 7.4 Add copy-to-clipboard button with toast notification

## 8. Generation Integration

- [x] 8.1 Create API config section (sync with Image Edit Studio: API Key, Base URL)
- [x] 8.2 Add model selection dropdown (gpt-image-1.5, nano-banana variants)
- [x] 8.3 Add aspect ratio selector
- [x] 8.4 Add image size selector
- [x] 8.5 Implement generate button with loading state
- [x] 8.6 Call `POST /api/v1/images` with composed prompt and selected images
- [x] 8.7 Display generation result in preview area
- [x] 8.8 Add download button for generated image
- [x] 8.9 Handle and display generation errors

## 9. Iteration Features

- [x] 9.1 Implement "Generate Again" button to reuse current settings
- [x] 9.2 Preserve previous result until new generation completes
- [x] 9.3 Allow parameter adjustment between generations

## 10. Polish & Testing

- [x] 10.1 Apply consistent styling with Image Edit Studio
- [x] 10.2 Add responsive layout for different screen sizes
- [x] 10.3 Test product selection flow end-to-end
- [x] 10.4 Test template customization persistence
- [x] 10.5 Test generation with various prompt combinations
- [x] 10.6 Test error handling scenarios
