## Context

This change migrates the image generation backend from the current `gpt-image-1.5` / `nano-banana-*` models to Google's `gemini-3-pro-image-preview`. The backend proxies requests to an external API at `API_BASE_URL` (default: `https://api.gpt-best.com`) using OpenAI-compatible endpoints.

### Current Architecture
```
Frontend (Vue.js) → Backend (FastAPI) → External API (API_BASE_URL/v1/images/...)
                      ↓
                 ImageEditsClient
```

The `ImageEditsClient` currently supports:
- `model`: Model name string
- `prompt`: Text prompt
- `response_format`: `url` or `b64_json`
- `aspect_ratio`: Ratio string like `16:9`
- `image_size`: Size string (currently used but not validated)

### Gemini 3 Pro Image Preview Specifics

Based on official documentation:
- **Model ID**: `gemini-3-pro-image-preview`
- **Image Size**: `1K` (default), `2K`, `4K` - **Must use uppercase 'K'**
- **Aspect Ratios**: 1:1, 16:9, 9:16, 4:3, 3:4, 3:2, 2:3, 4:5, 5:4
- **Features**:
  - Advanced reasoning ("Thinking" process)
  - Up to 14 reference images (5 human faces for consistency)
  - Google Search grounding
  - 4K resolution output

## Goals / Non-Goals

### Goals
- Replace default model with `gemini-3-pro-image-preview`
- Update frontend dropdowns to reflect new model options
- Ensure `image_size` parameter uses Gemini's `1K`/`2K`/`4K` format
- Maintain API compatibility for existing integrations

### Non-Goals
- Implementing Gemini-specific features like Google Search grounding
- Adding character consistency (multi-face) support
- Implementing thought signature handling for multi-turn conversations
- Breaking changes to API response format

## Decisions

### Decision 1: Keep External API Proxy Pattern
**What**: Continue using `ImageEditsClient` to proxy requests to external API
**Why**: The external API already supports Gemini models; no need to integrate Gemini SDK directly

### Decision 2: Remove Legacy Models from Frontend Only
**What**: Remove old model options from UI but don't block them in backend
**Why**: Allows power users to still use old models via custom API calls while guiding most users to Gemini

### Decision 3: Use Gemini Size Format for All Models
**What**: Standardize on `1K`/`2K`/`4K` size format
**Why**: Simpler UI, and the external API can handle format translation if needed for other models

**Alternatives considered**:
- Add model-specific size dropdowns → More complex, not necessary
- Keep both formats → Confusing for users

## Risks / Trade-offs

| Risk | Mitigation |
|------|------------|
| External API may not support Gemini 3 Pro yet | Test before deployment; keep one legacy option temporarily |
| Size format change may break saved presets | Frontend uses localStorage; minimal impact, users can re-save |
| Gemini 3 Pro is slower due to "Thinking" | Offer `gemini-2.5-flash-image` as faster alternative |

## Migration Plan

1. Deploy backend changes (backward compatible)
2. Rebuild and deploy frontend with new model options
3. Monitor for errors in image generation
4. Remove legacy model options from frontend after 1 week if no issues

### Rollback
- Revert frontend to previous build
- Backend remains compatible with old model names

## Open Questions

- [ ] Confirm external API (`api.gpt-best.com`) supports `gemini-3-pro-image-preview`
- [ ] Verify if aspect ratio options need adjustment for Gemini 3 Pro
