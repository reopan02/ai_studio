## Context
`POST /api/v1/images/generations` currently accepts `n` and forwards it to the upstream `/v1/images/generations` request for non-Gemini models. Some providers reject `n`, and Gemini generation currently does not use `n` at all (so the UI “生成数量” does not reliably map to output count).

`POST /api/v1/images/edits` currently always performs a single upstream call. It should support the same `n`-driven concurrency pattern for generating multiple edited variants.

## Goals / Non-Goals
- Goals
  - Generate exactly `n` images for a single request (bounded as today).
  - Treat `n` as concurrency for upstream calls; do not include `n` in outbound payloads.
  - Keep the backend response shape compatible with the existing frontend extraction logic (`response.data[*].url` or `response.data[*].b64_json`).
- Non-Goals
  - Change frontend request parameters or UI controls.
  - Introduce a background queue or new persistence model for one record per image.

## Design
### Request execution
- For `n=1`, perform a single upstream call as today (without adding `n` to the outbound JSON).
- For `n>1`, perform `n` upstream calls concurrently (each requesting one image by default) and aggregate results.

### Response aggregation
- Normalize each upstream response into an OpenAI-compatible `{ "data": [...] }` shape (handling `data`, `url`, and `b64_json` variants).
- Concatenate all `data` items into a single combined `data` array returned to the caller and stored on the `UserImage` record.

### Error handling
- If any upstream call fails (HTTP error or client exception), return `502` and do not return partial results.

## Validation
- Manual: use the `/image-generate` page, request multiple images, and confirm:
  - the UI renders `n` images
  - request storage shows outbound payloads without provider `n`
- Manual: submit `POST /api/v1/images/edits` with `n=2..4` and confirm:
  - the response contains `n` images in `response.data`
  - stored request metadata omits provider `n`
