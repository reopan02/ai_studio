## ADDED Requirements
### Requirement: Admin manage user target descriptions
The system SHALL allow admin users to list, edit, and delete saved target descriptions across all users.

#### Scenario: List descriptions
- **WHEN** an admin sends GET request to `/api/v1/admin/target-descriptions` with limit and offset
- **THEN** the system SHALL return a paginated list of descriptions including user and target type context
- **AND** a non-admin request SHALL return 403 Forbidden

#### Scenario: Edit description
- **WHEN** an admin sends PUT request to `/api/v1/admin/target-descriptions/{id}` with a new description
- **THEN** the system SHALL update the record and return the updated description

#### Scenario: Delete description
- **WHEN** an admin sends DELETE request to `/api/v1/admin/target-descriptions/{id}`
- **THEN** the system SHALL delete the record and return 204 No Content
- **WHEN** the record does not exist
- **THEN** the system SHALL return 404 Not Found

### Requirement: Admin UI for target description management
The ecommerce image generator SHALL provide an admin-only management modal for saved target descriptions.

#### Scenario: Open management modal
- **WHEN** an admin user opens the target description management modal from the Generate Target module
- **THEN** the modal SHALL display a list of saved descriptions with user, target type, and updated time
- **AND** each list item SHALL provide edit and delete actions