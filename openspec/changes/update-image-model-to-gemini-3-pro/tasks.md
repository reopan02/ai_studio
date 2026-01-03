## 1. Backend Implementation

- [x] 1.1 Update `ImageEditsClient` to support Gemini 3 Pro parameters
  - Add `image_size` parameter support (`1K`, `2K`, `4K`)
  - Ensure proper handling of Gemini API response format
  - Validate `image_size` uses uppercase 'K' as required by Gemini API

- [x] 1.2 Update `/api/v1/images/edits` endpoint
  - Accept `image_size` parameter from form data
  - Pass `image_size` to `ImageEditsClient`
  - Document the new parameter

- [x] 1.3 Update `/api/v1/images/generations` endpoint
  - Update valid sizes to use Gemini format (`1K`, `2K`, `4K`) instead of pixel dimensions
  - Accept `image_size` parameter
  - Add backward compatibility for legacy size values (optional)

## 2. Frontend: E-commerce Image Generator

- [x] 2.1 Update model selection in `ecommerce-image-page.vue`
  - Change default model to `gemini-3-pro-image-preview`
  - Update model dropdown options:
    - `gemini-3-pro-image-preview` (default, for quality)
    - `gemini-2.5-flash-image` (for speed)
  - Remove deprecated `gpt-image-1.5` and `nano-banana-*` options

- [x] 2.2 Update image settings in `ecommerce-image-page.vue`
  - Update Image Size options to `1K`, `2K`, `4K`
  - Ensure aspect ratio options align with Gemini 3 Pro supported ratios

- [x] 2.3 Remove API config from sidebar (moved to portal page)

## 3. Frontend: General Image Generator

- [x] 3.1 Update model selection in `image-generate-page.vue`
  - Change default model to `gemini-3-pro-image-preview`
  - Update model dropdown options (same as e-commerce page)
  - Remove deprecated model options

- [x] 3.2 Update image size options in `image-generate-page.vue`
  - Replace pixel-based sizes (`1024x1024`, `512x512`, `256x256`) with Gemini format (`1K`, `2K`, `4K`)
  - Update form submission to use new format

- [x] 3.3 Remove API config from sidebar (moved to portal page)

## 4. Frontend: Image Processing (image-page.vue)

- [x] 4.1 Update model selection in `image-page.vue`
  - Change default model to `gemini-3-pro-image-preview`
  - Update model dropdown options

- [x] 4.2 Remove API config from sidebar (moved to portal page)

- [x] 4.3 Update `image-legacy.ts` to use global config keys

## 5. Global API Configuration

- [x] 5.1 Add global API config section to `portal-page.vue`
  - Collapsible configuration panel
  - API Key and Base URL inputs
  - Save/Reset functionality
  - Shows "已配置" / "未配置" status

- [x] 5.2 Implement global localStorage keys
  - `global_api_key` and `global_base_url` as primary keys
  - Backward compatibility with legacy keys (`video_api_key`, `video_base_url`, `apiKey`, `baseUrl`)

- [x] 5.3 Update all pages to load config from global keys
  - `ecommerce-image-page.vue`
  - `image-generate-page.vue`
  - `image-legacy.ts`

## 6. Build and Verification

- [x] 6.1 Rebuild frontend assets
  - Run `npm run build` in frontend directory
  - Verify built assets in `app/static/assets/`

- [ ] 6.2 Manual testing
  - Test e-commerce image generation with `gemini-3-pro-image-preview`
  - Test general image generation with different image sizes
  - Test image processing page with Gemini model
  - Verify global API config is applied to all pages
  - Verify error handling for invalid parameters

## Notes

- Gemini 3 Pro Image Preview requires uppercase 'K' for size values (`1K`, `2K`, `4K`)
- The API currently uses `/v1/images/edits` and `/v1/images/generations` endpoints which remain compatible
- Default aspect ratios supported by Gemini 3 Pro: 1:1, 16:9, 9:16, 4:3, 3:4, etc.
- Global API config is stored with keys: `global_api_key`, `global_base_url`
- Legacy keys are also synced for backward compatibility
