# Design: Product Library AI Text Structuring + Manual Save

## Context

The repository already includes a Product Library:

- Backend CRUD under `/api/v1/products`
- Frontend Products page under `/products` (Vite MPA entry)

Today, creating a product is a single-step action that always runs AI recognition from the uploaded image. The requested experience is a two-step flow:

1) User provides image + optional unstructured text → AI pre-fills a structured form (preview only)
2) User reviews/edits → user clicks Save to create the product

Users must also be able to bypass AI completely and create a product via manual entry.

## Goals / Non-Goals

**Goals**
- Keep product image required for creation.
- Provide an AI “prefill” capability that does not create records.
- Allow manual creation without any AI calls.
- Keep changes backwards compatible and minimal.
- Improve Products page layout and add Portal entry for `/products`.

**Non-Goals**
- Add new product fields beyond the existing schema (no categories/brand/SKU in this change).
- Introduce async background jobs/queues for recognition.
- Implement server-side temporary image storage for preview (preview will not persist images).

## Decisions

### Decision 1: Two-step API design (Preview + Save)

**Choice**
- Add a preview endpoint `POST /api/v1/products/recognize` that accepts multipart `image` + optional `raw_text`.
- Preview returns structured fields (same schema as recognition) and auxiliary metadata, but performs **no** product creation and **no** image persistence.

**Rationale**
- Matches the desired UI: prefill first, user confirms Save.
- Avoids storing partial products when user cancels.
- Keeps implementation simple (no temporary storage needed).

### Decision 2: Manual save mode for create

**Choice**
- Extend `POST /api/v1/products` with an opt-in mode to skip recognition (manual save).

**Rationale**
- Enables manual entry without adding a parallel endpoint.
- Keeps existing “create-with-AI” behavior unchanged by default.

### Decision 3: LLM prompt uses both image and raw text

**Choice**
- When `raw_text` is provided, the recognition prompt includes it as additional context.
- If text conflicts with the image, prefer what can be visually confirmed; reduce confidence.

**Rationale**
- Improves extraction quality when users paste messy listing text.
- Keeps output constrained to the existing `ProductRecognitionResult` schema.

## API Sketch

### Preview recognition (new)

`POST /api/v1/products/recognize`

- Auth required (cookie/JWT as existing).
- Multipart:
  - `image` (required)
  - `raw_text` (optional string)
- Response (shape to be finalized in implementation):
  - structured fields: `name`, `dimensions`, `features`, `characteristics`, `confidence`
  - recognition metadata for UI diagnostics (optional)
- Does not create products and does not store images.

### Create product (extended)

`POST /api/v1/products`

- Multipart:
  - `image` (required)
  - structured fields (optional overrides)
  - `recognition_mode`:
    - `auto` (default): current behavior (run AI)
    - `manual`: skip AI and save user-provided fields
    - `prefill`: skip AI and persist the recognition payload returned by the preview endpoint (confidence + metadata)

## Frontend UX

- Products page adds an “unstructured text” input.
- “AI整理预填” triggers preview recognition and fills the structured fields in the form.
- “保存” creates the product:
  - `recognition_mode=prefill` if the user used AI prefill (persist preview confidence/metadata)
  - `recognition_mode=manual` if the user wants to bypass AI completely
- Portal adds a “产品库” card linking to `/products`.

## Risks / Trade-offs

- Preview requires uploading the image once for prefill and again for save (simple but duplicates upload).
- LLM output quality varies; keep confidence visible and allow easy manual correction.
