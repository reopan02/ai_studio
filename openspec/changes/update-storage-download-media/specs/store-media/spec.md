## ADDED Requirements

### Requirement: Store remote media content
The system SHALL download and store media bytes when creating image or video repository records that include an HTTP/HTTPS media URL.

#### Scenario: Store image content on create
- **WHEN** a client creates an image record with an HTTP/HTTPS image_url
- **THEN** the system SHALL download the image bytes
- **AND** SHALL encrypt and store the bytes in the user database
- **AND** SHALL record the content MIME type and size
- **AND** SHALL update the user's storage usage to include the stored content size

#### Scenario: Store video content on create
- **WHEN** a client creates a video record with an HTTP/HTTPS video_url
- **THEN** the system SHALL download the video bytes
- **AND** SHALL encrypt and store the bytes in the user database
- **AND** SHALL record the content MIME type and size
- **AND** SHALL update the user's storage usage to include the stored content size

### Requirement: Serve stored media content
The system SHALL provide authenticated endpoints to deliver stored media bytes for image and video records.

#### Scenario: Serve stored image content
- **WHEN** an authenticated user requests the stored content endpoint for an image they own
- **THEN** the system SHALL return the stored bytes with the correct content type
- **AND** SHALL return 404 if no stored content exists

#### Scenario: Serve stored video content
- **WHEN** an authenticated user requests the stored content endpoint for a video they own
- **THEN** the system SHALL return the stored bytes with the correct content type
- **AND** SHALL return 404 if no stored content exists

### Requirement: Content URL exposure
The system SHALL include a stable content_url in image/video API responses when stored media exists.

#### Scenario: List images with content URLs
- **WHEN** a client requests the image list endpoint
- **THEN** each record with stored content SHALL include content_url
- **AND** records without stored content SHALL omit content_url or set it to null

#### Scenario: List videos with content URLs
- **WHEN** a client requests the video list endpoint
- **THEN** each record with stored content SHALL include content_url
- **AND** records without stored content SHALL omit content_url or set it to null

### Requirement: Download limits and failure behavior
The system SHALL enforce download size limits and quota checks when storing media.

#### Scenario: Reject oversized downloads
- **WHEN** the media content size exceeds the allowed limit or the user's remaining quota
- **THEN** the system SHALL return HTTP 413
- **AND** SHALL NOT persist the record

#### Scenario: Download failure
- **WHEN** the media download fails or returns a non-success status
- **THEN** the system SHALL return an error response
- **AND** SHALL NOT persist the record
