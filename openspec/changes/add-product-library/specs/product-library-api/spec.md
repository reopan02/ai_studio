## ADDED Requirements

### Requirement: Product CRUD API Endpoints

The system SHALL provide REST API endpoints for creating, reading, updating, and deleting products.

#### Scenario: Create product with image upload and AI recognition

- **WHEN** an authenticated user sends a POST request to `/api/v1/products` with a multipart form containing an image file
- **THEN** the system SHALL validate the user's storage quota has sufficient space
- **AND** the system SHALL save the uploaded image to the file system
- **AND** the system SHALL trigger AI recognition to extract product attributes
- **AND** the system SHALL create a new product record in the database with user_id, extracted attributes, image URL, and confidence score
- **AND** the system SHALL increment the user's `storage_used_bytes` by the image file size
- **AND** the system SHALL return a 201 Created response with the product ID and recognized attributes

#### Scenario: List user's products with pagination

- **WHEN** an authenticated user sends a GET request to `/api/v1/products`
- **THEN** the system SHALL return a paginated list of products owned by the current user
- **AND** the response SHALL include product ID, name, dimensions, image URL, created timestamp, and confidence score
- **AND** the system SHALL support `offset` and `limit` query parameters for pagination (default limit=20)
- **AND** the system SHALL support `name` query parameter for case-insensitive filtering
- **AND** the response SHALL include total count metadata

#### Scenario: Get product detail by ID

- **WHEN** an authenticated user sends a GET request to `/api/v1/products/{id}`
- **THEN** the system SHALL return the full product details if the product belongs to the current user
- **AND** the response SHALL include all attributes: name, dimensions, features, characteristics, image URL, confidence, recognition metadata, and timestamps
- **AND** the system SHALL return 404 Not Found if the product does not exist or belongs to another user

#### Scenario: Update product attributes manually

- **WHEN** an authenticated user sends a PUT request to `/api/v1/products/{id}` with updated attributes
- **THEN** the system SHALL validate the product belongs to the current user
- **AND** the system SHALL update the specified fields (name, dimensions, features, characteristics)
- **AND** the system SHALL preserve the original AI recognition metadata
- **AND** the system SHALL update the `updated_at` timestamp
- **AND** the system SHALL return 200 OK with the updated product data

#### Scenario: Delete product and reclaim storage quota

- **WHEN** an authenticated user sends a DELETE request to `/api/v1/products/{id}`
- **THEN** the system SHALL validate the product belongs to the current user
- **AND** the system SHALL delete the product image file from the file system
- **AND** the system SHALL decrement the user's `storage_used_bytes` by the image size
- **AND** the system SHALL delete the product record from the database
- **AND** the system SHALL return 204 No Content

### Requirement: Product Storage Quota Enforcement

The system SHALL enforce user storage quotas when uploading product images.

#### Scenario: Reject upload when quota exceeded

- **WHEN** a user attempts to upload a product image that would exceed their storage quota
- **THEN** the system SHALL calculate: `current_used_bytes + new_image_size > storage_quota_bytes`
- **AND** the system SHALL return 403 Forbidden with an error message indicating insufficient storage
- **AND** the system SHALL NOT save the image or create a product record
- **AND** the response SHALL include quota details: quota, used, available, and requested size

#### Scenario: Successful upload within quota

- **WHEN** a user uploads a product image and `current_used_bytes + new_image_size <= storage_quota_bytes`
- **THEN** the system SHALL save the image and create the product
- **AND** the system SHALL atomically update `storage_used_bytes` in the same database transaction
- **AND** the system SHALL return the product creation response

### Requirement: Product Image Storage Management

The system SHALL store product images in a structured file system hierarchy.

#### Scenario: Save uploaded product image

- **WHEN** a product image is uploaded
- **THEN** the system SHALL save the file to `static/uploads/products/{user_id}/{product_id}.{ext}`
- **AND** the system SHALL generate a unique product UUID for the filename
- **AND** the system SHALL preserve the original file extension (jpg, jpeg, png)
- **AND** the system SHALL set the `original_image_url` field to the relative path

#### Scenario: Serve product images via static file endpoint

- **WHEN** a client requests a product image URL
- **THEN** the system SHALL serve the image file from the file system
- **AND** the system SHALL set appropriate Content-Type headers (image/jpeg, image/png)
- **AND** the system SHALL apply caching headers (Cache-Control: public, max-age=31536000 for production)

### Requirement: Product Ownership Validation

The system SHALL ensure users can only access and modify their own products.

#### Scenario: Prevent cross-user product access

- **WHEN** a user attempts to GET, PUT, or DELETE a product that belongs to another user
- **THEN** the system SHALL return 404 Not Found (not 403, to avoid information leakage)
- **AND** the system SHALL NOT reveal whether the product ID exists

#### Scenario: Admin override for product management

- **WHEN** an admin user (is_admin=true) accesses any product endpoint
- **THEN** the system SHALL allow access to products across all users
- **AND** the response SHALL include the owner's user_id for reference

### Requirement: Product Data Validation

The system SHALL validate product attributes according to schema constraints.

#### Scenario: Validate required fields on creation

- **WHEN** creating a product via POST /api/v1/products
- **THEN** the system SHALL require: image file (multipart upload)
- **AND** the system SHALL allow optional fields: name, dimensions, features, characteristics (can be provided manually or overridden from AI recognition)
- **AND** the system SHALL return 422 Unprocessable Entity with field-level errors for invalid data

#### Scenario: Validate field length constraints

- **WHEN** updating product attributes
- **THEN** the system SHALL enforce: name max 200 characters, dimensions max 100 characters
- **AND** the system SHALL validate features and characteristics as JSON arrays of strings
- **AND** the system SHALL return validation errors for constraint violations

### Requirement: Product Search and Filtering

The system SHALL support basic filtering of products by name.

#### Scenario: Case-insensitive name search

- **WHEN** a user sends GET /api/v1/products?name=保温
- **THEN** the system SHALL return products where the name contains "保温" (case-insensitive)
- **AND** the system SHALL use SQL ILIKE operator for matching
- **AND** the system SHALL only return products owned by the current user

#### Scenario: Combine search with pagination

- **WHEN** a user sends GET /api/v1/products?name=杯子&offset=10&limit=5
- **THEN** the system SHALL apply the name filter first
- **AND** the system SHALL apply pagination to the filtered results
- **AND** the total count SHALL reflect the filtered result set size
