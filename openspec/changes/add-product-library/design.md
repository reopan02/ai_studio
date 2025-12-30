# Design: Product Library with AI Recognition

## Context

This change introduces Module One from the e-commerce image generation system specification. The existing codebase is a FastAPI-based AI video/image generator proxy with user authentication, encrypted storage, and quota management. We need to add product library capabilities that leverage AI vision models to automatically extract structured product information from uploaded images.

**Reference architecture**: `\\NAS\coding\Image generation.md` defines a 4-module system where Product Library is the foundation.

**Reference implementation pattern**: `\\NAS\coding\llm_api.py` demonstrates StructLLM usage for constrained model responses.

**Constraints**:
- Must integrate with existing user authentication (JWT + sessions)
- Must respect storage quota enforcement (tracked in `storage_used_bytes`)
- Must follow encryption-at-rest pattern for sensitive data
- Must align with existing async/await architecture

**Stakeholders**:
- End users: Upload products, review AI recognition, manually correct errors
- System: Foundation for downstream main image, detail image, and listing generation modules

## Goals / Non-Goals

**Goals**:
- Enable product image upload with compression (>5MB threshold per spec)
- Automatically extract structured product attributes using LLM vision capabilities
- Store products with user ownership and quota enforcement
- Provide REST API for product CRUD operations
- Support human-in-the-loop correction for low-confidence AI results
- Maintain compatibility with existing authentication and storage patterns

**Non-Goals**:
- Modules 2-4 (main image, detail image, listing generation) - handled in separate changes
- Advanced product search/filtering - basic list/get sufficient for MVP
- Multi-image product variants - single representative image per product
- Real-time WebSocket updates - polling or standard HTTP requests only
- Product categories/taxonomy - flat structure initially

## Decisions

### Decision 1: LLM Integration Pattern

**Choice**: Use StructLLM library with Gemini API for structured product recognition.

**Rationale**:
- Reference code (`llm_api.py`) demonstrates working StructLLM + Pydantic pattern
- Gemini supports vision (image understanding) + structured outputs
- Pydantic validation ensures type-safe attribute extraction
- Existing codebase already uses Pydantic extensively (schemas.py)

**Alternatives considered**:
- OpenAI GPT-4V: Requires additional API integration; Gemini already in spec
- Custom vision model: Over-engineering for MVP; leverages existing LLM expertise
- Manual-only entry: Defeats purpose of AI-assisted workflow

**Implementation**:
- Create `app/clients/llm_client.py` with StructLLM initialization pattern from reference code
- Define `ProductRecognitionResult` Pydantic model with fields: `name`, `dimensions`, `features` (List[str]), `characteristics` (List[str]), `confidence` (float)
- Prompt template: "识别这张图片中的产品,返回产品名称、尺寸、功能特征和特点" with structured output constraints

### Decision 2: Database Schema Design

**Choice**: Single `products` table with JSON metadata field for extensibility.

**Rationale**:
- Aligns with existing pattern (see `UserVideo.request_encrypted`, `ApiRequestLog.query_params` using JSON columns)
- PostgreSQL JSON support allows flexible product attributes without schema migrations
- Core fields (name, dimensions) as columns for indexing; extended attributes in JSON

**Schema**:
```python
class Product(Base):
    __tablename__ = "products"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    name = Column(String(200), nullable=False)
    dimensions = Column(String(100), nullable=True)  # e.g., "350ml 保温杯"
    features = Column(JSON, nullable=True)  # ["24小时保温", "不锈钢内胆"]
    characteristics = Column(JSON, nullable=True)  # ["便携", "大容量"]

    original_image_url = Column(String(1000), nullable=False)
    recognition_confidence = Column(Float, nullable=True)  # 0.0-1.0
    recognition_metadata = Column(JSON, nullable=True)  # Full AI response for debugging

    image_size_bytes = Column(Integer, nullable=False, default=0)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
```

**Alternatives considered**:
- Separate tables for features/characteristics: Premature normalization; JSON simpler
- NoSQL document store: Inconsistent with existing PostgreSQL architecture
- Encrypted storage for product data: Products not PII; unnecessary overhead vs videos/images

### Decision 3: Image Storage Strategy

**Choice**: Store uploaded product images using existing file storage pattern, track size in quota.

**Rationale**:
- Spec requires "文件系统/OSS(图片文件)" storage layer
- Existing code has encryption/storage patterns in `app/core/`
- Product images less sensitive than generation request/response data (no encryption needed)

**Implementation**:
- Upload flow: Frontend compresses >5MB images → POST base64/multipart → Save to `static/uploads/products/{user_id}/{uuid}.jpg`
- Quota enforcement: Check `user.storage_used_bytes + image_size <= user.storage_quota_bytes` before save
- Update `user.storage_used_bytes` atomically on product creation
- Delete cleanup: Decrement quota on product deletion

