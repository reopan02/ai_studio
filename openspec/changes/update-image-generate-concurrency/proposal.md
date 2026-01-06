# Change: Update image generation to use concurrency for `n`

## Why
Some upstream image generation providers do not support the `n` parameter in `/v1/images/generations`, causing requests to fail or behave inconsistently. The UI already exposes a “生成数量 (n)” control, so the backend should generate multiple images without relying on an upstream `n` field.

## What Changes
- Treat `n` on `POST /api/v1/images/generations` as the number of concurrent single-image generation calls (bounded as today).
- Treat `n` on `POST /api/v1/images/edits` as the number of concurrent single-image edit calls (bounded as today).
- Do not include `n` in outbound provider requests (e.g., `/v1/images/generations`).
- Aggregate concurrent provider responses into one OpenAI-compatible response payload with a combined `data` array.
- Persist request/response payloads so stored provider requests reflect the actual outbound payloads (no provider `n`).

## Impact
- Affected capabilities: `image-generations`, `image-edits`
- Affected code: `app/api/v1/images.py`, `app/clients/image_edits_client.py`, `app/clients/gemini_image_client.py`
