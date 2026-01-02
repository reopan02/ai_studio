## ADDED Requirements

### Requirement: Image Generation Page Entry

The system SHALL provide a dedicated Image Generation page accessible from the main portal.

#### Scenario: Portal displays image generation entry

- **WHEN** a user visits the main portal page (`/`)
- **THEN** the system SHALL display a "图像生成" card alongside existing module cards
- **AND** clicking the card SHALL navigate to `/image-generate`

#### Scenario: Image generation page loads successfully

- **WHEN** an authenticated user navigates to `/image-generate`
- **THEN** the system SHALL serve a Vue 3 + TypeScript SPA page
- **AND** the page SHALL display: prompt input, model selection, image settings, and generate button
- **AND** the page SHALL inherit the same visual design system as the Image Edit Studio

### Requirement: Text-to-Image Generation API

The system SHALL provide an API endpoint for text-to-image generation following OpenAI DALL-E format.

#### Scenario: Generate image from text prompt

- **WHEN** a client calls `POST /api/v1/images/generations` with a valid prompt
- **THEN** the system SHALL forward the request to the configured image generation provider
- **AND** the system SHALL return the generated image URL(s)
- **AND** the generation SHALL be recorded in the user's image history

#### Scenario: API request format

- **WHEN** calling the generations endpoint
- **THEN** the request body SHALL accept:
  - `prompt` (string, required): Text description of desired image, max 1000 characters
  - `n` (integer, optional): Number of images to generate, 1-10, default 1
  - `size` (string, optional): Image size, one of "256x256", "512x512", "1024x1024"
  - `model` (string, optional): Model to use for generation
- **AND** the endpoint SHALL accept `X-API-Key` and `X-Base-Url` headers for custom configuration

#### Scenario: API response format

- **WHEN** image generation completes successfully
- **THEN** the response SHALL include:
  - `created` (integer): Unix timestamp
  - `data` (array): Array of objects with `url` field containing image URLs

#### Scenario: Handle generation failure

- **WHEN** image generation fails
- **THEN** the system SHALL return an appropriate HTTP error status
- **AND** the response SHALL include error details

### Requirement: Prompt Input Interface

The system SHALL provide a text input for describing the desired image.

#### Scenario: Display prompt textarea

- **WHEN** the Image Generation page loads
- **THEN** the UI SHALL display a textarea for entering the prompt
- **AND** the textarea SHALL have a placeholder guiding the user
- **AND** a character counter SHALL show current/max characters (0/1000)

#### Scenario: Validate prompt length

- **WHEN** the user enters a prompt exceeding 1000 characters
- **THEN** the UI SHALL prevent further input or truncate
- **AND** the character counter SHALL indicate the limit is reached

### Requirement: Image Count Selection

The system SHALL allow users to specify how many images to generate.

#### Scenario: Display image count selector

- **WHEN** the Image Generation page loads
- **THEN** the UI SHALL display a number selector for image count
- **AND** the selector SHALL allow values from 1 to 10
- **AND** the default value SHALL be 1

#### Scenario: Generate multiple images

- **WHEN** the user selects n > 1 and clicks generate
- **THEN** the system SHALL request n images from the API
- **AND** the UI SHALL display all generated images in a grid

### Requirement: Image Size Selection

The system SHALL allow users to select the output image size.

#### Scenario: Display size selector

- **WHEN** the Image Generation page loads
- **THEN** the UI SHALL display a dropdown or button group for size selection
- **AND** options SHALL include: "256x256", "512x512", "1024x1024"
- **AND** the default SHALL be "1024x1024"

### Requirement: Model Parameter Synchronization

The system SHALL share model and API configuration with the Image Edit Studio.

#### Scenario: Sync API configuration

- **WHEN** the Image Generation page loads
- **THEN** the system SHALL load API Key and Base URL from localStorage
- **AND** the same localStorage keys used by Image Edit Studio SHALL be used
- **AND** changes to configuration SHALL be saved to localStorage

#### Scenario: Model selection options

- **WHEN** the model selector is displayed
- **THEN** available models SHALL match those in Image Edit Studio
- **AND** models SHALL include: gpt-image-1.5, nano-banana-2-4k, nano-banana-2-2k, nano-banana-2, nano-banana

### Requirement: Generation Result Display

The system SHALL display generated images with download capability.

#### Scenario: Display single generated image

- **WHEN** image generation completes with n=1
- **THEN** the UI SHALL display the generated image prominently
- **AND** the image SHALL be clickable to view in full size
- **AND** a download button SHALL be provided

#### Scenario: Display multiple generated images

- **WHEN** image generation completes with n>1
- **THEN** the UI SHALL display all images in a responsive grid
- **AND** each image SHALL be individually downloadable
- **AND** clicking an image SHALL show it in a lightbox/modal

#### Scenario: Generation loading state

- **WHEN** image generation is in progress
- **THEN** the UI SHALL display a loading indicator
- **AND** the generate button SHALL be disabled
- **AND** an optional progress indicator MAY be shown

### Requirement: Generation History

The system SHALL maintain a history of generated images.

#### Scenario: Record generation in history

- **WHEN** image generation completes successfully
- **THEN** the generation SHALL be saved to the user's image history via API
- **AND** the history entry SHALL include: prompt, model, size, timestamp, image URLs

#### Scenario: Display generation history

- **WHEN** the user views the history section
- **THEN** the UI SHALL display recent generations with thumbnails
- **AND** clicking a history item SHALL load its details
- **AND** the user MAY reuse a previous prompt by clicking it

### Requirement: Error Handling

The system SHALL gracefully handle errors during generation.

#### Scenario: Display generation error

- **WHEN** image generation fails
- **THEN** the UI SHALL display an error message with details
- **AND** the user SHALL be able to retry generation
- **AND** the error state SHALL be clearable

#### Scenario: Handle network errors

- **WHEN** a network error occurs during generation
- **THEN** the UI SHALL display a connection error message
- **AND** the generate button SHALL become re-enabled for retry
