# Product Library Configuration

## Overview

The Product Library module enables AI-powered product attribute extraction from uploaded images using LLM vision capabilities.

## Environment Variables

Add the following environment variables to your `.env` file:

```env
# LLM API Configuration (for product recognition)
LLM_API_KEY=your_llm_api_key
LLM_API_BASE_URL=https://api.gpt-best.com
LLM_MODEL=openai/gpt-4o-mini

# Database Configuration (if not already set)
DATABASE_URL=postgresql+asyncpg://user:password@localhost/dbname

# Storage Configuration (if not already set)
STORAGE_MASTER_KEY=your_32_byte_base64_key
JWT_SECRET_KEY=your_jwt_secret_key
```

## LLM API Configuration

The product library uses the LLM API endpoint configured via `LLM_API_*`. The system supports:

- **StructLLM**: Constrains LLM responses to predefined Pydantic schemas
- **Gemini API**: Provides vision capabilities for image understanding
- **Automatic retry**: Uses exponential backoff (3 attempts) on API failures

### API Models

Recommended models for product recognition:
- `openai/gpt-4o-mini` - Fast and cost-effective
- `openai/gpt-4-vision-preview` - Higher accuracy
- `gemini-1.5-flash` - Google's vision model

## Image Processing

### Compression Settings

- **Threshold**: Images > 5MB are automatically compressed
- **Quality**: JPEG quality=85 (configurable in code)
- **Format**: PNG/RGBA images converted to JPEG for API transmission
- **Storage**: Original full-resolution images stored in file system

### Storage Paths

Product images are stored at:
```
app/static/uploads/products/{user_id}/{product_id}.{ext}
```

Directory structure is created automatically on first upload.

## Storage Quota Management

- Product images count toward user storage quota
- Quota check enforced before upload (fail fast)
- Quota automatically reclaimed on product deletion
- Default quota: 1 GiB per user (configurable in admin panel)

## AI Recognition Behavior

### Confidence Scoring

- **High (>= 0.7)**: Green badge, high-quality recognition
- **Medium (0.5-0.7)**: Yellow badge, manual review recommended
- **Low (< 0.5)**: Red badge, manual correction required
- **Manual (0.0)**: Manually entered products

### Fallback Handling

If AI recognition fails:
1. System logs error in `recognition_metadata`
2. User can manually enter all fields
3. Product saved with confidence=0.0
4. No blocking - user workflow continues

### Recognition Metadata

Full AI response stored in JSON for debugging:
```json
{
  "recognized_at": "2025-01-01T12:00:00Z",
  "model": "structllm",
  "confidence": 0.85,
  "original_result": {
    "name": "智能保温杯",
    "dimensions": "350ml",
    "features": ["24小时保温", "不锈钢内胆"],
    "characteristics": ["便携", "大容量"]
  },
  "was_compressed": true
}
```

## API Endpoints

### Product CRUD Operations

```bash
# Create product with image upload
POST /api/v1/products
Content-Type: multipart/form-data
Body: image (file), name (optional), dimensions (optional), features (optional JSON), characteristics (optional JSON)

# List user's products (paginated)
GET /api/v1/products?offset=0&limit=20&name=search_term

# Get product detail
GET /api/v1/products/{product_id}

# Update product attributes
PUT /api/v1/products/{product_id}
Content-Type: application/json
Body: {name, dimensions, features, characteristics}

# Delete product (reclaims quota)
DELETE /api/v1/products/{product_id}
```

### Response Formats

Product summary (list endpoint):
```json
{
  "id": "uuid",
  "name": "产品名称",
  "dimensions": "350ml",
  "original_image_url": "/uploads/products/user_id/product_id.jpg",
  "recognition_confidence": 0.85,
  "image_size_bytes": 524288,
  "created_at": "2025-01-01T12:00:00Z",
  "updated_at": "2025-01-01T12:00:00Z"
}
```

Product detail (get endpoint):
```json
{
  ...summary fields,
  "features": ["特征1", "特征2"],
  "characteristics": ["特点1", "特点2"],
  "recognition_metadata": {...}
}
```

## Frontend Access

Navigate to: `https://your-domain.com/products`

Features:
- Image upload with preview
- AI recognition results display
- Manual attribute editing
- Product grid with search
- Confidence score badges
- Delete with confirmation

## Troubleshooting

### AI Recognition Not Working

1. Verify `LLM_API_KEY` and `LLM_API_BASE_URL` are set
2. Check `structllm` is installed: `pip install structllm`
3. Ensure LLM model supports vision (image input)
4. Check API quota/rate limits

### Image Upload Failures

1. Verify user has available storage quota
2. Check file permissions on `app/static/uploads/`
3. Ensure Pillow is installed: `pip install Pillow`
4. Check image format is supported (jpg, png)

### Storage Quota Issues

1. Check user's `storage_quota_bytes` and `storage_used_bytes` in database
2. Admins can adjust quotas via admin panel or API
3. Delete unused products to reclaim space
4. Verify quota updates are atomic (transaction-based)

## Security Considerations

- Product images are NOT encrypted (unlike video/image generation data)
- User ownership validation prevents cross-user access
- Admin users can view all products (override for management)
- 404 returned for non-existent products (prevents ID enumeration)
- Quota enforcement prevents storage exhaustion attacks

## Performance Optimization

- Image compression reduces API transmission time
- Pagination prevents large payload responses
- Debounced search (300ms) reduces API calls
- Confidence caching avoids re-recognition
- Retry logic handles transient API failures

## Dependencies

New dependencies added:
- `Pillow` - Image processing and compression
- `structllm` - Constrained LLM response formatting

Existing dependencies used:
- `tenacity` - Retry logic with exponential backoff
- `FastAPI` - REST API framework
- `SQLAlchemy` - Database ORM
- `Pydantic` - Data validation
