# Design: Batch Prompt Generation Architecture

## Overview
This document describes the architecture and data flow for the batch prompt generation feature.

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              Frontend (Vue 3)                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────────────┐ │
│  │ Product Library │  │ Reference Input │  │ Prompt Review & Generation  │ │
│  │   Selection     │  │ (Image/Text)    │  │           Panel             │ │
│  └────────┬────────┘  └────────┬────────┘  └─────────────┬───────────────┘ │
│           │                    │                         │                 │
│           └────────────────────┼─────────────────────────┘                 │
│                                │                                            │
│                                ▼                                            │
│                    ┌───────────────────────┐                               │
│                    │   State Management    │                               │
│                    │ (selectedProduct,     │                               │
│                    │  references[],        │                               │
│                    │  generatedPrompts[])  │                               │
│                    └───────────┬───────────┘                               │
│                                │                                            │
└────────────────────────────────┼────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Backend API (FastAPI)                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    POST /api/v1/prompts/generate                     │   │
│  │  Input: { product_id, references: [{type, data}], options }         │   │
│  │  Output: { prompts: GeneratedPrompt[], metadata }                    │   │
│  └──────────────────────────────┬──────────────────────────────────────┘   │
│                                 │                                           │
│                                 ▼                                           │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    Prompt Generation Service                         │   │
│  │  - Reference preprocessing                                           │   │
│  │  - Parallel LLM calls                                                │   │
│  │  - Result aggregation                                                │   │
│  └──────────────────────────────┬──────────────────────────────────────┘   │
│                                 │                                           │
│                                 ▼                                           │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    LLM Client (StructLLM)                            │   │
│  │  - Vision analysis for images                                        │   │
│  │  - Text analysis for descriptions                                    │   │
│  │  - Structured output parsing                                         │   │
│  └──────────────────────────────┬──────────────────────────────────────┘   │
│                                 │                                           │
└─────────────────────────────────┼───────────────────────────────────────────┘
                                  │
                                  ▼
                    ┌─────────────────────────┐
                    │   External LLM API      │
                    │   (Gemini/GPT-4V)       │
                    └─────────────────────────┘
```

## API Design

### Endpoint: Generate Prompts from References

```
POST /api/v1/prompts/generate
Content-Type: multipart/form-data

Parameters:
- product_id: string (required) - ID of selected product from library
- references: File[] (optional) - Reference images
- reference_texts: string[] (optional) - Reference text descriptions
- options: JSON string (optional) - Generation options
  - language: "zh" | "en" (default: "zh")
  - include_product_context: boolean (default: true)
```

**Request Example:**
```
POST /api/v1/prompts/generate
Content-Type: multipart/form-data

product_id: "550e8400-e29b-41d4-a716-446655440000"
references[0]: <image file>
references[1]: <image file>
reference_texts[0]: "高端商务风格产品照，深色背景，专业灯光..."
options: {"language": "zh", "include_product_context": true}
```

**Response:**
```json
{
  "prompts": [
    {
      "id": "prompt-1",
      "scene": "深色大理石桌面",
      "angle": "45度俯拍",
      "lighting": "专业摄影灯",
      "style": "商务高端",
      "composition": "三分法构图",
      "background": "深色渐变",
      "props": ["名片", "钢笔"],
      "mood": "专业商务",
      "fullPrompt": "产品置于深色大理石桌面上，45度俯拍视角，专业摄影灯光，商务高端风格...",
      "confidence": 0.85,
      "sourceType": "image",
      "sourceIndex": 0
    },
    {
      "id": "prompt-2",
      "scene": "白色背景",
      "angle": "正面平拍",
      "lighting": "柔和自然光",
      "style": "简约现代",
      "composition": "居中构图",
      "background": "纯白背景",
      "props": [],
      "mood": "简洁干净",
      "fullPrompt": "产品置于白色背景正中，正面平拍视角，柔和自然光线...",
      "confidence": 0.78,
      "sourceType": "text",
      "sourceIndex": 0
    }
  ],
  "metadata": {
    "total_references": 3,
    "successful_extractions": 2,
    "failed_extractions": 1,
    "processing_time_ms": 2500,
    "product_context_used": true
  }
}
```

## Data Models

### Pydantic Schemas

```python
class ReferenceType(str, Enum):
    IMAGE = "image"
    TEXT = "text"

