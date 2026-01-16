# Toolbox Multiview Design

## Summary
Add a Toolbox entry in the portal AI generation section that links to a new /toolbox page. The toolbox page contains a multiview generation module that reads product names and images from the product library and calls the existing image edits endpoint to produce a single 2x2 white-background grid with four viewing angles.

## Goals
- Provide a dedicated toolbox page with a multiview generator.
- Use product library data as inputs (product name + selected reference images).
- Support configurable model, aspect ratio, resolution, and concurrency.
- Output single 2x2 grid images per result and persist them to user_images.

## Non-goals
- No backend image composition; output relies on model prompt adherence.
- No additional modules in the toolbox beyond multiview generation.
- No changes to product library schemas or APIs.

## UX / UI
- Portal: add a Toolbox card in the AI generation section (Chinese label: 工具箱).
- Toolbox page: left sidebar for model/settings and product selection, right panel for generation and results.
- Results: large preview + thumbnails, lightbox preview, download action.
- Prompt preview is read-only (fixed multiview template).

## Data Flow
1. Page loads global API config from localStorage.
2. Fetch product list from Supabase with search and pagination; load product images.
3. User selects product and multiple reference images.
4. Build multiview prompt using product name + fixed instructions.
5. Submit FormData to /api/v1/images/edits with selected images and config.
6. Parse response URLs; show results and persist to user_images.

## Prompt Strategy
The prompt instructs the model to return a single 2x2 grid on a pure white background with four angles (front, 45-degree side, back, top-down). Enforce consistent lighting, no props, no text, and uniform margins.

## Error Handling
- Block generation if product or reference images are missing.
- Confirm when concurrency is large.
- Show toast and error modal on failures.

## Persistence
Save each returned grid image to user_images with metadata:
- source: toolbox-multiview
- product_id
- selected_images
- aspect_ratio, image_size, index
- request/response payloads

## Testing
- Manual verification in the toolbox page (select product, generate, preview, download).
- Run python -m pytest for backend baseline.
- Run npm run typecheck and confirm no new errors beyond baseline.
