# Change: Update image generation model to Gemini 3 Pro Image Preview

## Why

The project currently uses `gpt-image-1.5` and `nano-banana-*` series models for image generation. The user requests migrating all drawing models to `gemini-3-pro-image-preview`, which is Google's state-of-the-art image generation model optimized for professional asset production, featuring advanced reasoning, multi-turn creation, 4K resolution support, and up to 14 reference images.

## What Changes

### Backend Changes
- **BREAKING**: Default image generation model changes from `gpt-image-1.5` to `gemini-3-pro-image-preview`
- Add new parameter `image_size` support for Gemini 3 Pro (values: `1K`, `2K`, `4K`)
- Maintain backward compatibility with existing API endpoints (`/v1/images/edits`, `/v1/images/generations`)
- Update `ImageEditsClient` to support Gemini-specific parameters

### Frontend Changes
- Update model selection dropdowns to use `gemini-3-pro-image-preview` as default
- Replace old model options with:
  - `gemini-3-pro-image-preview` (default, recommended for quality)
  - `gemini-2.5-flash-image` (faster, for speed-sensitive use cases)
- Update Image Size selector to match Gemini's `1K`/`2K`/`4K` format
- Update aspect ratio options to align with Gemini 3 Pro supported ratios

### Affected Pages
1. `frontend/src/pages/ecommerce-image/ecommerce-image-page.vue` - E-commerce image generator
2. `frontend/src/pages/image-generate/image-generate-page.vue` - General image generator

## Impact

- Affected specs: None (no specs exist yet)
- Affected code:
  - `app/api/v1/images.py` - Backend API routes
  - `app/clients/image_edits_client.py` - HTTP client for image generation
  - `frontend/src/pages/ecommerce-image/ecommerce-image-page.vue`
  - `frontend/src/pages/image-generate/image-generate-page.vue`
- User impact: Improved image quality with Gemini 3 Pro; existing prompts should continue to work
