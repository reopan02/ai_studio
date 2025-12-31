# Change: Add Product Library Text Structuring + Manual Save

## Why

The Product Library currently creates products via `POST /api/v1/products` which always attempts AI recognition from the uploaded image. This makes it hard to:

- Let users paste unstructured product info (e.g. copy from a listing) and use the LLM to prefill structured fields before saving.
- Let users create products by manually filling fields and saving immediately, without triggering AI processing.

In addition, the Portal page (`GET /`) does not provide an entry point to the Product Library, and the Product Library UI needs light visual polish to match the Portal’s card-based design.

## What Changes

- **AI structuring (prefill) flow**: Add an API to turn an image + unstructured text into structured product fields (name/dimensions/features/characteristics) without creating a product yet; the UI uses this to prefill the edit form and the user clicks Save to persist.
- **Manual save flow**: Add a way to create a product from user-entered fields without any AI processing.
- **UI + navigation**: Update the Product Library page to support “AI Prefill” and “Save” as separate steps, improve layout/spacing, and add a “产品库” entry on the Portal page linking to `/products`.

## Impact

- **Backend**
  - Adds `POST /api/v1/products/recognize` (preview structuring; no DB write).
  - Extends `POST /api/v1/products` to support a “manual” save mode that skips AI.
- **Frontend**
  - Products page: new “unstructured text” input + “AI整理预填” button and a separate “保存” button.
  - Portal page: add “产品库” card entry to `/products`.
- **Compatibility**
  - Existing Product Library APIs remain available; new behavior is additive/opt-in.

## Assumptions

- Product image remains **required** for creating a product.
- Structured output targets existing fields only: `name`, `dimensions`, `features`, `characteristics`.

