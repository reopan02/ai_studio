# Change: Unify Video Generation UI with Image Editor Architecture

## Why

The current video generation page (`app/static/index.html`) uses a single-column stacked layout that differs significantly from the image editing page (`images_editing/`). This inconsistency creates cognitive friction for users switching between video and image generation workflows. A unified architecture will:

1. **Reduce learning curve** - Same layout patterns across both media types
2. **Enable code reuse** - Shared CSS components and interaction patterns
3. **Improve efficiency** - Optimized screen real estate with sidebar layout
4. **Enhance discoverability** - Consistent placement of controls and actions

## What Changes

### Layout Restructure
- Convert video page from single-column to sidebar + main content layout
- Add collapsible API configuration section in sidebar
- Move model selection and video parameters to sidebar
- Create central video preview area with dedicated controls
- Add inline generation history section below prompt input
- Implement slide-in task/history panel on right side

### Component Alignment
- Adopt same header structure with logo, navigation, quick actions
- Use identical form input styles, button styles, and card patterns
- Implement same dropzone pattern for reference image uploads
- Mirror prompt input section with character count and status indicator
- Add same inline history grid with CRUD operations

### Interaction Consistency
- Apply same collapsible section pattern with chevron indicators
- Use identical hover-reveal action buttons
- Implement matching keyboard shortcuts (Escape to close, Ctrl+Enter to generate)
- Adopt same toast notification system and modal patterns

## Impact

### Affected Files
- `app/static/index.html` - Major restructure to sidebar layout
- `app/static/style.css` - Import/extend image editor styles
- `app/static/script.js` - Add inline history, collapsible sections

### Affected Specs
- `video-generation-layout` (new capability)

### Breaking Changes
- Visual layout will change significantly
- Users familiar with current layout will need brief adjustment
- No functional breaking changes

### Dependencies
- Requires extracting shared CSS to common file or duplicating styles
- May benefit from prior completion of `add-inline-history-display` pattern
