# Change: Add Inline Generation History Display Below Prompt Input

## Why
The current Generation History is only accessible via a side panel that users must explicitly open. This creates friction when users want to quickly reuse or reference previous generations. An inline display below the prompt input provides immediate visual context and easier access to CRUD operations for managing generation history.

## What Changes
- Add collapsible Generation History section directly below the prompt input area in the image editing page
- Display recent generations (default 5-10 visible, expandable) with thumbnail previews
- Enable full CRUD operations: view details, delete entries, edit prompts, and load prompts back into the input field
- Maintain existing side panel functionality for backward compatibility
- Sync state between inline display and side panel
- Persist all operations to localStorage

## Impact
- Affected specs: `image-editor-history` (new capability)
- Affected code:
  - `images_editing/index.html`: Add inline history HTML structure below prompt section
  - `images_editing/app.js`: Add inline history rendering and CRUD event handlers
  - `images_editing/styles.css`: Add styles for inline history display
- No breaking changes to existing functionality
