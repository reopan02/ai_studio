## MODIFIED Requirements

### Requirement: E-Commerce Image Generator Page Entry
The system SHALL provide a dedicated E-Commerce Image Generator page accessible from the main portal.

#### Scenario: Single-page workflow layout
- **WHEN** an authenticated user navigates to `/ecommerce-image`
- **THEN** the system SHALL render a single-page workflow that keeps the existing visual design system
- **AND** the page SHALL present a configuration sidebar and a main workflow area
- **AND** the main workflow area SHALL show sections in order: product info, template selection, prompt preview, and generation/result
- **AND** each section SHALL display a concise hint when its prerequisites are missing (e.g., no product selected, no reference images)

#### Scenario: UI copy renders correctly
- **WHEN** the page is rendered
- **THEN** all Chinese UI labels and helper text SHALL display without mojibake or replacement glyphs

### Requirement: Prompt Template System
The system SHALL provide a modular prompt template builder with preset options.

#### Scenario: Display template modules as chip groups
- **WHEN** the template modules are displayed
- **THEN** each module SHALL render its options as selectable chips
- **AND** users SHALL be able to select multiple chips per module
- **AND** selected chips SHALL be visually distinct

#### Scenario: Default template options
- **WHEN** the template modules are displayed
- **THEN** Scene options SHALL include at minimum: a plain white background, a natural-light tabletop, an outdoor scene, and a solid color background
- **AND** Angle options SHALL include at minimum: front, 45-degree side, top-down, and eye-level
- **AND** Style/Lighting options SHALL include at minimum: soft lighting, natural light, and studio lighting
- **AND** Target options SHALL include at minimum: main image, detail page, and poster

#### Scenario: Add/edit options inline
- **WHEN** a user adds a template option
- **THEN** the system SHALL insert a new editable chip and focus it for inline editing
- **AND** the new chip SHALL be immediately selectable

### Requirement: Template Customization
The system SHALL allow users to customize prompt templates.

#### Scenario: Edit template option text without losing selection
- **WHEN** a user edits the text of a selected chip
- **THEN** the selection state SHALL remain active after the edit
- **AND** the prompt preview SHALL reflect the edited text immediately

#### Scenario: Delete template option
- **WHEN** a user deletes a custom template option
- **THEN** the option SHALL be removed from the UI and localStorage
- **AND** any active selection for that option SHALL be removed

#### Scenario: Persist custom templates
- **WHEN** a user customizes template options
- **THEN** the customizations SHALL be stored in browser localStorage
- **AND** customizations SHALL be restored when the user revisits the page

### Requirement: Real-Time Prompt Preview
The system SHALL display a live preview of the composed prompt.

#### Scenario: Structured preview segments
- **WHEN** the user updates product info or template selections
- **THEN** the preview SHALL display labeled segments for product info, scene, angle, style, and target
- **AND** each segment SHALL indicate when it is empty or missing
- **AND** the final composed prompt SHALL be visible for copying

#### Scenario: Compose prompt from selections
- **WHEN** the user has selected a product and template options
- **THEN** the system SHALL concatenate: product info fields + scene + angle + style + target into a coherent prompt
- **AND** the preview SHALL update in real-time as selections change

#### Scenario: Copy prompt to clipboard
- **WHEN** the user clicks the copy action in the prompt preview
- **THEN** the composed prompt SHALL be copied to the system clipboard
- **AND** a success toast notification SHALL be displayed

#### Scenario: Prompt format
- **WHEN** displaying the composed prompt
- **THEN** the format SHALL be: "[product name] [product features], [scene description], [shooting angle], [style/lighting], [target style requirements]"
- **AND** optional fields that are not selected SHALL be omitted from the prompt
