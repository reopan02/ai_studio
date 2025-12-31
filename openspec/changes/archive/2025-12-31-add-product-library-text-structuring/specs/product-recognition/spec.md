## MODIFIED Requirements

### Requirement: Recognition Uses Image And Optional Unstructured Text

The recognition pipeline SHALL support using unstructured user-provided text to improve structured extraction.

#### Scenario: Use `raw_text` to improve extraction quality

- **WHEN** preview recognition is requested with an image and a non-empty `raw_text`
- **THEN** the system SHALL include `raw_text` as additional context in the LLM prompt
- **AND** the structured output SHALL still conform to the existing recognition schema (name/dimensions/features/characteristics/confidence)
- **AND** if `raw_text` conflicts with the image, the system SHALL prefer information that is visually confirmed and reduce confidence accordingly

