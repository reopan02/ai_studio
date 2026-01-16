## 1. Portal entry
- [ ] Add a toolbox card to the portal AI generation section and wire it to /toolbox.

## 2. Toolbox page
- [ ] Add toolbox MPA entry (toolbox.html, Vite input, main.ts).
- [ ] Implement toolbox page layout with model settings, product selection, reference image selection, and result gallery.
- [ ] Build multiview prompt generator and request payload for /api/v1/images/edits with global API config.
- [ ] Persist generated results to user_images with toolbox metadata.

## 3. Backend route
- [ ] Add a /toolbox route to serve app/static/toolbox.html.

## 4. Validation
- [ ] Run python -m pytest.
- [ ] Run npm run typecheck (document existing baseline errors if still present).
