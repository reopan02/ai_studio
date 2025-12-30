## ADDED Requirements

### Requirement: Video Page as Vue Entry
The system SHALL implement the video generation page (`/video`) using Vue 3 + TypeScript.

#### Scenario: Load the video studio UI
- **WHEN** an authenticated user visits `/video`
- **THEN** the page renders the video generation UI and loads required assets successfully

### Requirement: Preserve Upstream Generation Configuration
The video page SHALL preserve the ability to generate videos via a user-configured upstream API using an API key and base URL stored in localStorage.

#### Scenario: Persist API settings
- **WHEN** a user sets an API key and base URL in the UI
- **THEN** the settings are persisted in localStorage
- **AND** reloading the page restores the saved settings

#### Scenario: Use upstream configuration for generation
- **WHEN** a user starts a generation task
- **THEN** the client uses the configured upstream base URL and API key for upstream requests

### Requirement: Persist and Manage Video History
The video page SHALL continue to persist generated videos to the backend repository and provide history CRUD operations.

#### Scenario: Save a completed video
- **WHEN** a generation completes successfully
- **THEN** the client persists the record via backend endpoints under `/api/v1/videos`

#### Scenario: Delete a saved video
- **WHEN** a user deletes a saved video from history
- **THEN** the client calls `DELETE /api/v1/videos/{id}` with required credentials/CSRF headers
- **AND** the deleted item is removed from the UI

