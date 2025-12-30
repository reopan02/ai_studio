## ADDED Requirements

### Requirement: Products Page Build Entry

The system SHALL provide a Vite MPA build entry for the Product Library UI.

#### Scenario: Products page is included in frontend build output

- **WHEN** the frontend is built using the project’s Vite configuration
- **THEN** the build output SHALL include a Products page entry (HTML + bundled assets) alongside existing pages (e.g. video, storage, image)
- **AND** the Products page entry SHALL load a Vue 3 + TypeScript application for the Product Library UI

### Requirement: Product Library UI Uses Backend APIs

The Product Library UI SHALL integrate with the backend Product Library APIs defined by `add-product-library`.

#### Scenario: Upload product image and create product

- **WHEN** a logged-in user selects an image and submits the upload form in the Product Library UI
- **THEN** the UI SHALL call `POST /api/v1/products` using multipart form upload
- **AND** the UI SHALL display the created product using the API response (including `original_image_url` and `recognition_confidence`)

#### Scenario: List products with pagination and search

- **WHEN** the Product Library UI loads or the user searches by name
- **THEN** the UI SHALL call `GET /api/v1/products` with `offset`, `limit`, and optional `name` query parameters
- **AND** the UI SHALL render the returned list of products and pagination controls based on `total`

#### Scenario: Delete a product

- **WHEN** a user confirms deletion of a product in the Product Library UI
- **THEN** the UI SHALL call `DELETE /api/v1/products/{id}`
- **AND** the UI SHALL refresh the product list after successful deletion

#### Scenario: Update product attributes (manual correction)

- **WHEN** a user edits product attributes in the Product Library UI (name, dimensions, features, characteristics)
- **THEN** the UI SHALL call `PUT /api/v1/products/{id}` with the updated attributes
- **AND** the UI SHALL update the displayed product data based on the API response

### Requirement: Cookie Auth CSRF Handling

The Product Library UI SHALL support cookie-based authentication flows with CSRF protection for unsafe methods.

#### Scenario: CSRF token is sent for unsafe methods

- **WHEN** the browser has an `access_token` cookie and the UI issues a non-safe request to `/api/v1/products` (e.g. POST/PUT/DELETE)
- **THEN** the UI SHALL include the `X-CSRF-Token` header whose value matches the `csrf_token` cookie
