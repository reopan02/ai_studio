# 营销内容规划能力规格

## Overview
本能力基于已选定的营销策略路线生成 8 张图的内容规划，形成完整的 AIDA 销售叙事。

## ADDED Requirements

### Requirement: 内容规划输入
系统 SHALL 接收阶段一选定的策略路线与可选参考文案，并基于该路线生成内容规划。

#### Scenario: 路线选择前置
- **WHEN** 用户未选择策略路线
- **THEN** 系统拒绝生成并提示先完成阶段一

#### Scenario: 参考文案可选
- **WHEN** 用户未提供参考文案
- **THEN** 系统使用 AIDA 结构自动生成叙事

### Requirement: 8 张图结构与顺序
系统 SHALL 输出恰好 8 个 items，并满足固定 ID、类型、比例与顺序约束。

#### Scenario: 固定结构输出
- **WHEN** 阶段二生成成功
- **THEN** items 数组长度为 8 且顺序为 main_white → main_lifestyle → hook → problem → solution → features → trust → cta
- **AND** id 依次为 img_1_white, img_2_lifestyle, img_3_hook, img_4_problem, img_5_solution, img_6_features, img_7_trust, img_8_cta
- **AND** type 仅为 main_white / main_lifestyle / story_slide
 
### Requirement: 叙事连贯与 AIDA 对齐
系统 SHALL 确保 6 张长图符合 AIDA 逻辑，并在文案中体现前后衔接。

#### Scenario: 连贯叙事
- **WHEN** 生成 Hook/Problem/Solution/Features/Trust/CTA 六张图
- **THEN** 标题与内文体现 Attention→Interest→Desire→Action 的顺序
- **AND** 每张图的文案或构图摘要体现与上一张/下一张的衔接

### Requirement: 视觉一致性继承
系统 SHALL 继承阶段一路线的色彩方案、字体风格与视觉元素，并在全部 8 张图中保持一致。

#### Scenario: 统一视觉风格
- **WHEN** 基于某条路线生成内容规划
- **THEN** 各图的视觉摘要与提示词体现同一色彩系统与风格描述

### Requirement: 视觉提示词规则
系统 SHALL 为每个 item 生成英文提示词并满足格式与文字渲染要求。

#### Scenario: Prompt 格式约束
- **WHEN** 生成任意一张图的 `visual_prompt_en`
- **THEN** 1:1 图包含 "Square composition, 1:1 aspect ratio"
- **AND** 3:4 图包含 "Vertical composition, 3:4 aspect ratio, mobile screen layout"
- **AND** Prompt 开头明确产品主色/辅色
- **AND** 使用 "Render text" 或 "Display text" 明确渲染 `title_zh` 与 `copy_zh` 的简体中文内容
- **AND** CTA 图包含按钮文字

### Requirement: 文案与字数约束
系统 SHALL 输出符合字数范围的中文标题/内文/构图摘要，并提供企划名称。

#### Scenario: 字数与字段完整
- **WHEN** 阶段二生成成功
- **THEN** `plan_name` 为 10-30 字
- **AND** 每个 `title_zh` 为 10-15 字
- **AND** 每个 `copy_zh` 为 30-50 字
- **AND** 每个 `visual_summary_zh` 为 20-30 字
- **AND** `visual_prompt_en` 为 100-200 字

### Requirement: 输出结构校验
系统 SHALL 在 items 数量、顺序或字段缺失时返回可读错误。

#### Scenario: 输出结构不正确
- **WHEN** items 数量不足或顺序错误
- **THEN** 系统返回错误并提示可重试
