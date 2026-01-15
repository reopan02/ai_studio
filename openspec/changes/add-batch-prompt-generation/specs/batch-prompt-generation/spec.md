# Batch Prompt Generation Capability Specification

## Overview

This specification defines the Batch Prompt Generation capability, which enables users to generate structured prompts from reference objects (images or text) for e-commerce product image generation.

---

## ADDED Requirements

### Requirement: Reference Object Input
Users shall be able to input reference objects that serve as inspiration for prompt generation.

#### Scenario: User uploads reference images
**Given** user has selected a product from the Product Library
**When** user uploads one or more reference images
**Then** the images are displayed in a preview grid
**And** each image can be individually removed
**And** the system accepts JPEG and PNG formats up to 10MB each

#### Scenario: User enters reference text
**Given** user has selected a product from the Product Library
**When** user enters text in the reference text area
**Then** the text is stored for prompt generation
**And** the text area supports multi-line input

#### Scenario: User provides multiple references
**Given** user has selected a product
**When** user provides multiple reference images AND/OR text entries
**Then** each reference is processed independently
**And** each reference generates at least one prompt

#### Scenario: Parallel processing of multiple images
**Given** user has uploaded multiple reference images (e.g., 5 images)
**When** prompt generation is triggered
**Then** all images are analyzed concurrently by LLM
**And** processing time is significantly less than sequential processing
**And** results are aggregated and returned together

---

### Requirement: LLM Configuration
The system shall use LLM settings from the project's `.env` file.

#### Scenario: LLM client initialization
**Given** the backend server starts
**When** the LLM client is initialized
**Then** it reads `API_BASE_URL` from `.env`
**And** it reads `API_KEY` from `.env`
**And** it reads `LLM_MODEL` from `.env`
**And** uses these settings for all LLM calls

---

### Requirement: LLM-Powered Prompt Extraction
The system shall use LLM vision and text analysis to extract structured prompt components from references.

#### Scenario: Vision analysis of reference image
**Given** user has provided a reference image
**When** prompt generation is triggered
**Then** the LLM analyzes the image for photography elements
**And** extracts: scene, angle, lighting, style, composition, background, props, mood
**And** assigns a confidence score (0.0-1.0)

#### Scenario: Text analysis of reference description
**Given** user has provided reference text
**When** prompt generation is triggered
**Then** the LLM analyzes the text for descriptive elements
**And** generates structured prompt fields
**And** assigns a confidence score (0.0-1.0)

#### Scenario: Product context integration
**Given** user has selected a product with attributes
**And** user has provided references
**When** prompt generation is triggered
**Then** the LLM considers product name, dimensions, features, and characteristics
**And** generates prompts appropriate for the product type

---

### Requirement: Structured Prompt Output
Generated prompts shall follow a consistent structured format.

#### Scenario: Prompt structure
**Given** LLM has analyzed a reference
**When** a prompt is generated
**Then** the prompt contains the following fields:
- id: unique identifier
- scene: environment/setting description
- angle: camera angle description
- lighting: lighting setup description
- style: visual style description
- composition: composition approach
- background: background treatment
- props: list of supporting objects
- mood: atmosphere/feeling
- fullPrompt: complete combined prompt text
- confidence: extraction confidence score
- sourceType: "image" or "text"
- sourceIndex: index of source reference

#### Scenario: Full prompt composition
**Given** structured fields have been extracted
**When** fullPrompt is generated
**Then** it combines product context with extracted fields
**And** forms a coherent Chinese prompt suitable for image generation

---

### Requirement: Prompt Review and Selection
Users shall be able to review, select, and manage generated prompts.

#### Scenario: Display generated prompts
**Given** prompts have been generated
**When** user views the results panel
**Then** each prompt is displayed as a card
**And** card shows all structured fields
**And** card shows confidence badge
**And** card shows source indicator

---

### Requirement: User-Friendly Prompt Display
Prompts shall be displayed in a user-friendly format, NOT as raw JSON.

#### Scenario: Form-based field display
**Given** prompts have been generated
**When** user views a prompt card
**Then** each field (scene, angle, lighting, etc.) is displayed as a labeled input field
**And** fields are organized in a clear vertical layout
**And** NO raw JSON is shown to the user

