# Change: Add E-Commerce Image Generator

## Why

The system has a functioning Product Library and an Image Edit Studio, but lacks a streamlined workflow specifically for generating e-commerce product images. Users currently need to manually compose prompts and cannot leverage pre-built templates optimized for product photography scenarios (main product images, detail shots, promotional posters). This change adds a dedicated "E-Commerce Image Generator" entry point that bridges Product Library selection with structured prompt templates, enabling rapid generation of professional product images.

## What Changes

- **Portal entry**: Add a new "电商图生成" card on the main portal page (`/`) linking to `/ecommerce-image`
- **Frontend page**: Create a new Vite MPA entry for E-Commerce Image Generator with Vue 3 + TypeScript
- **Product selector**: Provide a product picker that loads products from the Product Library, displaying product name, thumbnail, and basic info
- **Product info panel**: Auto-populate product information (name, dimensions, features, characteristics) from the selected product; allow user to edit/toggle which fields to include in the prompt
- **Multi-image reference**: Display all reference images associated with the selected product; allow user to select which images to use for generation
- **Prompt template system**: Provide preset prompt templates with modular sections:
  1. Scene selection (e.g., "白色背景", "自然光桌面", "户外场景")
  2. Shooting angle (e.g., "正面", "45度侧面", "俯视")
  3. Style/Lighting (optional, e.g., "柔和光影", "高对比度")
  4. Generation target (e.g., "主图", "详情页", "海报")
- **Template customization**: Allow users to freely edit, add, or remove template options; store custom templates in localStorage
- **Real-time prompt preview**: Concatenate selected template modules + product info into a final prompt; display live preview as user adjusts options
- **Generation**: Call existing image generation API (`POST /api/v1/images`) with composed prompt and selected reference images
- **Reuse & iteration**: After generation, allow user to reuse current settings or adjust parameters for another round

## Impact

- **Affected specs**:
  - New capability: `ecommerce-image-ui` (E-Commerce Image Generator frontend)
  - Related: `product-library-api` (read products for selection)
  - Related: existing image generation API (no changes, just consumption)

- **Affected code**:
  - `frontend/ecommerce-image.html` - New Vite entry HTML
  - `frontend/vite.config.ts` - Add MPA entry for ecommerce-image
  - `frontend/src/pages/ecommerce-image/` - New Vue 3 page components
  - `frontend/src/pages/portal/portal-page.vue` - Add portal card
  - `app/main.py` - Serve `/ecommerce-image` route
  - `app/static/` - Build output

- **Dependencies**:
  - Requires `add-product-library` (Product Library API)
  - Uses existing image generation endpoints
  - No new Python packages required
