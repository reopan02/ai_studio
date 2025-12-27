# Change: Integrate Image Editor with Database Storage

## Why
Currently, the Image Editor (`/image`) uses "Drawing History" which appears to store generated images locally (likely in browser localStorage). This means:
- Generated images are not persisted to the database
- Users cannot access their image generation history across devices
- No integration with the existing storage quota and management system
- Inconsistent user experience compared to video generation (which saves to database)

## What Changes
- **REPLACE**: Local "Drawing History" → Database-backed "生成存储库" (Generation Repository)
- **NEW**: Integrate with existing `POST /api/v1/images` endpoint to save generated images
- **NEW**: Integrate with existing `GET /api/v1/images` endpoint to load image history
- **NEW**: Add "返回主页面" (Back to Home) button in image editor header
- **ENHANCED**: Display saved images from database in the repository section
- **ENHANCED**: Support CRUD operations (view, delete) for saved images

**Breaking Changes**:
- Users will lose any locally stored Drawing History (migration not feasible as local data has no user association)
- This is acceptable as Drawing History is a temporary preview feature

## Impact
- **Affected specs**: `specs/image-generation-storage/spec.md` (new capability)
- **Affected code**:
  - `images_editing/index.html` - Update UI, replace localStorage logic with API calls
  - `app/main.py` - Ensure `/image` route requires authentication
- **Database changes**: None (uses existing `user_images` table)
- **API changes**: None (uses existing endpoints)
- **User experience**: Image editor now saves to database, accessible from `/storage` page
