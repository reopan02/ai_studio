## ADDED Requirements

### Requirement: Unified Sidebar Layout
The video generation page SHALL use a sidebar + main content layout matching the image editor architecture.

#### Scenario: Display sidebar with collapsible sections
- **WHEN** the video generation page loads
- **THEN** a left sidebar displays with collapsible sections
- **AND** sections include: API Configuration, Model Selection, Video Parameters, Reference Images
- **AND** each section has a chevron indicator showing expand/collapse state
- **AND** collapsed state is persisted to localStorage

#### Scenario: Sidebar responsive behavior
- **WHEN** the viewport width is less than 1024px
- **THEN** the sidebar collapses to a narrower width or becomes a slide-in panel
- **AND** touch/click toggles visibility on mobile

### Requirement: Central Video Preview Area
The video generation page SHALL display a central preview area for video output matching the image editor result area pattern.

#### Scenario: Show placeholder state
- **WHEN** no video has been generated
- **THEN** a placeholder with video icon and instructional text is displayed
- **AND** the placeholder text reads "Ready to Create" or similar

#### Scenario: Show loading state
- **WHEN** a video generation task is submitted
- **THEN** the placeholder is replaced with a loading spinner and progress indicator
- **AND** status text indicates "Generating your video..."

#### Scenario: Show video result
- **WHEN** a video generation completes successfully
- **THEN** the video is displayed in a player with playback controls
- **AND** result actions (Download, Share, Fullscreen) appear below the player

### Requirement: Unified Prompt Section
The video generation page SHALL display a prompt input section matching the image editor layout.

#### Scenario: Prompt input with character count
- **WHEN** the user views the main content area
- **THEN** a prompt textarea appears below the video preview area
- **AND** a character count displays the current prompt length
- **AND** a status indicator shows the current state (Ready, Generating, Error)

#### Scenario: Generate button styling
- **WHEN** the prompt section is displayed
- **THEN** a Generate button appears with matching style to image editor
- **AND** the button includes an icon and "Generate" text
- **AND** the button disables during generation

### Requirement: Inline Generation History
The video generation page SHALL display an inline history section below the prompt area matching the image editor pattern.

#### Scenario: Display inline history grid
- **WHEN** generation history exists
- **THEN** a collapsible section displays video thumbnails in a grid
- **AND** each item shows thumbnail, prompt preview, model name, and timestamp
- **AND** a count badge shows total history items

#### Scenario: History CRUD operations
- **WHEN** the user hovers over a history item
- **THEN** action buttons appear (Load, Edit Prompt, Delete)
- **AND** clicking Load loads the prompt and displays the video
- **AND** clicking Edit opens a modal to edit the prompt
- **AND** clicking Delete shows confirmation then removes the item

#### Scenario: History expand/collapse
- **WHEN** the user clicks the history section toggle
- **THEN** the section smoothly expands or collapses
- **AND** the toggle icon rotates to indicate state
- **AND** the preference is saved to localStorage

### Requirement: Task/History Side Panel
The video generation page SHALL provide a slide-in right panel for task management.

#### Scenario: Open side panel
- **WHEN** the user clicks the history button in the header
- **THEN** a panel slides in from the right
- **AND** the panel displays active tasks and complete history
- **AND** clicking outside or pressing Escape closes the panel

### Requirement: Consistent Component Styling
The video generation page SHALL use identical styling patterns to the image editor.

#### Scenario: Form controls styling
- **WHEN** form inputs are displayed
- **THEN** they use the same styling as image editor (colors, borders, focus states)

#### Scenario: Button styling
- **WHEN** buttons are displayed
- **THEN** they follow the same hierarchy: primary (accent color), secondary (muted), ghost (transparent)

#### Scenario: Toast notifications
- **WHEN** a notification is triggered
- **THEN** it appears in the same position and with the same styling as image editor

### Requirement: Keyboard Shortcuts
The video generation page SHALL support the same keyboard shortcuts as the image editor.

#### Scenario: Escape key closes panels
- **WHEN** the user presses Escape
- **THEN** any open modal or side panel closes

#### Scenario: Ctrl+Enter submits
- **WHEN** the user presses Ctrl+Enter (or Cmd+Enter on Mac) while in prompt textarea
- **THEN** the generate action is triggered
