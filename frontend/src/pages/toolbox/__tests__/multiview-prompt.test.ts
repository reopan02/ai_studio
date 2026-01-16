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
