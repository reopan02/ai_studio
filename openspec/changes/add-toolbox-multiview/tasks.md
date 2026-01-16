## 1. Portal entry
- [x] Add a toolbox card to the portal AI generation section and wire it to /toolbox.

## 2. Toolbox page
- [x] Add toolbox MPA entry (toolbox.html, Vite input, main.ts).
- [x] Implement toolbox page layout with model settings, product selection, reference image selection, and result gallery.
- [x] Build multiview prompt generator and request payload for /api/v1/images/edits with global API config.
- [x] Persist generated results to user_images with toolbox metadata.

## 3. Backend route
- [x] Add a /toolbox route to serve app/static/toolbox.html.

## 4. Validation
- [x] Run python -m pytest.
- [x] Run npm run typecheck (document existing baseline errors if still present).
