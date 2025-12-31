## ADDED Requirements

### Requirement: Product Recognition Preview API

The system SHALL provide an authenticated API to structure product information (preview-only) without creating a product record.

#### Scenario: Preview structured fields from image + unstructured text

- **WHEN** an authenticated user sends `POST /api/v1/products/recognize` with multipart fields `image` (required) and `raw_text` (optional)
- **THEN** the system SHALL validate the image is a supported type (JPEG/PNG)
- **AND** the system SHALL run the product recognition pipeline and produce structured fields: `name`, `dimensions`, `features`, `characteristics`, and `confidence`
- **AND** the system SHALL return the structured fields and recognition metadata in the response
- **AND** the system SHALL NOT create a product record and SHALL NOT persist the uploaded image

## MODIFIED Requirements

### Requirement: Create Product Can Skip AI Recognition

The system SHALL allow creating a product with an image while skipping AI recognition.

#### Scenario: Manual create without AI processing

- **WHEN** an authenticated user sends `POST /api/v1/products` with multipart `image` and `recognition_mode=manual`
- **THEN** the system SHALL enforce the user’s storage quota for the image upload
- **AND** the system SHALL store the image and create a product record using the user-provided fields (or defaults)
- **AND** the system SHALL NOT call the LLM recognition pipeline
- **AND** the system SHALL set `recognition_confidence` to `0.0`
- **AND** the system SHALL set `recognition_metadata` to `NULL`

#### Scenario: Create product from AI prefill without server-side AI processing

- **WHEN** an authenticated user sends `POST /api/v1/products` with multipart `image`, `recognition_mode=prefill`, and the preview recognition payload (confidence + metadata)
- **THEN** the system SHALL enforce the user’s storage quota for the image upload
- **AND** the system SHALL store the image and create a product record using the submitted structured fields
- **AND** the system SHALL NOT call the LLM recognition pipeline
- **AND** the system SHALL set `recognition_confidence` and `recognition_metadata` from the submitted preview recognition payload
