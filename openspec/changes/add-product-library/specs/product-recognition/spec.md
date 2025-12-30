## ADDED Requirements

### Requirement: AI-Based Product Attribute Extraction

The system SHALL use LLM vision capabilities to automatically extract structured product attributes from uploaded product images.

#### Scenario: Successful product recognition with high confidence

- **WHEN** a user uploads a clear product image (e.g., a thermos bottle on white background)
- **THEN** the system SHALL call the LLM API with the product image and a structured prompt
- **AND** the system SHALL return a JSON response containing product name, dimensions, features (list), characteristics (list), and a confidence score (0.0-1.0)
- **AND** the confidence score SHALL be >= 0.7 for well-recognized products

#### Scenario: Low confidence recognition requiring manual review

- **WHEN** the LLM returns a confidence score < 0.7 or missing required fields (name, dimensions)
- **THEN** the system SHALL mark incomplete fields with a low-confidence indicator
- **AND** the system SHALL allow the user to manually edit or complete the extracted attributes
- **AND** the system SHALL save the product with the user-corrected values

#### Scenario: AI recognition failure fallback

- **WHEN** the LLM API call fails (timeout, rate limit, service error)
- **THEN** the system SHALL return an error response indicating recognition failure
- **AND** the system SHALL allow the user to manually enter all product attributes
- **AND** the system SHALL set confidence score to 0.0 for manually entered products

### Requirement: Structured Prompt Engineering

The system SHALL use StructLLM library to constrain LLM responses to a predefined Pydantic schema.

#### Scenario: Structured output validation

- **WHEN** calling the LLM API for product recognition
- **THEN** the system SHALL provide a Pydantic model with fields: name (str), dimensions (str), features (List[str]), characteristics (List[str]), confidence (float)
- **AND** the system SHALL use a Chinese-language prompt: "识别这张图片中的产品,返回产品名称、尺寸、功能特征和特点"
- **AND** the LLM response SHALL be automatically validated against the Pydantic schema
- **AND** validation failures SHALL raise a clear exception with field-level error details

### Requirement: Image Preprocessing for Recognition

The system SHALL preprocess uploaded images before sending to the LLM API.

#### Scenario: Image compression before LLM call

- **WHEN** an uploaded product image exceeds 5MB in size
- **THEN** the system SHALL compress the image to reduce file size
- **AND** the compression SHALL use JPEG format with quality parameter >= 85
- **AND** the compressed image SHALL be sent to the LLM API
- **AND** the original full-resolution image SHALL be stored in the product library

#### Scenario: Image format conversion

- **WHEN** an uploaded image is in PNG or other lossless format
- **THEN** the system SHALL convert it to JPEG for LLM API transmission
- **AND** the system SHALL preserve the original format in storage
- **AND** the system SHALL track both original and processed image sizes in metadata

### Requirement: Recognition Metadata Storage

The system SHALL store the complete AI recognition response for debugging and audit purposes.

#### Scenario: Store full LLM response

- **WHEN** the LLM API successfully returns product attributes
- **THEN** the system SHALL save the full JSON response in the product's `recognition_metadata` field
- **AND** the metadata SHALL include raw LLM output, confidence score, and timestamp
- **AND** the metadata SHALL be accessible via the product detail API endpoint

#### Scenario: Track recognition source

- **WHEN** a product is created or updated
- **THEN** the system SHALL record whether attributes came from AI recognition or manual entry
- **AND** the `recognition_metadata` field SHALL be NULL for fully manual entries
- **AND** the `confidence` field SHALL be 0.0 for manual entries and 0.0-1.0 for AI-assisted entries
