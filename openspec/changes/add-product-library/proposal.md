# Change: Add Product Library with AI Recognition

## Why

The system currently supports video and image generation APIs, but lacks the foundational product library module needed for the planned e-commerce image generation system. Module One: Product Library is the first critical step in building a complete AI-powered product image generation workflow. This module enables users to upload product images, leverage LLM-based structured recognition to extract product attributes (name, dimensions, features, characteristics), and store them in a library for subsequent main image, detail image, and product listing generation.

Reference documentation: `\\NAS\coding\Image generation.md` specifies this as priority order 1 ("优先实现产品库模块") because it serves as the foundation for all downstream generation tasks.

## What Changes

- **Database schema**: Add `products` table with UUID primary key, user_id foreign key, and fields for name, dimensions, features, characteristics, original_image_url, recognition_confidence, and JSON metadata
- **LLM integration**: Integrate StructLLM (reference: `\\NAS\coding\llm_api.py`) to call Gemini API with structured prompts that return validated JSON containing product attributes
- **API endpoints**: Add `/api/v1/products` REST endpoints for CRUD operations (create, list, get, update, delete) with user authentication
- **Image upload**: Frontend image compression (>5MB threshold) and backend storage handling with quota enforcement
- **AI recognition**: Structured prompt engineering to extract product name, dimensions, features, and characteristics from uploaded images
- **Human oversight**: Return confidence scores and allow manual correction of low-confidence or incomplete AI-extracted fields
- **Frontend integration**: Vue3 + TypeScript components for product upload, AI recognition preview, and manual editing

## Impact

- **Affected specs**:
  - New capability: `product-recognition` (AI-based product attribute extraction)
  - New capability: `product-library-api` (CRUD operations for product management)
  - Modified: `user-authentication` (extends user context to product ownership)
  - Modified: `storage-management` (product images count toward user quota)

- **Affected code**:
  - `app/models/database.py` - Add Product model
  - `app/models/schemas.py` - Add Pydantic schemas for product requests/responses
  - `app/api/v1/` - New `products.py` route handler
  - `app/clients/` - New LLM client for Gemini/StructLLM integration
  - `app/core/` - New product image storage handling
  - `app/static/` - New Vue3 product library page components
  - `app/db/` - Database initialization includes new Product table

- **Dependencies**:
  - New Python package: `structllm` (for constrained LLM response formatting)
  - Gemini API access (vision + structured output capabilities)
  - Existing: FastAPI, SQLAlchemy, PostgreSQL, user authentication, storage encryption