class GeneratedPrompt(BaseModel):
    id: str
    scene: str
    angle: str
    lighting: str
    style: str
    composition: str
    background: str
    props: List[str] = []
    mood: str
    fullPrompt: str
    confidence: float = Field(ge=0.0, le=1.0)
    sourceType: ReferenceType
    sourceIndex: int

class PromptGenerationRequest(BaseModel):
    product_id: str
    reference_texts: Optional[List[str]] = None
    options: Optional[Dict[str, Any]] = None

class PromptGenerationResponse(BaseModel):
    prompts: List[GeneratedPrompt]
    metadata: Dict[str, Any]
```

## LLM Integration

### Configuration (from `.env`)

LLM settings are read from the project's `.env` file:

```env
API_BASE_URL=https://api.gpt-best.com
API_KEY=your-provider-api-key
LLM_MODEL=openai/gpt-4o-mini
```

The existing `LLMConfig` class in `app/clients/llm_client.py` handles this configuration.

### System Prompt for Vision Analysis
```
你是一个专业的电商产品摄影分析师。请仔细分析提供的参考图片，提取以下摄影元素：

1. 场景(scene): 拍摄场景/背景环境
2. 角度(angle): 拍摄角度
3. 光线(lighting): 光线类型和效果
4. 风格(style): 整体视觉风格
5. 构图(composition): 构图方式
6. 背景(background): 背景处理
7. 道具(props): 场景中的辅助物品
8. 氛围(mood): 整体氛围感受

基于分析结果，生成一个完整的产品摄影提示词。
置信度(confidence)表示你对分析结果的确信程度(0.0-1.0)。
```

### System Prompt for Text Analysis
```
你是一个专业的电商产品摄影提示词生成专家。请分析用户提供的产品描述文本，提取并生成结构化的摄影提示词：

文本中可能包含：
- 产品使用场景描述
- 产品特点和卖点
- 目标用户群体
- 品牌调性

请基于这些信息推断最合适的摄影风格并生成结构化提示词。
```

## Processing Flow

### Sequence Diagram

```
Frontend                    Backend                     LLM API
   │                          │                            │
   │ POST /prompts/generate   │                            │
   │ (product_id, references) │                            │
   │─────────────────────────>│                            │
   │                          │                            │
   │                          │ Validate & preprocess      │
   │                          │───────────────────────>    │
   │                          │                            │
   │                          │ For each reference:        │
   │                          │                            │
   │                          │ ┌──────────────────────┐   │
   │                          │ │ Parallel processing   │   │
   │                          │ │                      │   │
   │                          │ │  Image refs:         │   │
   │                          │ │  - Compress/convert  │   │
   │                          │ │  - Vision analysis   │──>│
   │                          │ │                      │   │
   │                          │ │  Text refs:          │   │
   │                          │ │  - Text analysis     │──>│
   │                          │ │                      │   │
   │                          │ └──────────────────────┘   │
   │                          │                            │
   │                          │<──────────────────────────│
   │                          │                            │
   │                          │ Aggregate results         │
   │                          │ Generate fullPrompts      │
   │                          │                            │
   │<─────────────────────────│                            │
   │ { prompts: [...] }       │                            │
   │                          │                            │
   │ User edits prompts       │                            │
   │                          │                            │
   │ POST /images/generate    │                            │
   │ (product_image, prompt)  │                            │
   │─────────────────────────>│                            │
   │                          │                            │