#### Scenario: Editable input fields
**Given** a prompt is displayed
**When** user is in edit mode
**Then** each field is an editable text input
**And** labels are in Chinese (场景, 拍摄角度, 光线, etc.)
**And** props field accepts comma-separated values

#### Scenario: Full prompt preview
**Given** a prompt is displayed
**When** user views the card
**Then** a "完整提示词预览" section shows the combined fullPrompt
**And** this preview updates when fields are edited
**And** the preview is displayed in a read-only textarea

#### Scenario: Confidence visualization
**Given** a prompt has a confidence score
**When** user views the prompt card
**Then** confidence is shown as a progress bar with percentage
**And** visual color indicates quality (green > 70%, yellow 50-70%, red < 50%)

#### Scenario: Select prompts for generation
**Given** prompts are displayed
**When** user clicks a prompt card
**Then** the prompt is selected/deselected
**And** selection state is visually indicated
**And** multiple prompts can be selected

#### Scenario: Select all prompts
**Given** prompts are displayed
**When** user clicks "Select All"
**Then** all prompts are selected
**And** button changes to "Deselect All"

---

### Requirement: Prompt Editing
Users shall be able to edit generated prompts before use.

#### Scenario: Edit prompt fields
**Given** a prompt is displayed
**When** user clicks the edit button
**Then** all fields become editable
**And** user can modify any field
**And** changes are preserved locally

#### Scenario: Update full prompt on edit
**Given** user is editing a prompt
**When** user modifies any field
**Then** fullPrompt is automatically regenerated
**And** updated prompt reflects changes

#### Scenario: Cancel editing
**Given** user is editing a prompt
**When** user clicks cancel or clicks outside
**Then** changes are discarded
**And** original values are restored

---

### Requirement: Batch Image Generation
Users shall be able to generate images using selected prompts.

#### Scenario: Generate images from selected prompts
**Given** one or more prompts are selected
**And** product images are selected
**When** user clicks "Generate Images"
**Then** image generation is triggered for each prompt
**And** product image is used as subject
**And** prompt fullPrompt is used as generation instruction

#### Scenario: Track generation progress
**Given** batch image generation is in progress
**When** user views the progress modal
**Then** progress bar shows completion percentage
**And** current/total count is displayed
**And** user can cancel remaining generations

#### Scenario: Handle generation failures
**Given** batch image generation is in progress
**When** a generation fails
**Then** the failure is logged
**And** other generations continue
**And** failed items are marked in final results

---

### Requirement: Error Handling
The system shall handle errors gracefully throughout the workflow.

#### Scenario: No product selected
**Given** no product is selected
**When** user attempts to generate prompts
**Then** generate button is disabled
**And** hint text explains requirement

#### Scenario: No references provided
**Given** product is selected
**And** no references are provided
**When** user attempts to generate prompts
**Then** generate button is disabled
**And** hint text explains requirement

#### Scenario: LLM extraction failure
**Given** references are provided
**When** LLM fails to extract prompt from one reference
**Then** the failed reference is marked
**And** other references are still processed
**And** partial results are returned

#### Scenario: All extractions fail
**Given** references are provided
**When** all LLM extractions fail
**Then** error message is displayed
**And** user can retry generation
**And** no empty prompts are shown

---

## API Contract

### POST /api/v1/prompts/generate

**Request**: `multipart/form-data`
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| product_id | string | Yes | Product UUID |
| references | File[] | No* | Reference images |
| reference_texts | string[] | No* | Reference text descriptions |
| options | JSON | No | Generation options |

*At least one reference (image or text) must be provided.

**Response**: `200 OK`
```json
{
  "prompts": [GeneratedPrompt],
  "metadata": {
    "total_references": number,
    "successful_extractions": number,
    "failed_extractions": number,
    "processing_time_ms": number
  }
}
```

**Error Responses**:
- `400 Bad Request`: Missing required fields or invalid input
- `404 Not Found`: Product not found or not owned by user
- `422 Unprocessable Entity`: Invalid file format or content
- `500 Internal Server Error`: LLM service failure

---

## Cross-References

- **Product Library**: Provides product context and images
- **LLM Client**: Provides StructLLM integration for structured output
- **Image Generation API**: Consumes generated prompts for image creation
