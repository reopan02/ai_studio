# Change: Add toolbox entry with multiview generation

## Why
Users need a dedicated toolbox entry to generate white-background multiview product grids from the product library, with configurable concurrency and image settings.

## What Changes
- Add a new toolbox page with a multiview generation module that reads product names/images and calls Gemini via the existing image edits endpoint.
- Add a toolbox card to the portal AI generation section that links to the new page.
- Add a backend route to serve the toolbox HTML entry point.

## Impact
- Affected specs: toolbox
- Affected code: frontend portal page, new toolbox MPA page, Vite inputs, FastAPI static routes
