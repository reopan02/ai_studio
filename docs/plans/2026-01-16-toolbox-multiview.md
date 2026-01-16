# Toolbox Multiview Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan.

**Goal:** Add a toolbox entry and page that generates single 2x2 multiview grid images from product library inputs using the existing image edits endpoint.

**Architecture:** Extend the frontend MPA with a new /toolbox entry point and Vue page. Reuse Supabase product data and the image edits API, building a fixed multiview prompt and persisting results to user_images. Add a FastAPI route to serve the new toolbox HTML.

**Tech Stack:** Vue 3 + TypeScript + Vite MPA, FastAPI, Supabase, image edits API.

### Task 1: Backend route for toolbox page

**Files:**
- Modify: `app/main.py`
- Test: `tests/test_toolbox_route.py`

**Step 1: Write the failing test**

```python
from app.main import app

def test_toolbox_route_registered() -> None:
    paths = {route.path for route in app.routes}
    assert "/toolbox" in paths
```

**Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_toolbox_route.py -v`
Expected: FAIL with assertion error for missing /toolbox.

**Step 3: Write minimal implementation**

```python
@app.get("/toolbox")
async def toolbox_page():
    return FileResponse("app/static/toolbox.html")
```

**Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_toolbox_route.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add tests/test_toolbox_route.py app/main.py
git commit -m "feat: add toolbox route"
```

### Task 2: Multiview prompt helper (TDD)

**Files:**
- Create: `frontend/src/pages/toolbox/multiview-prompt.ts`
- Create: `frontend/src/pages/toolbox/__tests__/multiview-prompt.test.ts`
- Modify: `frontend/package.json` (add test script/devDependency if needed)

**Step 1: Write the failing test**

```ts
import { describe, it, expect } from "vitest";
import { buildMultiviewPrompt } from "../multiview-prompt";

describe("buildMultiviewPrompt", () => {
  it("includes product name and grid instructions", () => {
    const prompt = buildMultiviewPrompt("保温杯");
    expect(prompt).toContain("保温杯");
    expect(prompt).toContain("2x2");
    expect(prompt).toContain("白底");
  });
});
```

**Step 2: Run test to verify it fails**

Run: `npm run test`
Expected: FAIL (function not found or test setup missing).

**Step 3: Write minimal implementation**

```ts
export function buildMultiviewPrompt(productName: string): string {
  const name = productName?.trim() || "商品";
  return `${name}，生成单张2x2四宫格白底商品图，四个角度：正面、45度侧面、背面、俯视。纯白背景，柔和棚拍光，产品居中，无道具无文字无水印，边距一致。`;
}
```

**Step 4: Run test to verify it passes**

Run: `npm run test`
Expected: PASS

**Step 5: Commit**

```bash
git add frontend/src/pages/toolbox/multiview-prompt.ts frontend/src/pages/toolbox/__tests__/multiview-prompt.test.ts frontend/package.json
git commit -m "test: add multiview prompt helper"
```

### Task 3: Toolbox MPA and UI wiring

**Files:**
- Create: `frontend/toolbox.html`
- Create: `frontend/src/pages/toolbox/main.ts`
- Create: `frontend/src/pages/toolbox/toolbox-page.vue`
- Modify: `frontend/vite.config.ts`
- Modify: `frontend/src/pages/portal/portal-page.vue`

**Step 1: Write the failing test**

Manual test checklist:
- Portal shows Toolbox card in AI generation section.
- /toolbox loads the toolbox page.
- Product selection and image selection work.
- Generate returns a 2x2 grid image.

**Step 2: Run manual test to verify it fails**

Run: `npm run dev` and navigate to `/toolbox`.
Expected: 404 or missing UI.

**Step 3: Write minimal implementation**

- Add toolbox.html and Vite input entry.
- Implement toolbox-page.vue with settings, product selection, multiview prompt preview, and generate button.
- Reuse product fetching logic from ecommerce image page.
- Call /api/v1/images/edits with selected images, model settings, and multiview prompt.
- Persist results to user_images with source=toolbox-multiview metadata.

**Step 4: Run manual test to verify it passes**

Run: `npm run dev` and verify the checklist above.
Expected: Toolbox page loads, generation succeeds, and results display.

**Step 5: Commit**

```bash
git add frontend/toolbox.html frontend/src/pages/toolbox frontend/vite.config.ts frontend/src/pages/portal/portal-page.vue
git commit -m "feat: add toolbox multiview page"
```

### Task 4: Full validation

**Step 1: Run backend tests**

Run: `python -m pytest`
Expected: PASS (allow existing warnings).

**Step 2: Run frontend typecheck**

Run: `npm run typecheck`
Expected: Baseline errors may persist; confirm no new errors introduced.

**Step 3: Commit final adjustments**

```bash
git add -A
git commit -m "chore: finalize toolbox multiview"
```
