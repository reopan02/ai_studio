## ADDED Requirements

### Requirement: E-Commerce Image Generator Page Entry

The system SHALL provide a dedicated E-Commerce Image Generator page accessible from the main portal.

#### Scenario: Portal displays e-commerce image generator entry

- **WHEN** a user visits the main portal page (`/`)
- **THEN** the system SHALL display a "电商图生成" card alongside existing module cards (视频生成, 存储库, 图像处理, 产品库)
- **AND** clicking the card SHALL navigate to `/ecommerce-image`

#### Scenario: E-commerce image page loads successfully

- **WHEN** an authenticated user navigates to `/ecommerce-image`
- **THEN** the system SHALL serve a Vue 3 + TypeScript SPA page
- **AND** the page SHALL display: product selector, prompt template builder, prompt preview, and generate button
- **AND** the page SHALL inherit the same visual design system as the Image Edit Studio

### Requirement: Product Library Integration

The system SHALL allow users to select products from their Product Library to use as generation source.

#### Scenario: Load and display user products

- **WHEN** the E-Commerce Image Generator page loads
- **THEN** the system SHALL fetch the user's products via `GET /api/v1/products`
- **AND** the UI SHALL display a searchable/filterable list of products with thumbnails and names
- **AND** the list SHALL support pagination if the user has many products

#### Scenario: Select a product for generation

- **WHEN** a user selects a product from the product list
- **THEN** the system SHALL load the product's full details via `GET /api/v1/products/{id}`
- **AND** the UI SHALL auto-populate the product info panel with: name, dimensions, features, characteristics
- **AND** the UI SHALL display all reference images associated with the product

#### Scenario: Edit product info for prompt

- **WHEN** a product is selected
- **THEN** the user SHALL be able to toggle which fields (name, dimensions, features, characteristics) to include in the generated prompt
- **AND** the user SHALL be able to edit field values inline (changes affect prompt only, not the Product Library record)
- **AND** changes SHALL be reflected immediately in the prompt preview

### Requirement: Multi-Image Reference Selection

The system SHALL support selecting multiple reference images from the product for image generation.

#### Scenario: Display product reference images

- **WHEN** a product with multiple images is selected
- **THEN** the UI SHALL display all images associated with the product in a grid
- **AND** each image SHALL be selectable/deselectable via checkbox or click

#### Scenario: Select reference images for generation

- **WHEN** the user selects one or more reference images
- **THEN** the selected images SHALL be included in the generation API call
- **AND** the UI SHALL indicate which images are currently selected
- **AND** at least one image MUST be selected before generation can proceed

### Requirement: Prompt Template System

The system SHALL provide a modular prompt template builder with preset options.

#### Scenario: Display template modules

- **WHEN** the E-Commerce Image Generator page loads
- **THEN** the UI SHALL display template modules for:
  1. Scene selection (场景选择)
  2. Shooting angle (拍摄角度)
  3. Style/Lighting (风格/光影) - marked as optional
  4. Generation target (生成目标: 主图/详情/海报)
- **AND** each module SHALL have preset options that the user can select

#### Scenario: Default template options

- **WHEN** the template modules are displayed
- **THEN** Scene options SHALL include at minimum: "白色背景", "自然光桌面", "户外场景", "纯色背景"
- **AND** Angle options SHALL include at minimum: "正面", "45度侧面", "俯视", "平视"
- **AND** Style/Lighting options SHALL include at minimum: "柔和光影", "自然光", "专业棚拍"
- **AND** Target options SHALL include: "主图", "详情页", "海报"

#### Scenario: Select template options

- **WHEN** a user selects options from template modules
- **THEN** the selections SHALL be immediately reflected in the prompt preview
- **AND** multiple options within a single module MAY be selectable (e.g., combining "白色背景" + "柔和光影")

### Requirement: Template Customization

The system SHALL allow users to customize prompt templates.

#### Scenario: Edit template option text

- **WHEN** a user clicks to edit a preset option
- **THEN** the UI SHALL allow inline editing of the option text
- **AND** edited options SHALL be saved to localStorage for persistence

#### Scenario: Add custom template option

- **WHEN** a user clicks "Add option" in a template module
- **THEN** the UI SHALL add a new editable option field
- **AND** the custom option SHALL be saved to localStorage

#### Scenario: Delete template option

- **WHEN** a user deletes a custom template option
- **THEN** the option SHALL be removed from the UI and localStorage
- **AND** preset options SHALL be restorable via a "Reset to defaults" action

#### Scenario: Persist custom templates

- **WHEN** a user customizes template options
- **THEN** the customizations SHALL be stored in browser localStorage
- **AND** customizations SHALL be restored when the user revisits the page

### Requirement: Real-Time Prompt Preview

The system SHALL display a live preview of the composed prompt.

#### Scenario: Compose prompt from selections

- **WHEN** the user has selected a product and template options
- **THEN** the system SHALL concatenate: product info fields + scene + angle + style + target into a coherent prompt
- **AND** the preview SHALL update in real-time as selections change

#### Scenario: Prompt format

- **WHEN** displaying the composed prompt
- **THEN** the format SHALL be: "[产品名称] [产品特征], [场景描述], [拍摄角度], [风格/光影], [生成目标风格要求]"
- **AND** optional fields that are not selected SHALL be omitted from the prompt

#### Scenario: Copy prompt to clipboard

- **WHEN** the user clicks a "Copy" button next to the prompt preview
- **THEN** the composed prompt SHALL be copied to the system clipboard
- **AND** a success toast notification SHALL be displayed

### Requirement: Image Generation Execution

The system SHALL trigger image generation using the existing image API.

#### Scenario: Generate e-commerce image

- **WHEN** the user clicks the "Generate" button
- **AND** at least one reference image is selected
- **AND** a prompt has been composed
- **THEN** the system SHALL call `POST /api/v1/images` with:
  - `prompt`: the composed prompt text
  - `images`: the selected reference images (as multipart or base64)
  - Model parameters synchronized with Image Edit Studio settings
- **AND** the UI SHALL display a loading state during generation

#### Scenario: Display generation result

- **WHEN** image generation completes successfully
- **THEN** the system SHALL display the generated image in a result preview area
- **AND** the user SHALL be able to download the generated image
- **AND** the generation SHALL be recorded in the user's generation history

#### Scenario: Handle generation failure

- **WHEN** image generation fails
- **THEN** the system SHALL display an error message with failure details
- **AND** the user SHALL be able to retry generation

### Requirement: Model Parameter Synchronization

The system SHALL use model parameters consistent with the Image Edit Studio.

#### Scenario: Sync model settings

- **WHEN** the E-Commerce Image Generator page loads
- **THEN** the system SHALL use the same model selection options as Image Edit Studio (e.g., gpt-image-1.5, nano-banana variants)
- **AND** aspect ratio and size options SHALL match Image Edit Studio
- **AND** saved API configuration (API Key, Base URL) SHALL be shared

### Requirement: Iteration and Reuse

The system SHALL support iterating on generated images.

#### Scenario: Reuse current settings

- **WHEN** an image has been generated
- **THEN** the user SHALL be able to click "Generate Again" to create another image with the same settings
- **AND** all current selections (product, images, template options) SHALL be preserved

#### Scenario: Adjust and regenerate

- **WHEN** an image has been generated
- **THEN** the user SHALL be able to modify template options or product info
- **AND** clicking "Generate" again SHALL use the updated settings
- **AND** the previous result SHALL remain visible until new generation completes
