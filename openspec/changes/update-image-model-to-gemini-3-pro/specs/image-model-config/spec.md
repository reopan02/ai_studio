## ADDED Requirements

### Requirement: Gemini 3 Pro Image Preview Model Support

The system SHALL support `gemini-3-pro-image-preview` as the default image generation model for all image generation interfaces.

#### Scenario: Default model selection
- **WHEN** user opens the e-commerce image generator or general image generator page
- **THEN** the model selector SHALL default to `gemini-3-pro-image-preview`

#### Scenario: Alternative model selection
- **WHEN** user needs faster generation with lower quality requirements
- **THEN** the system SHALL offer `gemini-2.5-flash-image` as an alternative option

### Requirement: Gemini Image Size Configuration

The system SHALL support Gemini-style image size configuration using `1K`, `2K`, and `4K` values.

#### Scenario: Image size selection
- **WHEN** user selects an image size for generation
- **THEN** the available options SHALL be `1K` (default), `2K`, and `4K`
- **AND** the size value SHALL use uppercase 'K' as required by Gemini API

#### Scenario: Backend image size handling
- **WHEN** the backend receives an image generation request with `image_size` parameter
- **THEN** it SHALL pass the value directly to the external API
- **AND** it SHALL validate that the value is one of `1K`, `2K`, or `4K`

## MODIFIED Requirements

### Requirement: Model Selection Options

The frontend model selection dropdowns SHALL display only the following models:
- `gemini-3-pro-image-preview` (default, labeled for quality)
- `gemini-2.5-flash-image` (labeled for speed)

The following deprecated models SHALL be removed from the UI:
- `gpt-image-1.5`
- `nano-banana-2-4k`
- `nano-banana-2-2k`
- `nano-banana-2`
- `nano-banana`

#### Scenario: E-commerce image generator model options
- **WHEN** user views the model selection in e-commerce image page
- **THEN** only Gemini models SHALL be available
- **AND** `gemini-3-pro-image-preview` SHALL be pre-selected

#### Scenario: General image generator model options
- **WHEN** user views the model selection in image generation page
- **THEN** only Gemini models SHALL be available
- **AND** `gemini-3-pro-image-preview` SHALL be pre-selected

### Requirement: Image Size Format in General Image Generator

The general image generator page SHALL use Gemini-style size format instead of pixel dimensions.

#### Scenario: Size selection UI update
- **WHEN** user views the image size selector
- **THEN** the options SHALL be `1K`, `2K`, `4K` instead of `256x256`, `512x512`, `1024x1024`
- **AND** `1K` SHALL be the default selection
