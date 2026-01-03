## MODIFIED Requirements

### Requirement: E-Commerce Image Generator Page Entry
The system SHALL provide a dedicated E-Commerce Image Generator page accessible from the main portal using a wizard-style step-by-step layout.

#### Scenario: Wizard-based workflow layout
- **WHEN** an authenticated user navigates to `/ecommerce-image`
- **THEN** the system SHALL render a wizard-based layout with a top step navigation bar
- **AND** the step navigation SHALL display four steps: Product Selection, Template Configuration, Preview, and Generation
- **AND** the current step SHALL be visually highlighted
- **AND** completed steps SHALL display a checkmark indicator
- **AND** users SHALL be able to click on completed steps to navigate back

#### Scenario: Step navigation constraints
- **WHEN** a user attempts to navigate to a future step that has unmet prerequisites
- **THEN** the navigation SHALL be disabled or blocked
- **AND** a hint SHALL indicate what needs to be completed first

#### Scenario: Responsive layout
- **WHEN** the page is viewed on screens ≥1440px wide
- **THEN** the layout SHALL display as three columns: sidebar (products), main content, and preview/results panel
- **WHEN** the page is viewed on screens 1024-1439px wide
- **THEN** the layout SHALL display as two columns with wizard steps stacked vertically in main content
- **WHEN** the page is viewed on screens <1024px wide
- **THEN** the layout SHALL display as a single column with top navigation and vertically stacked content

### Requirement: Enhanced Typography and Spacing
The system SHALL use larger typography and increased spacing for improved readability.

#### Scenario: Font size specifications
- **WHEN** the page is rendered
- **THEN** template option chips SHALL use a minimum font size of 15px
- **AND** module titles SHALL use a minimum font size of 16px
- **AND** panel titles SHALL use a minimum font size of 18px
- **AND** button text SHALL use a minimum font size of 16px
- **AND** the main generate button SHALL use a minimum font size of 18px
- **AND** helper text SHALL use a minimum font size of 14px

#### Scenario: Spacing specifications
- **WHEN** the page is rendered
- **THEN** panel inner padding SHALL be at least 24px
- **AND** spacing between template option chips SHALL be at least 12px
- **AND** spacing between template groups SHALL be at least 28px
- **AND** step indicators SHALL have a minimum size of 36px diameter

### Requirement: Collapsible Template Groups
The system SHALL display template options in collapsible groups to reduce visual clutter.

#### Scenario: Collapsible group display
- **WHEN** a template module is rendered
- **THEN** it SHALL be displayed as a collapsible group with a header showing the category name
- **AND** the header SHALL include an expand/collapse toggle button
- **AND** expanding a group SHALL reveal all template option chips within

#### Scenario: Collapsed group summary
- **WHEN** a template group is collapsed
- **THEN** the header SHALL display a summary of selected options count or labels
- **AND** clicking anywhere on the header SHALL expand the group

#### Scenario: Default expansion state
- **WHEN** the template configuration step is initially displayed
- **THEN** the first group with no selections SHALL be expanded by default
- **AND** groups that have selections SHALL start collapsed to reduce visual noise

### Requirement: Wizard Step Content Organization
The system SHALL organize content into four distinct wizard steps.

#### Scenario: Step 1 - Product Selection
- **WHEN** step 1 is active
- **THEN** the main panel SHALL display: product search and list, product images grid, editable product information fields
- **AND** selecting a product SHALL automatically select its primary image
- **AND** step completion requires: a product selected AND at least one reference image selected

#### Scenario: Step 2 - Template Configuration
- **WHEN** step 2 is active
- **THEN** the main panel SHALL display: collapsible template groups (scene, angle, style, target), prompt template editor
- **AND** each group SHALL support multi-select chips with inline edit capability
- **AND** step completion requires: at least one template option selected in any category

#### Scenario: Step 3 - Preview
- **WHEN** step 3 is active
- **THEN** the main panel SHALL display: structured prompt preview with labeled segments, full prompt text, copy to clipboard action
- **AND** variable values SHALL be highlighted in the structured preview
- **AND** empty segments SHALL indicate their missing state

#### Scenario: Step 4 - Generation
- **WHEN** step 4 is active
- **THEN** the main panel SHALL display: generate button (prominent), generation status/spinner, result image when available, download and regenerate actions
- **AND** the generate button SHALL be disabled if prerequisites are not met

### Requirement: Step Transition Animation
The system SHALL provide smooth visual transitions between wizard steps.

#### Scenario: Step change animation
- **WHEN** a user navigates between wizard steps
- **THEN** the outgoing step content SHALL fade out
- **AND** the incoming step content SHALL fade in
- **AND** the total transition duration SHALL be 200-300ms
