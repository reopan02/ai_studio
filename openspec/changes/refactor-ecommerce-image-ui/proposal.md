# Change: Refactor E-Commerce Image Generator UI Flow

## Why
The current e-commerce image page stacks many panels without clear workflow guidance, and prompt preview is a single raw string. Template options are stored by label, which makes editing brittle and can desync selection. The UI copy also contains mojibake and needs cleanup.

## What Changes
- Reorganize the single-page layout into clearer workflow sections (product -> templates -> preview -> generate) while keeping the existing visual style.
- Replace template option state with stable IDs and a refined chip editor (multi-select, inline edit, add/delete).
- Introduce a structured prompt preview with labeled segments, variable highlighting, and copy support.
- Tighten empty states and guidance so each section communicates prerequisites.
- Fix garbled Chinese UI strings across the page.

## Impact
- Affected specs: ecommerce-image-ui (modify requirements).
- Affected code: `frontend/src/pages/ecommerce-image/ecommerce-image-page.vue`, `frontend/src/styles/ecommerce-image.css`.
- No backend or API changes.
