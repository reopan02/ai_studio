## ADDED Requirements

### Requirement: Vue 3 + TypeScript Build System
The system SHALL build the frontend using Vue 3 and TypeScript.

#### Scenario: Build multi-page artifacts
- **WHEN** a developer runs the frontend build command
- **THEN** the build produces separate HTML entry files for each page
- **AND** JavaScript/CSS assets are emitted with hashed filenames suitable for long-term caching

#### Scenario: Type-check the frontend
- **WHEN** a developer runs the frontend type-check command
- **THEN** TypeScript completes without type errors

### Requirement: Vite Multi-Page (Plan B)
The system SHALL use a Vite multi-page build so each backend route maps to a dedicated HTML entry.

#### Scenario: Route-to-entry mapping
- **WHEN** the server serves `/`, `/login`, `/video`, `/storage`, `/admin`, and `/image`
- **THEN** each route renders its corresponding built HTML entry
- **AND** the page loads its JavaScript/CSS assets from the configured static mounts

### Requirement: Preserve Backend API Contracts
The migration SHALL NOT require changes to existing backend API contracts.

#### Scenario: Existing API calls remain valid
- **WHEN** users interact with the migrated frontend
- **THEN** requests to existing endpoints under `/api/v1/*` continue to function as before

