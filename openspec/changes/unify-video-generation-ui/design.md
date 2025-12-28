# Design: Unified Video Generation UI Architecture

## Overview

This document analyzes the image editing page (`images_editing/`) architecture and proposes a unified layout framework for the video generation page (`app/static/`) to ensure consistent user experience across both media generation interfaces.

---

## Part 1: Image Editing Page Architecture Analysis

### 1.1 Layout Structure (Three-Column Design)

```
┌─────────────────────────────────────────────────────────────────────┐
│  HEADER (Logo, Navigation, Quick Actions)                           │
├──────────────┬───────────────────────────────────────┬──────────────┤
│              │                                       │              │
│   SIDEBAR    │           MAIN CONTENT                │   HISTORY   │
│   (Left)     │           (Center)                    │   PANEL     │
│              │                                       │   (Right)   │
│  - Config    │  ┌─────────────────────────────────┐ │              │
│  - Model     │  │       RESULT AREA               │ │  (Slide-in) │
│  - Upload    │  │   (Preview/Loading/Result)      │ │              │
│              │  └─────────────────────────────────┘ │              │
│              │  ┌─────────────────────────────────┐ │              │
│              │  │       PROMPT SECTION            │ │              │
│              │  │   (Input + Actions)             │ │              │
│              │  └─────────────────────────────────┘ │              │
│              │  ┌─────────────────────────────────┐ │              │
│              │  │    INLINE HISTORY               │ │              │
│              │  │   (Collapsible Grid)            │ │              │
│              │  └─────────────────────────────────┘ │              │
└──────────────┴───────────────────────────────────────┴──────────────┘
```

### 1.2 Functional Modules

| Module | Location | Components | Purpose |
|--------|----------|------------|---------|
| **API Config** | Sidebar | API Key, Base URL, Save/Reset | External API configuration |
| **Model Selection** | Sidebar | Search, Dropdown, Aspect Ratio, Size | Model and output parameters |
| **Reference Input** | Sidebar | Dropzone, Preview Grid, Edit Mask | Input media management |
| **Result Display** | Main (Top) | Placeholder, Loading, Result Image | Output preview |
| **Prompt Input** | Main (Middle) | Textarea, Char Count, Generate Button | Creation command |
| **Inline History** | Main (Bottom) | Collapsible Grid, CRUD Actions | Quick access to history |
| **Side History** | Right Panel | Full History List | Complete history view |

### 1.3 User Interaction Flow

```
1. Configure API (Optional)
   └─> Save credentials to localStorage

2. Select Model & Parameters
   └─> Choose model, aspect ratio, quality

3. Upload Reference Images (Optional)
   └─> Drag/drop or select files
   └─> Edit mask if needed

4. Enter Prompt
   └─> Type description
   └─> View char count

5. Generate
   └─> Click Generate button
   └─> View loading state
   └─> See result in main area

6. Post-Generation Actions
   └─> Download, Share, Fullscreen
   └─> Load from history
   └─> Edit history prompt
```

### 1.4 Key UI Patterns

1. **Collapsible Sections**: Config, History sections collapse to save space
2. **Progressive Disclosure**: Advanced options hidden until needed
3. **Immediate Feedback**: Loading states, toast notifications
4. **Contextual Actions**: Action buttons appear on hover
5. **Keyboard Shortcuts**: Ctrl+Z (undo), Ctrl+S (save), Escape (close)

---

## Part 2: Current Video Page Analysis

### 2.1 Current Layout (Single-Column)

```
┌──────────────────────────────────────────────┐
│  HEADER (Back, Title, Storage Link)          │
├──────────────────────────────────────────────┤
│  SETTINGS CARD                               │
│  (API Key, Base URL)                         │
├──────────────────────────────────────────────┤
│  CREATE TASK CARD                            │
│  (Model, Prompt, Parameters, Generate)       │
├──────────────────────────────────────────────┤
│  STATUS CARD                                 │
│  (Task List, Real-time Updates)              │
└──────────────────────────────────────────────┘
```

### 2.2 Key Differences from Image Editor

| Aspect | Image Editor | Video Generator (Current) |
|--------|--------------|---------------------------|
| Layout | 3-column (Sidebar + Main + Panel) | Single column stacked |
| Config | Collapsible sidebar section | Dedicated card |
| Prompt | Bottom of main area | Inside task card |
| Result | Central display area | Task list items |
| History | Inline grid + side panel | Separate storage page |
| Actions | Contextual hover buttons | Task row actions |

---

## Part 3: Unified Architecture Proposal

### 3.1 New Video Page Layout

