# Change: Add Image Generation (Text-to-Image) Feature

## Why

Users need a dedicated text-to-image generation feature that allows creating images purely from text prompts, without requiring reference images. The current "图像处理" (Image Edit Studio) requires reference images for editing, but many use cases only need text-to-image capability.

The new feature will:
- Provide a simpler workflow for pure text-to-image generation
- Use the OpenAI-compatible `/v1/images/generations` API format
- Share model/API configuration with the existing Image Edit Studio

## What Changes

### Backend
- Add new endpoint `POST /api/v1/images/generations` following OpenAI DALL-E format
- Parameters: prompt (required), n (number of images, 1-10), size (256x256, 512x512, 1024x1024)
- Response: Array of image URLs

### Frontend
- Add new "图像生成" portal card on main page
- Create `/image-generate` page with:
  - Prompt input with character counter
  - Model selection (synced with Image Edit Studio)
  - Number of images selector (1-10)
  - API Key/Base URL configuration (shared with Image Edit Studio)
  - Generation result display with download
  - Generation history

### Shared Configuration
- API Key, Base URL stored in localStorage with same keys as Image Edit Studio
- Model options consistent with Image Edit Studio

## Impact

- Affected specs: New `image-generation-ui` capability
- Affected code:
  - `app/api/v1/images.py` - Add generations endpoint
  - `app/main.py` - Add route for new page
  - `frontend/src/pages/portal/portal-page.vue` - Add portal card
  - New frontend files for image generation page
  - `frontend/vite.config.ts` - Add MPA entry
- No breaking changes to existing functionality