**Alternatives considered**:
- External OSS (Alibaba Cloud OSS, AWS S3): Adds deployment complexity; local files sufficient for MVP
- Store in database as BLOB: Poor performance for large images; file system better

### Decision 4: API Design

**Choice**: RESTful CRUD endpoints at `/api/v1/products` with pagination and filtering.

**Endpoints**:
- `POST /api/v1/products` - Create product with image upload + AI recognition
- `GET /api/v1/products` - List user's products (paginated, filterable by name)
- `GET /api/v1/products/{id}` - Get single product detail
- `PUT /api/v1/products/{id}` - Update product (manual correction)
- `DELETE /api/v1/products/{id}` - Delete product + image + reclaim quota

**Rationale**:
- Consistent with existing patterns (`/api/v1/videos`, `/api/v1/images`, `/api/v1/storage`)
- Leverage existing dependency injection (`get_current_user` from `app/api/deps.py`)
- Standard pagination pattern (offset/limit query params)

**Alternatives considered**:
- GraphQL: Unnecessary complexity for simple CRUD
- Nested under `/api/v1/users/{id}/products`: Adds routing complexity; user context from JWT sufficient

### Decision 5: Frontend Architecture

**Choice**: Single-page Vue3 + TypeScript component at `static/product-library.html` with composables.

**Rationale**:
- Existing frontend uses Vue3 + TS (migrated per git history: "feat: migrate frontend to Vue 3 + TypeScript")
- MPA (multi-page app) architecture per `project.md` tech stack
- Composables pattern for reusable logic (upload, API calls, form validation)

**Structure**:
```
app/static/
├── product-library.html          # Main page
├── js/product-library/
│   ├── main.ts                   # App entry
│   ├── components/
│   │   ├── ProductUpload.vue     # Image upload + compression
│   │   ├── RecognitionPreview.vue # Show AI results + edit
│   │   └── ProductList.vue       # List products with search
│   └── composables/
│       ├── useProductApi.ts      # API client
│       └── useImageCompression.ts # >5MB compression logic
```

**Alternatives considered**:
- Separate SPA build: Over-engineering; static multi-page aligns with existing architecture
- jQuery/vanilla JS: Inconsistent with Vue3 migration; harder to maintain

## Risks / Trade-offs

### Risk 1: LLM API rate limits and costs

**Mitigation**:
- Implement exponential backoff retry (using existing `tenacity` library)
- Add request queuing if needed (defer to Module 2 implementation with Celery)
- Cache recognition results in `recognition_metadata` JSON to avoid re-processing
- Provide manual entry fallback if AI recognition fails

### Risk 2: Image compression quality loss

**Mitigation**:
- Configurable compression threshold (default 5MB per spec)
- Store original image dimensions in metadata for reference
- Quality parameter tuning (JPEG quality=85 as default)
- Allow users to download original if needed

### Risk 3: Storage quota exhaustion

**Mitigation**:
- Enforce quota checks before upload (fail fast with clear error)
- Admin endpoint to adjust quotas (already exists: `UserQuotaUpdate` schema)
- Cleanup tool for orphaned images (future improvement)

### Risk 4: Incomplete or incorrect AI recognition

**Mitigation**:
- Return `confidence` score with recognition results
- Frontend highlights low-confidence fields (<0.7 threshold) for manual review
- Allow full manual override of all extracted fields
- Store original AI response in `recognition_metadata` for debugging

## Migration Plan

**Phase 1: Database Schema** (non-breaking)
1. Add `products` table via SQLAlchemy model definition
2. Run database migration: `Base.metadata.create_all()` on startup (existing pattern)
3. No impact on existing users/videos/images tables

**Phase 2: Backend API** (new endpoints)
1. Implement product CRUD endpoints
2. Add LLM client integration
3. Test with manual API calls (Postman/curl)
4. No impact on existing video/image generation APIs

**Phase 3: Frontend** (new page)
1. Create product library page
2. Link from portal navigation
3. Optional feature - existing users unaffected

**Rollback**:
- Remove product page link from navigation
- Drop `products` table if needed (no foreign key dependencies from other tables)
- Remove LLM client dependency

## Open Questions

1. **Gemini API endpoint and authentication**: Need to confirm base URL and API key configuration. Assumption: Use same `API_BASE_URL` and `API_KEY` from `.env` as existing image generation?

2. **Image format restrictions**: Should we restrict to JPEG/PNG only, or support WebP/HEIC? Spec doesn't specify. Proposal: Start with JPEG/PNG, add others if needed.

3. **Confidence threshold UX**: What visual indicator for low-confidence fields? Proposal: Yellow highlight + warning icon for <0.7, red for <0.5.

4. **Bulk upload**: Spec shows single-image workflow. Should we support batch upload (multiple products at once)? Proposal: Defer to future enhancement; single upload simpler for MVP.

5. **Product search**: Basic list endpoint sufficient, or should we add full-text search on name/features? Proposal: Simple `ILIKE` filter on name field initially, upgrade to PostgreSQL full-text search if needed.
