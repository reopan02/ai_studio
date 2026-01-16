// @vitest-environment jsdom
import { mount } from "@vue/test-utils";
import { describe, it, expect, vi } from "vitest";

const mockQuery = {
  select: () => mockQuery,
  order: () => mockQuery,
  range: () => Promise.resolve({ data: [], error: null, count: 0 }),
  eq: () => mockQuery,
  single: () => Promise.resolve({ data: null, error: null }),
  in: () => Promise.resolve({ data: [], error: null }),
  then: (resolve: (value: unknown) => unknown) =>
    Promise.resolve({ data: [], error: null, count: 0 }).then(resolve),
};

vi.mock("@/shared/supabase", () => ({
  apiFetch: vi.fn(),
  getUserId: vi.fn(),
  supabase: {
    from: () => mockQuery,
  },
}));

import ToolboxPage from "../toolbox-page.vue";

describe("toolbox-page", () => {
  it("renders header and disabled generate button by default", () => {
    const wrapper = mount(ToolboxPage);
    expect(wrapper.text()).toContain("工具箱");

    const generateButton = wrapper.get("[data-test=generate-button]");
    expect(generateButton.attributes("disabled")).toBeDefined();
  });
});
