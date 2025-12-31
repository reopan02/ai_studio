## ADDED Requirements

### Requirement: AI Prefill Workflow In Product Library UI

The Product Library UI SHALL support an AI prefill step that does not persist products until the user explicitly saves.

#### Scenario: AI prefill does not create a product

- **WHEN** a user selects an image and clicks “AI整理预填”
- **THEN** the UI SHALL call `POST /api/v1/products/recognize` with multipart `image` and optional `raw_text`
- **AND** the UI SHALL fill the structured form fields with the response values
- **AND** the UI SHALL NOT create a product until the user clicks “保存产品”

### Requirement: Manual Save Workflow

The Product Library UI SHALL allow saving a product without triggering AI processing.

#### Scenario: Create product manually without AI

- **WHEN** a user fills the structured fields manually and clicks “保存产品”
- **THEN** the UI SHALL call `POST /api/v1/products` with multipart `image` and `recognition_mode=manual`
- **AND** the UI SHALL refresh the product list after creation

### Requirement: Save After AI Prefill

The Product Library UI SHALL allow saving a product using the preview recognition payload without a second recognition call.

#### Scenario: Save after AI prefill persists recognition payload

- **WHEN** a user clicks “保存产品” after an “AI整理预填” operation
- **THEN** the UI SHALL call `POST /api/v1/products` with multipart `image` and `recognition_mode=prefill`
- **AND** the request SHALL include the preview recognition payload (confidence + metadata)
- **AND** the UI SHALL refresh the product list after creation

### Requirement: Portal Entry For Product Library

The Portal page SHALL provide a navigation entry to the Product Library.

#### Scenario: Portal links to `/products`

- **WHEN** a user opens the Portal page (`GET /`)
- **THEN** the UI SHALL display a “产品库” entry that navigates to `/products`