```

## Frontend State Management

```typescript
interface BatchPromptState {
  // Selected product from library
  selectedProduct: Product | null;
  selectedProductImages: string[];  // IDs of selected product images

  // Reference inputs
  referenceImages: File[];
  referenceTexts: string[];

  // Generated prompts
  generatedPrompts: GeneratedPrompt[];
  selectedPromptIds: string[];

  // UI state
  isGenerating: boolean;
  generationProgress: number;
  generationError: string | null;

  // Edit state
  editingPromptId: string | null;
  editedPrompts: Map<string, Partial<GeneratedPrompt>>;
}
```

## UI Components

### User-Friendly Prompt Display

**Important**: Prompts are displayed in input fields, NOT as raw JSON. Each prompt is rendered as a visual card with labeled form fields.

#### PromptCard Layout (Visual Design)

```
┌─────────────────────────────────────────────────────────────────────┐
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │ 来源: 图片 #1                               置信度: ████ 85% │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                     │
│  场景         ┌─────────────────────────────────────────────────┐  │
│               │ 深色大理石桌面                                   │  │
│               └─────────────────────────────────────────────────┘  │
│                                                                     │
│  拍摄角度     ┌─────────────────────────────────────────────────┐  │
│               │ 45度俯拍                                         │  │
│               └─────────────────────────────────────────────────┘  │
│                                                                     │
│  光线         ┌─────────────────────────────────────────────────┐  │
│               │ 专业摄影灯                                       │  │
│               └─────────────────────────────────────────────────┘  │
│                                                                     │
│  风格         ┌─────────────────────────────────────────────────┐  │
│               │ 商务高端                                         │  │
│               └─────────────────────────────────────────────────┘  │
│                                                                     │
│  构图         ┌─────────────────────────────────────────────────┐  │
│               │ 三分法构图                                       │  │
│               └─────────────────────────────────────────────────┘  │
│                                                                     │
│  背景         ┌─────────────────────────────────────────────────┐  │
│               │ 深色渐变                                         │  │
│               └─────────────────────────────────────────────────┘  │
│                                                                     │
│  道具         ┌─────────────────────────────────────────────────┐  │
│               │ 名片, 钢笔                                       │  │
│               └─────────────────────────────────────────────────┘  │
│                                                                     │
│  氛围         ┌─────────────────────────────────────────────────┐  │
│               │ 专业商务                                         │  │
│               └─────────────────────────────────────────────────┘  │
│                                                                     │
│  ─────────────────────────────────────────────────────────────────  │
│  完整提示词预览:                                                    │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │ 产品置于深色大理石桌面上，45度俯拍视角，专业摄影灯光，      │  │
│  │ 商务高端风格，三分法构图...                                  │  │
│  └─────────────────────────────────────────────────────────────┘  │
│                                                                     │
│  ┌─────────┐  ┌─────────┐                          ☑ 选中生成   │
│  │  编辑   │  │  复制   │                                        │
│  └─────────┘  └─────────┘                                        │
└─────────────────────────────────────────────────────────────────────┘
```

#### Vue Component Structure

```vue
<!-- PromptCard.vue -->
<template>
  <div class="prompt-card" :class="{ selected: isSelected }">
    <!-- Header with source and confidence -->
    <div class="prompt-header">
      <span class="source-badge">
        来源: {{ sourceType === 'image' ? '图片' : '文本' }} #{{ sourceIndex + 1 }}
      </span>
      <div class="confidence-bar">
        置信度: <progress :value="confidence" max="1"></progress> {{ Math.round(confidence * 100) }}%
      </div>
    </div>

    <!-- Editable fields - NOT JSON -->
    <div class="prompt-fields">
      <div class="field-row">
        <label>场景</label>
        <input v-model="editablePrompt.scene" :disabled="!isEditing" />
      </div>
      <div class="field-row">
        <label>拍摄角度</label>
        <input v-model="editablePrompt.angle" :disabled="!isEditing" />
      </div>
      <div class="field-row">
        <label>光线</label>
        <input v-model="editablePrompt.lighting" :disabled="!isEditing" />
      </div>
      <div class="field-row">
        <label>风格</label>
        <input v-model="editablePrompt.style" :disabled="!isEditing" />
      </div>
      <div class="field-row">
        <label>构图</label>
        <input v-model="editablePrompt.composition" :disabled="!isEditing" />
      </div>
      <div class="field-row">
        <label>背景</label>
        <input v-model="editablePrompt.background" :disabled="!isEditing" />
      </div>
      <div class="field-row">
        <label>道具</label>
        <input v-model="propsText" :disabled="!isEditing" placeholder="逗号分隔" />
      </div>
      <div class="field-row">
        <label>氛围</label>
        <input v-model="editablePrompt.mood" :disabled="!isEditing" />
      </div>
    </div>

    <!-- Full prompt preview -->
    <div class="full-prompt-preview">
      <label>完整提示词预览</label>
      <textarea readonly :value="fullPrompt"></textarea>
    </div>

    <!-- Actions -->
    <div class="prompt-actions">
      <button @click="toggleEdit">{{ isEditing ? '保存' : '编辑' }}</button>
      <button @click="copyPrompt">复制</button>
      <label class="select-checkbox">
        <input type="checkbox" v-model="isSelected" />
        选中生成
      </label>
    </div>
  </div>
