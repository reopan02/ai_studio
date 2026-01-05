## 1. Schema and data model
- [ ] 1.1 Add media storage columns to UserImage/UserVideo (content_encrypted, content_mime_type, content_size_bytes, source_url)
- [ ] 1.2 Add runtime migration checks in app/db/init.py to add new columns when missing
- [ ] 1.3 Update Pydantic schemas to include content_url in summaries/details

## 2. Media download + storage
- [ ] 2.1 Implement a shared media download helper with timeouts, size limits, and MIME detection
- [ ] 2.2 Update image endpoints (edits, generations, create) to download and store media bytes
- [ ] 2.3 Update video endpoints (generate/sync, create) to download and store media bytes
- [ ] 2.4 Update storage quota accounting and delete handlers to include stored media bytes

## 3. Media delivery endpoints
- [ ] 3.1 Add authenticated endpoints to stream stored image and video bytes
- [ ] 3.2 Ensure content-type and content-disposition headers are set for browser playback/download

## 4. Frontend integration
- [ ] 4.1 Update storage UI to prefer content_url with fallback to existing URL fields
- [ ] 4.2 Update image generation/history UIs to prefer content_url

## 5. Validation
- [ ] 5.1 Manual verify: create image/video, confirm stored media loads from internal URLs
- [ ] 5.2 Manual verify: storage quota increments with stored media size
