## 1. Backend API: Recognition Preview

- [x] 1.1 Add `POST /api/v1/products/recognize` (multipart `image` + optional `raw_text`) that returns structured fields without creating a product
- [x] 1.2 Reuse existing image preprocessing + StructLLM schema validation for preview recognition
- [x] 1.3 Ensure cookie auth + CSRF works for the preview endpoint (unsafe method)

## 2. Backend API: Manual Save Mode

- [x] 2.1 Extend `POST /api/v1/products` with a `recognition_mode` option to skip AI (`manual`)
- [x] 2.2 When `manual`, do not call LLM; set `recognition_confidence=0.0` and `recognition_metadata=NULL`
- [x] 2.3 Preserve existing default behavior (`auto`) for backward compatibility
- [x] 2.4 Add `recognition_mode=prefill` to persist preview recognition payload (confidence + metadata) without a second LLM call

## 3. Frontend: AI Prefill + Save

- [x] 3.1 Add a "无结构化信息" textarea on Products page
- [x] 3.2 Add "AI整理预填" button that calls `POST /api/v1/products/recognize` and fills name/dimensions/features/characteristics
- [x] 3.3 Store the preview confidence/metadata client-side after "AI整理预填"
- [x] 3.4 Add a "保存产品" button that creates a product:
  - `recognition_mode=prefill` if AI prefill was used (persist preview confidence/metadata)
  - `recognition_mode=manual` if saving purely manual fields

## 4. Frontend: Portal Navigation + UI Polish

- [x] 4.1 Add a "产品库" card entry on the Portal page linking to `/products`
- [x] 4.2 Improve Products page layout/spacing to match Portal card style and ensure responsive behavior (desktop vs mobile)

## 5. Validation (Manual)

- [ ] 5.1 AI Prefill: image + raw text → prefilled fields appear; product not created until Save
- [ ] 5.2 Manual Save: fill fields + image → Save creates product with `confidence=0.0`
- [ ] 5.3 End-to-end: Portal → Products → prefill → edit → save → list/search → edit → delete
- [ ] 5.4 Verify CSRF headers for POST/PUT/DELETE continue to work