</template>
```

### Component Tree
```
BatchPromptPage
├── ProductSelector (existing, reuse from ecommerce-image)
│   └── ProductList
│       └── ProductCard
├── ReferenceInputPanel
│   ├── ImageDropzone
│   │   └── ImagePreviewGrid
│   └── TextInputArea
├── GenerateButton
├── PromptResultsPanel
│   ├── PromptCard (x N)
│   │   ├── PromptFields (scene, angle, etc.)
│   │   ├── ConfidenceBadge
│   │   ├── EditButton
│   │   └── SelectCheckbox
│   └── BatchActionBar
│       ├── SelectAllButton
│       └── GenerateImagesButton
└── GenerationProgressModal
    └── ProgressBar
```

## Error Handling

| Error Case | Handling |
|------------|----------|
| No product selected | Disable generate button, show hint |
| No references provided | Disable generate button, show hint |
| LLM API failure for one reference | Continue with others, mark failed |
| All LLM calls fail | Show error, allow retry |
| Invalid image format | Skip image, show warning |
| Image too large | Compress before sending |
| Rate limit exceeded | Queue and retry with backoff |

## Performance Considerations

1. **Parallel Processing**: Process multiple reference images concurrently using `asyncio.gather()`:
   - Max 5 parallel LLM calls to avoid rate limiting
   - Each uploaded image is analyzed independently
   - Results are aggregated and returned together
2. **Image Compression**: Compress images > 2MB before LLM analysis
3. **Caching**: Cache product context to avoid re-fetching
4. **Debouncing**: Debounce text input before processing
5. **Progressive Loading**: Show prompts as they become available

### Parallel Image Processing Flow

```python
async def process_references(references: List[Reference]) -> List[GeneratedPrompt]:
    """Process multiple references in parallel"""
    semaphore = asyncio.Semaphore(5)  # Max 5 concurrent

    async def process_one(ref: Reference, index: int) -> GeneratedPrompt:
        async with semaphore:
            if ref.type == "image":
                return await analyze_image(ref.data, index)
            else:
                return await analyze_text(ref.data, index)

    tasks = [process_one(ref, i) for i, ref in enumerate(references)]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    # Filter out failures
    return [r for r in results if isinstance(r, GeneratedPrompt)]
```

## Security Considerations

1. **Input Validation**: Validate file types, sizes, and content
2. **Rate Limiting**: Limit API calls per user per minute
3. **User Isolation**: Ensure users can only access their own products
4. **Content Filtering**: Consider filtering inappropriate reference images

