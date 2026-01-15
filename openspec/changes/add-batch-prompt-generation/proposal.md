# Proposal: Add Batch Prompt Generation for E-commerce Images

## Change ID
`add-batch-prompt-generation`

## Summary
Add a batch prompt generation workflow that:
1. Uses selected product images from the Product Library as objects (subjects)
2. Allows users to upload reference objects (images or text descriptions) that LLM analyzes to reverse-engineer prompts
3. Generates structured prompts using StructLLM with user-editable output
4. Supports batch input of reference objects for batch prompt generation
5. Enables users to select/edit prompts and iterate through them for product image generation

## Background

### Current State
- **Product Library (Module 1)**: Fully implemented. Users can upload product images with AI-powered attribute recognition (name, dimensions, features, characteristics)
- **E-commerce Image Generation**: Wizard-based workflow where users select products, configure templates (scene, angle, style, target), and generate prompts for image generation
- **LLM Integration**: StructLLM client exists for structured output parsing with Gemini/GPT-4V vision models

### Problem Statement
Current workflow requires manual prompt composition. Users need:
- A way to use reference images/text to automatically generate prompts
- Batch processing capability to create multiple prompts efficiently
- Ability to review, select, and edit generated prompts before image generation

## Proposed Solution

### Workflow Overview
```
Product Library Image   +   Reference Objects    →    LLM Analysis    →    Structured Prompts
    (subject)               (image/text)              (reverse-engineer)     (batch output)
         ↓                                                                          ↓
                                              User Selection & Editing
                                                         ↓
                                              Product Image Generation
                                              (iterate through prompts)
```

### Key Features

#### 1. Reference Object Input
- **Image Upload**: Users can upload multiple reference images simultaneously (e.g., existing product photos, competitor images, inspiration images)
- **Parallel Processing**: All uploaded images are analyzed concurrently by LLM
- **Text Input**: Users can paste raw text descriptions (e.g., product descriptions from e-commerce listings)
- **Batch Support**: Multiple reference objects can be input and processed at once

#### 2. LLM-Powered Prompt Extraction
- Vision model analyzes reference images to extract style, scene, lighting, and composition details
- Text analysis extracts key descriptive elements
- StructLLM constrains output to a defined prompt schema

#### 3. Structured Prompt Output Schema
```typescript
interface GeneratedPrompt {
  id: string;
  scene: string;           // e.g., "木质桌面"
  angle: string;           // e.g., "45度俯拍"
  lighting: string;        // e.g., "自然光"
  style: string;           // e.g., "简约现代"
  composition: string;     // e.g., "居中构图"
  background: string;      // e.g., "浅色渐变背景"
  props: string[];         // e.g., ["绿植", "咖啡杯"]
  mood: string;            // e.g., "温馨生活"
  fullPrompt: string;      // Combined prompt text
  confidence: number;      // 0.0-1.0
  sourceType: 'image' | 'text';
  sourceIndex: number;
}
```

#### 4. User-Friendly Prompt Display
- **Editable Input Fields**: Each prompt field (scene, angle, style, etc.) displayed as labeled input field
- **No Raw JSON**: Structured data presented in form layout, not JSON format
- **Visual Cards**: Each generated prompt displayed as a card with clear field labels
- **Inline Editing**: Click any field to edit directly
- **Confidence Indicator**: Visual badge showing AI confidence level

#### 5. Prompt Review & Selection UI
- Display generated prompts in a selectable list/grid
- Allow multi-selection for batch generation
- Inline editing for each prompt field
- Preview of how the prompt will be composed

#### 5. Product Image Generation Loop
- For each selected prompt, combine with product subject image
- Generate product images using existing image generation API
- Track progress for batch operations

## Non-Goals (Out of Scope)
- Real-time prompt generation during image upload (deferred for later)
- Prompt template persistence/saving (can be added later)
- Multi-product batch generation in single session

## Dependencies
- Existing Product Library module and API
- LLM client (StructLLM) using `.env` configuration:
  - `API_BASE_URL`: LLM API endpoint
  - `API_KEY`: API authentication key
  - `LLM_MODEL`: Model identifier (e.g., `openai/gpt-4o-mini`)
- Image generation API (Gemini image models)

## Affected Components
- **Backend**: New API endpoints for prompt generation
- **Frontend**: New page or wizard step for batch prompt workflow
- **Database**: Optional - prompt history storage

## Risks & Mitigations
| Risk | Mitigation |
|------|------------|
| LLM prompt extraction quality varies | Allow manual editing of all generated fields |
| Long processing time for batch | Show progress indicators, process in parallel where possible |
| Rate limiting on LLM API | Implement backoff and queue management |

## Success Metrics
- Users can generate 5+ prompts from reference objects in under 30 seconds
- At least 70% of generated prompts require minimal editing
- Batch generation completes without user intervention

## Related Documents
- `design.md` - Architectural details and data flow
- `tasks.md` - Implementation task breakdown
- `specs/batch-prompt-generation/spec.md` - Detailed requirements
