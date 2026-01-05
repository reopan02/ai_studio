## Context
Repository records currently store only remote media URLs. When remote links expire or require new auth, stored history loses its content. We need to persist the media bytes in the user database while keeping access controlled and quota-aware.

## Goals / Non-Goals
- Goals:
  - Download and store media bytes for new image/video records.
  - Encrypt stored media at rest.
  - Provide authenticated endpoints to serve stored media.
  - Include content_url in API responses when stored media exists.
  - Count stored media bytes toward user storage quota.
- Non-Goals:
  - Backfill existing records.
  - Deduplicate identical media.
  - Add CDN or background processing.

## Decisions
- Decision: Store downloaded media bytes in new encrypted BLOB columns for user_images and user_videos.
- Decision: Keep the original remote URL in a source_url column; expose content_url in API responses when stored media exists.
- Decision: Enforce a maximum download size and user quota checks; fail the save if the download exceeds limits or fails.

## Risks / Trade-offs
- Larger DB size and encryption cost for videos. Mitigation: size limits and clear errors.
- Longer request time due to downloads. Mitigation: timeouts and user feedback.
- Memory usage during encryption of large blobs. Mitigation: strict size limits.

## Migration Plan
- Add nullable columns with defaults to existing tables.
- No backfill of existing records.
- New endpoints use stored media if present; UI falls back to remote URL otherwise.

## Open Questions
- Should the system fall back to saving only the remote URL when download fails?
- What maximum media size should be allowed per download (config value and default)?
- Should content_url be returned in list endpoints, detail endpoints, or both?
