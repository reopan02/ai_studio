# Implementation Tasks

## 1. Authentication & Navigation
- [x] 1.1 Update `app/main.py` to require authentication for `/image` route
- [x] 1.2 Add "返回主页面" button in image editor header linking to `/`
- [x] 1.3 Add redirect to `/login` if user is not authenticated

## 2. Backend Integration (Minimal Changes)
- [x] 2.1 Verify `POST /api/v1/images` endpoint accepts required fields from image editor
- [x] 2.2 Verify `GET /api/v1/images` endpoint returns data in expected format
- [x] 2.3 Verify `DELETE /api/v1/images/{id}` endpoint works correctly

## 3. Frontend - Replace Drawing History with Database Storage
- [x] 3.1 Remove localStorage-based Drawing History code
- [x] 3.2 Rename "Drawing History" section to "生成存储库" (Generation Repository)
- [x] 3.3 Add API client functions for authentication check (GET /api/v1/auth/me)
- [x] 3.4 Implement `saveImageToRepository()` function using `POST /api/v1/images`
- [x] 3.5 Implement `loadImagesFromRepository()` function using `GET /api/v1/images`
- [x] 3.6 Implement `deleteImageFromRepository(id)` function using `DELETE /api/v1/images/{id}`
- [x] 3.7 Update UI to display images from database (with thumbnails, titles, prompts)
- [x] 3.8 Add auto-refresh after successful image generation (edits endpoint already saves)
- [x] 3.9 Add delete functionality with confirmation dialog
- [x] 3.10 Handle CSRF token for API requests
- [x] 3.11 Handle storage quota exceeded errors (413 status)
- [x] 3.12 Show loading states during API calls

## 4. UI/UX Enhancements
- [x] 4.1 Update repository grid to display images from API
- [x] 4.2 Show image metadata (model, prompt, created_at)
- [x] 4.3 Show localized timestamps (Chinese format)
- [x] 4.4 Add empty state message when no images exist ("暂无生成记录")
- [x] 4.5 Add success/error toast notifications for save/delete operations

## 5. Testing & Validation
- [ ] 5.1 Test image generation and automatic save to database
- [ ] 5.2 Test loading images from database on page load
- [ ] 5.3 Test delete functionality
- [ ] 5.4 Test authentication redirect flow
- [ ] 5.5 Test storage quota exceeded scenario
- [ ] 5.6 Test CSRF protection
- [ ] 5.7 Verify images appear in `/storage` page
- [ ] 5.8 Validate OpenSpec with `openspec validate integrate-image-editor-storage --strict`