```
┌─────────────────────────────────────────────────────────────────────┐
│  HEADER (Logo, "Video Generation Studio", History, Settings)        │
├──────────────┬───────────────────────────────────────┬──────────────┤
│              │                                       │              │
│   SIDEBAR    │           MAIN CONTENT                │  TASK/HIST  │
│   (Left)     │           (Center)                    │   PANEL     │
│              │                                       │   (Right)   │
│  - Config    │  ┌─────────────────────────────────┐ │              │
│    (Collaps) │  │       VIDEO PREVIEW AREA        │ │  Task List  │
│              │  │   (Placeholder/Loading/Video)   │ │  + History  │
│  - Model     │  │   [Video Player Controls]       │ │              │
│    Selection │  └─────────────────────────────────┘ │              │
│              │  ┌─────────────────────────────────┐ │              │
│  - Reference │  │       PROMPT SECTION            │ │              │
│    Images    │  │   (Input + Generate Button)     │ │              │
│    (Dropzone)│  └─────────────────────────────────┘ │              │
│              │  ┌─────────────────────────────────┐ │              │
│  - Video     │  │    INLINE GENERATION HISTORY    │ │              │
│    Options   │  │   (Collapsible Video Grid)      │ │              │
│   (Duration, │  └─────────────────────────────────┘ │              │
│    Ratio)    │                                       │              │
└──────────────┴───────────────────────────────────────┴──────────────┘
```

### 3.2 Module Mapping (Image → Video)

| Image Editor Module | Video Generator Equivalent | Notes |
|---------------------|---------------------------|-------|
| API Configuration | API Configuration | Identical structure |
| Model Selection | Model Selection | Add video-specific models |
| Aspect Ratio | Aspect Ratio + Duration | Extended for video |
| Image Size | Resolution/Quality | HD option mapping |
| Reference Images | Reference Images/Frames | Same dropzone pattern |
| Edit Mask | (Optional) Frame Selection | Different modal |
| Prompt Input | Prompt Input | Same component |
| Generate Button | Generate Button | Same style |
| Result Image | Video Player | Enhanced for video |
| Zoom Controls | Playback Controls | Play, pause, seek |
| Download/Share | Download/Share | Same actions |
| Inline History | Inline History | Video thumbnails |
| Side History Panel | Task + History Panel | Combined view |

### 3.3 Interaction Flow Alignment

**Unified Flow:**
```
1. Configure API (Collapsible, same as image editor)
2. Select Model (Sora/Veo/Seedance dropdown, same pattern)
3. Set Video Parameters (Duration, Ratio - mirroring image params)
4. Upload Reference (Same dropzone, same preview grid)
5. Enter Prompt (Same textarea, same char count)
6. Generate (Same button style, same loading pattern)
7. View Result (Video player instead of image)
8. Post-Actions (Download, Share - same pattern)
9. History (Inline grid with video thumbnails)
```

### 3.4 Shared UI Components

```
Reusable Components:
├── Header (Logo, Nav, Quick Actions)
├── Sidebar Container (Collapsible Sections)
├── Config Section (API Key, Base URL, Save/Reset)
├── Model Selector (Search, Dropdown)
├── Dropzone (Drag/Drop Upload)
├── Preview Grid (Thumbnails with actions)
├── Prompt Input (Textarea + Char Count + Status)
├── Generate Button (Primary action button)
├── Result Area (Placeholder, Loading, Content)
├── Inline History (Collapsible Grid)
├── Side Panel (Slide-in panel)
├── Toast Notifications
└── Modals (Preview, Edit, Confirm)
```

---

## Part 4: Styling Unification

### 4.1 CSS Variable Alignment

Both pages should use identical CSS variables:
- Colors: `--bg-primary`, `--bg-secondary`, `--text-primary`, `--accent-color`
- Spacing: `--spacing-sm`, `--spacing-md`, `--spacing-lg`
- Borders: `--border-radius`, `--border-color`
- Shadows: `--shadow-sm`, `--shadow-md`
- Transitions: `--transition-fast`, `--transition-normal`

### 4.2 Component Styling Consistency

| Component | Style Pattern |
|-----------|---------------|
| Buttons | `.btn`, `.btn-primary`, `.btn-secondary`, `.btn-ghost` |
| Inputs | `.form-input`, `.form-select`, `.form-textarea` |
| Cards | `.sidebar-section`, `.card` |
| Dropzone | `.upload-area`, `.drag-over` |
| Grid | `.preview-grid`, `.inline-history-grid` |
| Toast | `.toast`, `.toast-success`, `.toast-error` |

---

## Part 5: Implementation Strategy

### Phase 1: Layout Restructure
- Convert single-column to sidebar + main layout
- Move config to collapsible sidebar section
- Create central video preview area

### Phase 2: Component Migration
- Extract shared styles to common CSS
- Implement unified sidebar pattern
- Add inline history section

### Phase 3: Interaction Enhancement
- Add keyboard shortcuts
- Implement collapsible sections
- Add hover action patterns

### Phase 4: Polish
- Unified animations
- Responsive breakpoints
- Accessibility improvements

---

## Appendix: File References

- Image Editor HTML: `images_editing/index.html`
- Image Editor CSS: `images_editing/styles.css`
- Image Editor JS: `images_editing/app.js`
- Video Dashboard HTML: `app/static/index.html`
- Video Dashboard CSS: `app/static/style.css`
- Video Dashboard JS: `app/static/script.js`
