# Change: Download and store media content for repository records

## Why
Remote media URLs can expire or become inaccessible. Storing only the link means repository history can lose its content. We need to persist the generated media bytes in the user database so storage history remains durable.

## What Changes
- Backend: When creating image/video repository records with HTTP/HTTPS media URLs, download the media and store encrypted bytes plus MIME type and size.
- Backend: Include a stable internal content_url in image/video API responses when stored media is available.
- Backend: Add authenticated endpoints to serve stored media bytes for images and videos.
- Backend: Enforce download size limits and update per-user storage usage to include stored media bytes.
- Database: Add columns to store media bytes, MIME type, size, and source URL for image/video records.
- Frontend: Prefer content_url when rendering stored images/videos in the storage/history UIs.

## Impact
- Affected specs: store-media
- Affected code:
  - app/models/database.py
  - app/models/schemas.py
  - app/api/v1/images.py
  - app/api/v1/videos.py
  - app/api/v1/video.py
  - app/db/init.py
  - frontend/src/legacy/storage-legacy.ts
  - frontend/src/legacy/image-legacy.ts
  - frontend/src/pages/image-generate/image-generate-page.vue
  - frontend/src/pages/ecommerce-image/ecommerce-image-page.vue
