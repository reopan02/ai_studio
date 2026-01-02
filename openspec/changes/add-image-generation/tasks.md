## 1. Backend API

- [x] 1.1 Create `POST /api/v1/images/generations` endpoint in `app/api/v1/images.py`
- [x] 1.2 Implement request validation (prompt required, n 1-10, size validation)
- [x] 1.3 Forward request to image generation provider via client
- [x] 1.4 Return OpenAI-compatible response format (created, data array with URLs)
- [x] 1.5 Store generation record in database
- [x] 1.6 Handle and return appropriate error responses

## 2. Frontend Setup

- [x] 2.1 Create `frontend/image-generate.html` entry file
- [x] 2.2 Create `frontend/src/pages/image-generate/main.ts` entry point
- [x] 2.3 Create `frontend/src/pages/image-generate/image-generate-page.vue` main component
- [x] 2.4 Update `frontend/vite.config.ts` to add `image-generate` MPA entry
- [x] 2.5 Verify frontend builds correctly with `npm run build`

## 3. Portal Integration

- [x] 3.1 Add "图像生成" card to `frontend/src/pages/portal/portal-page.vue`
- [x] 3.2 Add route in `app/main.py` to serve `/image-generate` page

## 4. API Configuration Panel

- [x] 4.1 Create API config section (collapsible)
- [x] 4.2 Add API Key input with visibility toggle
- [x] 4.3 Add Base URL input with visibility toggle
- [x] 4.4 Load/save config from shared localStorage keys
- [x] 4.5 Add Save and Reset buttons

## 5. Model Selection

- [x] 5.1 Create model dropdown with options matching Image Edit Studio
- [x] 5.2 Add model search/filter functionality
- [x] 5.3 Sync model selection with localStorage

## 6. Prompt Input

- [x] 6.1 Create prompt textarea with placeholder
- [x] 6.2 Add character counter (0/1000)
- [x] 6.3 Implement max length enforcement
- [x] 6.4 Add prompt history dropdown

## 7. Image Settings

- [x] 7.1 Create image count selector (1-10)
- [x] 7.2 Create image size selector (256x256, 512x512, 1024x1024)
- [x] 7.3 Set default values (n=1, size=1024x1024)

## 8. Generation Execution

- [x] 8.1 Create generate button with loading state
- [x] 8.2 Implement API call to `/api/v1/images/generations`
- [x] 8.3 Include CSRF token in request
- [x] 8.4 Pass custom API Key/Base URL headers if configured
- [x] 8.5 Handle generation response

## 9. Result Display

- [x] 9.1 Create result area with placeholder state
- [x] 9.2 Display single generated image with zoom controls
- [x] 9.3 Display multiple images in responsive grid
- [x] 9.4 Add download button for each image
- [x] 9.5 Add fullscreen/lightbox view
- [x] 9.6 Show loading spinner during generation

## 10. Generation History

- [x] 10.1 Create inline history section
- [x] 10.2 Display recent generations with thumbnails
- [x] 10.3 Load history from API on page load
- [x] 10.4 Add click to reuse prompt functionality
- [x] 10.5 Add collapse/expand toggle

## 11. Error Handling

- [x] 11.1 Display error modal for generation failures
- [x] 11.2 Show toast notifications for success/error
- [x] 11.3 Handle network errors gracefully
- [x] 11.4 Enable retry after error

## 12. Styling & Polish

- [x] 12.1 Apply consistent styling with Image Edit Studio
- [x] 12.2 Add responsive layout for mobile/tablet
- [x] 12.3 Add hover states and transitions
- [x] 12.4 Test end-to-end generation flow
- [x] 12.5 Test error scenarios
