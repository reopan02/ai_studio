# 营销视觉策略生成能力规格

## Overview
本能力用于基于“产品图 + 产品信息”生成产品分析、三条差异化营销视觉路线，以及每条路线三张海报级提示词。

## ADDED Requirements

### Requirement: 策略生成输入
系统 SHALL 接收产品图（必填，JPEG/PNG）以及可选的产品名称、卖点/功能描述，并在缺少产品图时拒绝生成。

#### Scenario: 正常输入
- **WHEN** 用户提供 JPEG/PNG 产品图并提交阶段一
- **THEN** 系统进入策略生成流程

#### Scenario: 缺少产品图
- **WHEN** 用户未提供产品图
- **THEN** 系统返回错误并提示产品图必填

### Requirement: 产品分析输出
系统 SHALL 输出 `product_analysis`，包含名称、英文视觉描述与中文卖点，并满足字数约束。

#### Scenario: 输出字段完整
- **WHEN** 阶段一生成成功
- **THEN** `product_analysis.name` 与输入的产品名称一致（若提供）
- **AND** `product_analysis.visual_description` 为 50-100 字中文描述
- **AND** `product_analysis.key_features_zh` 为 50-150 字中文卖点

### Requirement: 三条差异化路线
系统 SHALL 生成恰好 3 条策略路线，每条路线包含指定字段且满足字数约束，并在至少三个维度上彼此差异化。

#### Scenario: 路线数量与字段
- **WHEN** 阶段一生成成功
- **THEN** `marketing_routes` 数组长度为 3
- **AND** 每条路线包含 `route_name`、`headline_zh`、`subhead_zh`、`style_brief_zh`、`target_audience_zh`、`visual_elements_zh`
- **AND** `route_name` 为 2-10 字，`headline_zh` 为 5-20 字，`subhead_zh` 为 10-30 字

#### Scenario: 路线差异化
- **WHEN** 三条路线生成完成
- **THEN** 任意两条路线在以下维度中至少三个存在差异：目标客群、诉求、视觉风格、情感调性

### Requirement: 海报提示词规则
系统 SHALL 为每条路线生成 3 个海报级英文提示词，并包含中文摘要与关键格式要求。

#### Scenario: 提示词结构与质量
- **WHEN** 路线生成成功
- **THEN** 每条路线的 `image_prompts` 恰好包含 3 个元素
- **AND** 每个 `prompt_en` 以 "A stunning professional advertising poster layout..." 开头
- **AND** `prompt_en` 包含产品锚点（产品名称与核心特征）
- **AND** `prompt_en` 明确写出产品主色与辅色（来源于产品图视觉分析）
- **AND** `prompt_en` 含文字渲染指示（标题位置、字体风格、文字内容）
- **AND** `prompt_en` 描述构图、光影、材质与氛围
- **AND** `prompt_en` 长度为 100-200 字
- **AND** `summary_zh` 为 30-50 字中文摘要

### Requirement: 文案语言规则
系统 SHALL 在简体中文模式下输出中文营销文案，仅在产品名称为英文时允许保留该英文名称。

#### Scenario: 中文文案默认
- **WHEN** 产品名称为中文或未提供英文品牌元素
- **THEN** `headline_zh`、`subhead_zh` 与 `summary_zh` 均为简体中文

### Requirement: 输出结构校验
系统 SHALL 仅输出符合结构约束的 JSON，并在结构或字数不满足时返回可读错误。

#### Scenario: 结构与字数校验失败
- **WHEN** LLM 输出缺失字段或字数不符合要求
- **THEN** 系统返回错误并提示可重试
