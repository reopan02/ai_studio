## ADDED Requirements

### Requirement: Target Type Data Model
The system SHALL store target types in a database table with configurable prompt templates.

#### Scenario: Target type data structure
- **WHEN** the system initializes
- **THEN** the `target_types` table SHALL exist with columns: id, name, placeholder, default_template, sort_order, created_at, updated_at
- **AND** the table SHALL be pre-populated with default target types: 主图, 详情页, 海报, 白底图, 场景图

### Requirement: Target Types API
The system SHALL provide RESTful APIs for managing target types.

#### Scenario: List target types
- **WHEN** a client sends GET request to `/api/v1/target-types`
- **THEN** the system SHALL return a list of all target types ordered by sort_order
- **AND** each target type SHALL include: id, name, placeholder, default_template, sort_order

#### Scenario: Create target type (admin only)
- **WHEN** an admin user sends POST request to `/api/v1/target-types` with name, placeholder, default_template
- **THEN** the system SHALL create a new target type and return the created object
- **WHEN** a non-admin user attempts to create a target type
- **THEN** the system SHALL return 403 Forbidden

#### Scenario: Update target type (admin only)
- **WHEN** an admin user sends PUT request to `/api/v1/target-types/:id` with updated fields
- **THEN** the system SHALL update the target type and return the updated object
- **WHEN** the target type does not exist
- **THEN** the system SHALL return 404 Not Found

#### Scenario: Delete target type (admin only)
- **WHEN** an admin user sends DELETE request to `/api/v1/target-types/:id`
- **THEN** the system SHALL delete the target type and return 204 No Content
- **WHEN** the target type does not exist
- **THEN** the system SHALL return 404 Not Found

### Requirement: Smart Prompt Template UI
The system SHALL provide intelligent prompt guidance based on selected target type.

#### Scenario: Single-select target type
- **WHEN** the user views the "生成目标" module in ecommerce image generator
- **THEN** target types SHALL be displayed as radio buttons (single-select)
- **AND** only one target type can be selected at a time

#### Scenario: Dynamic placeholder text
- **WHEN** a user selects a target type
- **THEN** the prompt input box SHALL update its placeholder text to the selected type's `placeholder` field
- **AND** the placeholder SHALL guide the user on what to describe

#### Scenario: Default template auto-fill
- **WHEN** a user selects a target type
- **THEN** the prompt input box SHALL be pre-filled with the selected type's `default_template` content
- **AND** the user SHALL be able to edit the pre-filled content

#### Scenario: Prompt generation without target name
- **WHEN** the system generates the final prompt
- **THEN** the prompt SHALL NOT include the target type name directly (e.g., "主图")
- **AND** the prompt SHALL include the user's edited target description content instead

### Requirement: Admin Target Type Management
The system SHALL provide an admin interface for managing target types.

#### Scenario: Target type management tab
- **WHEN** an admin user navigates to the Admin page
- **THEN** a "目标类型管理" tab SHALL be available
- **AND** clicking the tab SHALL display the target type management interface

#### Scenario: Target type list display
- **WHEN** the target type management interface is displayed
- **THEN** all target types SHALL be shown in a table with columns: name, placeholder, default_template, actions
- **AND** target types SHALL be ordered by sort_order

#### Scenario: Add new target type
- **WHEN** an admin clicks the "添加目标类型" button
- **THEN** a form dialog SHALL appear with fields: name, placeholder, default_template
- **AND** submitting the form SHALL create a new target type and refresh the list

#### Scenario: Edit target type
- **WHEN** an admin clicks the edit button for a target type
- **THEN** an edit form SHALL appear pre-filled with the current values
- **AND** submitting the form SHALL update the target type and refresh the list

#### Scenario: Delete target type
- **WHEN** an admin clicks the delete button for a target type
- **THEN** a confirmation dialog SHALL appear
- **AND** confirming SHALL delete the target type and refresh the list

### Requirement: Fallback for Offline/Error Scenarios
The system SHALL provide fallback behavior when target types cannot be loaded.

#### Scenario: API load failure fallback
- **WHEN** the frontend fails to load target types from the API
- **THEN** the system SHALL use built-in default target types
- **AND** the user experience SHALL not be blocked
