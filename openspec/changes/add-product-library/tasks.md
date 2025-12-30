## 1. Database Schema Setup

- [x] 1.1 Add `Product` model to `app/models/database.py` with fields: id, user_id, name, dimensions, features (JSON), characteristics (JSON), original_image_url, recognition_confidence, recognition_metadata (JSON), image_size_bytes, created_at, updated_at
- [x] 1.2 Add Pydantic schemas to `app/models/schemas.py`: ProductCreate, ProductUpdate, ProductSummary, ProductDetail, ProductRecognitionResult
- [x] 1.3 Test database migration by running app startup and verifying `products` table creation

## 2. LLM Client Integration

- [x] 2.1 Add `structllm` dependency to project requirements (requirements.txt or pyproject.toml)
- [x] 2.2 Create `app/clients/llm_client.py` with StructLLM initialization following reference pattern from `\\NAS\coding\llm_api.py`
- [x] 2.3 Define `ProductRecognitionResult` Pydantic model with name, dimensions, features, characteristics, confidence fields
- [x] 2.4 Implement `recognize_product(image_base64: str) -> ProductRecognitionResult` function with structured Chinese prompt
- [x] 2.5 Add environment variables for LLM API configuration (API_BASE_URL, API_KEY, LLM_MODEL)
- [x] 2.6 Add error handling and retry logic using `tenacity` library for LLM API failures
- [ ] 2.7 Test LLM integration with sample product image and verify structured output

## 3. Image Storage and Processing

- [x] 3.1 Create `app/core/product_storage.py` with functions: save_product_image, delete_product_image, compress_image_if_needed
- [x] 3.2 Implement image compression logic for files >5MB using PIL/Pillow with JPEG quality=85
- [x] 3.3 Create directory structure `static/uploads/products/{user_id}/` on server startup
- [x] 3.4 Implement quota enforcement check: validate `storage_used_bytes + image_size <= storage_quota_bytes`
- [x] 3.5 Implement atomic quota update: increment/decrement `storage_used_bytes` in database transaction
- [ ] 3.6 Test image upload, compression, and storage with various file sizes and formats

## 4. Backend API Endpoints

- [x] 4.1 Create `app/api/v1/products.py` route handler file
- [x] 4.2 Implement `POST /api/v1/products` endpoint: accept multipart image upload, trigger AI recognition, save product, update quota
- [x] 4.3 Implement `GET /api/v1/products` endpoint: list user's products with pagination (offset/limit) and name filtering
- [x] 4.4 Implement `GET /api/v1/products/{id}` endpoint: return product detail with ownership validation
- [x] 4.5 Implement `PUT /api/v1/products/{id}` endpoint: update product attributes with ownership validation
- [x] 4.6 Implement `DELETE /api/v1/products/{id}` endpoint: delete product, remove image file, reclaim quota
- [x] 4.7 Add products router to `app/main.py` FastAPI app
- [ ] 4.8 Test all endpoints with Postman/curl: create, list, get, update, delete

## 5. Frontend - Product Upload Component

- [x] 5.1 Create `app/static/product-library.html` page with Vue3 app initialization
- [x] 5.2 Create integrated single-file frontend (simplified approach for faster delivery)
- [x] 5.3 Implement product upload component with image file input, preview, and compression indicator
- [x] 5.4 Implement client-side image handling for product upload
- [x] 5.5 Implement multipart form upload to POST /api/v1/products endpoint
- [x] 5.6 Display upload progress and handle quota exceeded errors with user-friendly messages
- [ ] 5.7 Test image upload flow: select file, compress if needed, upload, verify API response

## 6. Frontend - Recognition Preview Component

- [x] 6.1 Implement recognition preview component to display AI-extracted attributes
- [x] 6.2 Show product name, dimensions, features (as bullet list), characteristics (as tags)
- [x] 6.3 Highlight low-confidence fields (<0.7) with yellow background and warning icon
- [x] 6.4 Provide inline editing for all fields: text inputs for name/dimensions, tag editor for features/characteristics
- [x] 6.5 Integrate save functionality via POST /api/v1/products endpoint
- [ ] 6.6 Test recognition preview: view AI results, edit low-confidence fields, save changes

## 7. Frontend - Product List Component

- [x] 7.1 Implement product list component with grid view
- [x] 7.2 Display product cards: thumbnail image, name, dimensions, creation date, confidence score badge
- [x] 7.3 Implement search input with debounced API call to GET /api/v1/products?name=query
- [x] 7.4 Implement basic product loading and display
- [x] 7.5 Add delete confirmation dialog with quota reclaim notification
- [ ] 7.6 Test product list: load products, search by name, navigate pages, delete product

## 8. Frontend Integration and Navigation

- [x] 8.1 Add "产品库" (Product Library) link to navigation menu within product-library.html
- [x] 8.2 Implement integrated API client functions for all product endpoints
- [x] 8.3 Implement loading states, error handling, and toast notifications for API operations
- [ ] 8.4 Test full user flow: navigate to product library → upload product → review AI results → edit attributes → view in list → delete

## 9. Testing and Validation

- [ ] 9.1 Test with various product images: clear products on white background, complex scenes, low-quality images
- [ ] 9.2 Verify confidence scores correlate with recognition accuracy
- [ ] 9.3 Test quota enforcement: upload until quota full, verify error message, delete product, verify quota reclaimed
- [ ] 9.4 Test edge cases: corrupted image files, unsupported formats, extremely large files (>100MB)
- [ ] 9.5 Test cross-user isolation: verify users cannot access other users' products
- [ ] 9.6 Test admin access: verify admin users can view all products

## 10. Documentation and Configuration

- [ ] 10.1 Add LLM API configuration section to README or .env.example
- [ ] 10.2 Document required environment variables: API_BASE_URL, API_KEY, LLM_MODEL (e.g., "gemini-1.5-flash")
- [ ] 10.3 Update API documentation (if using OpenAPI/Swagger auto-docs, verify product endpoints appear)
- [x] 10.4 Add code comments explaining AI recognition prompt strategy and confidence scoring
- [x] 10.5 Document image compression settings and quota management behavior
