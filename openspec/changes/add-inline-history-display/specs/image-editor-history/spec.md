## ADDED Requirements

### Requirement: Inline History Display
The image editor SHALL display a generation history section directly below the prompt input area with collapsible visibility controls.

#### Scenario: Display history section on page load
- **WHEN** the image editor page loads
- **THEN** an inline generation history section appears below the prompt input
- **AND** the section displays the most recent 5-10 generation entries with thumbnails
- **AND** the section can be expanded to show more entries or collapsed to save space

#### Scenario: Empty state display
- **WHEN** no generation history exists
- **THEN** a placeholder message "No generation history yet" is displayed
- **AND** the empty state encourages users to create their first generation

### Requirement: View Generation History
Users SHALL be able to view generation history entries with thumbnails, prompts, model information, and timestamps.

#### Scenario: View history item details
- **WHEN** a user views the inline history section
- **THEN** each entry displays a thumbnail of the generated image
- **AND** displays the prompt text (truncated if longer than 100 characters)
- **AND** displays the model name and generation timestamp
- **AND** provides action buttons for load, edit, and delete operations

### Requirement: Load History Prompt
Users SHALL be able to load a previous generation's prompt back into the prompt input field.

#### Scenario: Load prompt from history
- **WHEN** a user clicks on a history entry or the "load" action button
- **THEN** the prompt text is copied into the main prompt input field
- **AND** the character count updates to reflect the new prompt length
- **AND** the generated image is displayed in the result area

### Requirement: Delete History Entry
Users SHALL be able to delete individual generation history entries with confirmation.

#### Scenario: Delete history entry with confirmation
- **WHEN** a user clicks the delete button on a history entry
- **THEN** a confirmation dialog appears asking "Delete this generation?"
- **AND** if confirmed, the entry is removed from both in-memory state and localStorage
- **AND** both inline display and side panel are updated to reflect the deletion
- **AND** a success toast notification confirms the deletion

### Requirement: Edit History Prompt
Users SHALL be able to edit the prompt text of existing history entries.

#### Scenario: Edit prompt inline
- **WHEN** a user clicks the edit button on a history entry
- **THEN** the prompt text becomes editable in place
- **AND** save and cancel buttons appear
- **AND** when saved, the updated prompt is persisted to localStorage
- **AND** both inline display and side panel reflect the updated prompt

### Requirement: State Synchronization
The system SHALL maintain consistent state between the inline history display and the existing side panel.

#### Scenario: Sync on history changes
- **WHEN** a generation history operation occurs (create, update, delete)
- **THEN** both the inline display and side panel are updated simultaneously
- **AND** localStorage is updated with the current state
- **AND** the state persists across page reloads

### Requirement: Expand/Collapse Control
The inline history section SHALL support expand/collapse functionality to manage screen space.

#### Scenario: Toggle visibility
- **WHEN** a user clicks the expand/collapse toggle button
- **THEN** the history section smoothly expands or collapses with animation
- **AND** the toggle button icon updates to indicate the current state
- **AND** the collapsed/expanded preference is saved to localStorage
