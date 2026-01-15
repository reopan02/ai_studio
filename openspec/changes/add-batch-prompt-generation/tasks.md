# Tasks: Batch Prompt Generation Implementation

## Overview
Implementation tasks for the batch prompt generation feature, ordered for incremental delivery.

---

## Phase 1: Backend Foundation

### Task 1.1: Create Prompt Generation Schemas
**Status**: Pending
**Estimate**: Small
**File**: `app/models/schemas.py`

Add Pydantic schemas for prompt generation:
- `GeneratedPrompt` - Output schema for a single generated prompt
- `PromptGenerationRequest` - Request parameters
- `PromptGenerationResponse` - Full response with prompts and metadata

**Validation**:
- Unit test schema validation

---

### Task 1.2: Create Prompt Generation LLM Prompts
**Status**: Pending
**Estimate**: Small
**File**: `app/clients/llm_client.py`

Add system prompts and helper functions for:
- Vision-based reference image analysis
- Text-based reference analysis
- Full prompt composition from structured fields

**Validation**:
- Manual test with sample images/text

---

### Task 1.3: Create Prompt Generation Service
**Status**: Pending
**Estimate**: Medium
**File**: `app/core/prompt_service.py` (new)

Implement core service logic:
- Reference preprocessing (image compression, text normalization)
- **Parallel LLM call orchestration using `asyncio.gather()`**
- **Process multiple uploaded images concurrently (max 5 parallel)**
- Result aggregation and prompt composition
- Error handling for partial failures

**Validation**:
- Unit tests with mocked LLM client
- Integration test with real LLM
- Verify parallel processing performance

---

### Task 1.4: Create Prompt Generation API Endpoint
**Status**: Pending
**Estimate**: Medium
**File**: `app/api/v1/prompts.py` (new)

Implement `POST /api/v1/prompts/generate`:
- Multipart form handling for images
- Input validation
- Product context lookup
- Call prompt service
- Return structured response

**Validation**:
- API test with curl/Postman
- Integration test

---

### Task 1.5: Register Prompts Router
**Status**: Pending
**Estimate**: Small
**File**: `app/main.py`

- Add prompts router to FastAPI app
- Add `/prompt-studio` page route

**Validation**:
- Endpoint accessible

---

## Phase 2: Frontend - Reference Input

### Task 2.1: Create Reference Input Panel Component
**Status**: Pending
**Estimate**: Medium
**File**: `frontend/src/pages/prompt-studio/components/ReferenceInputPanel.vue` (new)

Component for:
- Image dropzone with drag-and-drop
- Image preview grid with remove buttons
- Text input area with placeholder
- Batch import support

**Validation**:
- Visual test, file upload works

---

### Task 2.2: Create Prompt Studio Page Structure
**Status**: Pending
**Estimate**: Medium
**Files**:
- `frontend/src/pages/prompt-studio/prompt-studio-page.vue` (new)
- `frontend/src/pages/prompt-studio/main.ts` (new)

Main page layout with:
- Product selector (reuse from ecommerce-image)
- Reference input panel
- Generate button
- Results area (placeholder)

**Validation**:
- Page renders, navigation works

---

### Task 2.3: Integrate Product Selector
**Status**: Pending
**Estimate**: Small
**File**: `frontend/src/pages/prompt-studio/prompt-studio-page.vue`

Reuse or adapt product selector from ecommerce-image page:
- Product list with search
- Image selection for selected product
- State management integration

**Validation**:
- Can select product and images

---

## Phase 3: Frontend - Prompt Generation & Display

### Task 3.1: Implement Generate Prompt API Call
**Status**: Pending
**Estimate**: Small
**File**: `frontend/src/pages/prompt-studio/prompt-studio-page.vue`

- Collect references and product context
- Call backend API
- Handle loading/error states
- Store results in state

**Validation**:
- API call works, results displayed

---

### Task 3.2: Create Prompt Card Component (User-Friendly Display)
**Status**: Pending
**Estimate**: Medium
**File**: `frontend/src/pages/prompt-studio/components/PromptCard.vue` (new)

**IMPORTANT**: Display prompts in input fields, NOT as raw JSON.

