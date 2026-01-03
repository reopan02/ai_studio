# Change: Redesign E-Commerce Image Generator with Wizard UI

## Why
当前电商图生成页面存在以下用户体验问题：
1. **字体过于小** - 按钮、标签、标签片(chips)的字体大小 (12-14px) 在实际使用中难以阅读
2. **排版拥挤** - 模板选项区域标签过于密集，缺乏视觉呼吸空间
3. **操作流程不够清晰** - 虽然有步骤指示器，但用户仍然难以理解完整流程和当前进度
4. **信息层次不够分明** - 所有内容在单页平铺，用户容易迷失

## What Changes
- 采用**向导式分步(Wizard)设计**，将流程拆分为清晰的4个步骤，每步聚焦单一任务
- **增大核心元素字体尺寸**：标签字体从 13px 提升到 15-16px，按钮从 14px 提升到 16px
- **优化模板标签区域**：增大标签尺寸和间距，支持分组收缩，减少视觉拥挤
- 添加**顶部步骤导航条**，显示完整流程和当前进度
- 增加**面板内间距和视觉层次**，提升内容可读性
- 支持**响应式设计**，兼顾大中小屏幕
- 保留现有产品选择和模板系统的功能逻辑，只改变呈现形式

## Impact
- Affected specs: `ecommerce-image-ui` (modify requirements)
- Affected code:
  - `frontend/src/pages/ecommerce-image/ecommerce-image-page.vue`
  - `frontend/src/styles/ecommerce-image.css`
- No backend or API changes
- 与现有 `refactor-ecommerce-image-ui` 提案兼容，可视为在其基础上的进一步优化
