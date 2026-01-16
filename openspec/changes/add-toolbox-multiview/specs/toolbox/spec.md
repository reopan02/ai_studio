## ADDED Requirements

### Requirement: Toolbox entry in portal
The system SHALL expose a toolbox entry in the portal AI generation section that links to the toolbox page.

#### Scenario: Navigate to toolbox
- **WHEN** a user opens the portal page
- **THEN** the AI generation section shows a toolbox card
- **AND** selecting it navigates to /toolbox

### Requirement: Toolbox multiview module
The system SHALL provide a toolbox page with a multiview generation module that reads products from the product library and supports selecting multiple reference images.

#### Scenario: Select product and images
- **WHEN** a user selects a product
- **THEN** the page loads product details and associated images
- **AND** the user can select multiple reference images

### Requirement: Multiview generation request
The system SHALL generate a single 2x2 white-background multiview grid per result using the image edits endpoint, based on the selected product name and reference images, with configurable model, aspect ratio, resolution, and concurrency.

#### Scenario: Generate multiview grid
- **WHEN** a user configures settings and triggers generation
- **THEN** the system sends an image edits request with the multiview prompt and selected images
- **AND** each returned image is a single 2x2 multiview grid

### Requirement: Results and persistence
The system SHALL display generated grid images with preview and download actions and persist them to the user image repository with toolbox metadata.

#### Scenario: View and save result
- **WHEN** generation succeeds
- **THEN** the result gallery shows returned grids
- **AND** each result is stored with source=toolbox-multiview metadata