Component layout:
- **Header**: Source badge (图片 #1 / 文本 #1) + Confidence progress bar with percentage
- **Form fields** (labeled inputs, NOT JSON):
  - 场景 (scene) - text input
  - 拍摄角度 (angle) - text input
  - 光线 (lighting) - text input
  - 风格 (style) - text input
  - 构图 (composition) - text input
  - 背景 (background) - text input
  - 道具 (props) - text input (comma-separated)
  - 氛围 (mood) - text input
- **完整提示词预览**: Read-only textarea showing combined fullPrompt
- **Actions**: 编辑 button, 复制 button, Selection checkbox

**Validation**:
- Visual test: No JSON displayed anywhere
- All fields shown as labeled Chinese inputs
- Confidence bar shows color based on score

---

### Task 3.3: Create Prompt Results Panel
**Status**: Pending
**Estimate**: Medium
**File**: `frontend/src/pages/prompt-studio/prompt-studio-page.vue`

Results area with:
- Grid/list of PromptCards
- Multi-select support
- Empty state handling
- Loading skeleton

**Validation**:
- Results display correctly

---

## Phase 4: Prompt Editing

### Task 4.1: Add Inline Edit Mode to PromptCard
**Status**: Pending
**Estimate**: Medium
**File**: `frontend/src/pages/prompt-studio/components/PromptCard.vue`

- Edit button toggles edit mode
- Editable fields for each prompt attribute
- Save/cancel buttons
- Update fullPrompt on field changes

**Validation**:
- Can edit and save changes

---

### Task 4.2: Add Batch Action Bar
**Status**: Pending
**Estimate**: Small
**File**: `frontend/src/pages/prompt-studio/prompt-studio-page.vue`

Fixed bar at bottom with:
- Selection count display
- Select all / Deselect all buttons
- "Generate Images" button (leads to next phase)

**Validation**:
- Actions work, selection state correct

---

## Phase 5: Image Generation Integration

### Task 5.1: Connect to Image Generation API
**Status**: Pending
**Estimate**: Medium
**File**: `frontend/src/pages/prompt-studio/prompt-studio-page.vue`

- For each selected prompt, call image generation
- Pass product image + prompt
- Track progress for batch
- Display results or link to storage

**Validation**:
- End-to-end workflow works

---

### Task 5.2: Add Generation Progress Modal
**Status**: Pending
**Estimate**: Small
**File**: `frontend/src/pages/prompt-studio/components/GenerationProgressModal.vue` (new)

- Progress bar for batch generation
- Current/total count
- Cancel button
- Error display for failed items

**Validation**:
- Modal shows during generation

---

## Phase 6: Polish & Testing

### Task 6.1: Add Error Handling & Edge Cases
**Status**: Pending
**Estimate**: Small
**Files**: Multiple

- Handle no product selected
- Handle no references
- Handle LLM failures
- Handle large files
- Rate limit feedback

**Validation**:
- All error cases handled gracefully

---

### Task 6.2: Add Loading States & Skeletons
**Status**: Pending
**Estimate**: Small
**Files**: Frontend components

- Skeleton loaders for product list
- Spinner during prompt generation
- Disabled states during loading

**Validation**:
- Visual feedback during all async operations

---

### Task 6.3: Integration Testing
**Status**: Pending
**Estimate**: Medium
**Files**: `tests/`

- End-to-end test: select product → add references → generate prompts → select → generate images
- Test batch with multiple references
- Test partial failure handling

**Validation**:
- All tests pass

---

### Task 6.4: Add Navigation & Page Route
**Status**: Pending
**Estimate**: Small
**Files**:
- `app/main.py`
- `frontend/vite.config.ts`

- Add `/prompt-studio` to backend routes
- Add page entry to Vite MPA config
- Add navigation link from main menu

**Validation**:
- Page accessible from app

---

## Task Dependencies

```
1.1 ─┬─> 1.2 ─> 1.3 ─> 1.4 ─> 1.5
     │
     └──────────────────────────────────> 2.1 ─┬─> 2.2 ─> 2.3
                                               │
                                               └─> 3.1 ─> 3.2 ─> 3.3 ─> 4.1 ─> 4.2
                                                                              │
                                                                              └─> 5.1 ─> 5.2
                                                                                        │
                                                                                        └─> 6.1 ─> 6.2 ─> 6.3 ─> 6.4
```

## Parallel Work Opportunities

- **Phase 1** (Backend) and **Phase 2.1** (Reference Input Component) can proceed in parallel
- **Task 3.2** (PromptCard) can be developed in parallel with **Task 3.1** (API integration)
- **Task 5.2** (Progress Modal) can be developed in parallel with **Task 5.1** (Image generation)

## Milestones

| Milestone | Tasks | Description |
|-----------|-------|-------------|
| M1: Backend Ready | 1.1-1.5 | API endpoint functional |
| M2: Basic UI | 2.1-2.3 | Can input references |
| M3: Prompt Generation | 3.1-3.3 | End-to-end prompt generation |
| M4: Editing | 4.1-4.2 | Full prompt editing workflow |
| M5: Complete | 5.1-6.4 | Full feature complete |
