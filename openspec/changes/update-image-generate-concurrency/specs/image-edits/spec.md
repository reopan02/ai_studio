## ADDED Requirements

### Requirement: Interpret `n` as concurrency for image edits
The system SHALL interpret the `n` form field on `POST /api/v1/images/edits` as the requested image count and the concurrency level for upstream image edit calls, bounded to the server’s supported range.

#### Scenario: Edit multiple images in one request
- **WHEN** an authenticated user calls `POST /api/v1/images/edits` with `n=3`
- **THEN** the system issues 3 upstream edit calls concurrently
- **AND** the system returns a successful response containing 3 images in `response.data`

### Requirement: Omit provider `n` from outbound edit requests
The system SHALL NOT include an `n` field in the outbound request payload when calling an upstream `/v1/images/edits`-style endpoint.

#### Scenario: Upstream edit request payload does not contain `n`
- **WHEN** an authenticated user calls `POST /api/v1/images/edits` with `n=4`
- **THEN** each upstream request payload omits the `n` field

### Requirement: Aggregate upstream edit results into a single OpenAI-compatible response
The system SHALL aggregate upstream responses into a single OpenAI-compatible response object with a combined `data` array.

#### Scenario: Aggregate edit results
- **WHEN** each upstream call returns a response containing a single image in `data`
- **THEN** the final response contains a combined `data` array with `n` images

### Requirement: Fail the edit request if any upstream call fails
The system SHALL return an HTTP `502` response if any of the upstream calls fails.

#### Scenario: One upstream edit call fails
- **WHEN** at least one upstream call returns a non-2xx response
- **THEN** the system returns `502`
