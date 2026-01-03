## MODIFIED Requirements

### Requirement: Portal Homepage Layout
The system SHALL provide a categorized portal homepage with grouped feature entries.

#### Scenario: Page title and branding
- **WHEN** an authenticated user navigates to the portal homepage `/`
- **THEN** the page title SHALL display as "AI 创作工作室"
- **AND** the subtitle SHALL display as "请选择功能模块"
- **AND** all UI text SHALL be in Chinese

#### Scenario: Feature grouping
- **WHEN** the portal homepage is displayed
- **THEN** feature cards SHALL be organized into three groups:
  - "AI 生成" group containing: AI 视频, AI 图像, 电商图片
  - "资产管理" group containing: 产品素材库, 生成记录, 图像编辑
  - "系统设置" group containing: 管理后台 (admin only)
- **AND** each group SHALL have a visible section title with decorative styling
- **AND** groups SHALL be visually separated with appropriate spacing

#### Scenario: Card layout and sizing
- **WHEN** the portal homepage is displayed on a screen ≥1200px wide
- **THEN** cards SHALL display in a grid with maximum 3 cards per row
- **AND** each card SHALL have a minimum width of 360px
- **AND** cards SHALL have generous padding (≥48px)
- **WHEN** the screen is 768-1199px wide
- **THEN** cards SHALL display with maximum 2 cards per row
- **WHEN** the screen is <768px wide
- **THEN** cards SHALL display in a single column

### Requirement: Visual Impact Icons
The system SHALL display gradient-filled icons for each feature card.

#### Scenario: Gradient icon rendering
- **WHEN** feature cards are displayed
- **THEN** each card icon SHALL use a unique two-color gradient fill
- **AND** the icon size SHALL be at least 80px
- **AND** gradients SHALL be implemented using SVG linearGradient definitions

#### Scenario: Icon color assignments
- **WHEN** the AI 视频 card is displayed
- **THEN** its icon SHALL use a purple-to-blue gradient (#8B5CF6 to #3B82F6)
- **WHEN** the AI 图像 card is displayed
- **THEN** its icon SHALL use a blue-to-cyan gradient (#3B82F6 to #06B6D4)
- **WHEN** the 电商图片 card is displayed
- **THEN** its icon SHALL use an orange-to-pink gradient (#F97316 to #EC4899)
- **WHEN** the 产品素材库 card is displayed
- **THEN** its icon SHALL use a green-to-cyan gradient (#10B981 to #06B6D4)
- **WHEN** the 生成记录 card is displayed
- **THEN** its icon SHALL use a blue-to-purple gradient (#3B82F6 to #8B5CF6)
- **WHEN** the 图像编辑 card is displayed
- **THEN** its icon SHALL use a pink-to-purple gradient (#EC4899 to #8B5CF6)
- **WHEN** the 管理后台 card is displayed
- **THEN** its icon SHALL use a gray-to-blue gradient (#64748B to #3B82F6)

### Requirement: Feature Card Naming
The system SHALL use consistent Chinese naming for all feature cards.

#### Scenario: Card titles and descriptions
- **WHEN** the portal homepage is displayed
- **THEN** cards SHALL display with the following titles and descriptions:
  - "AI 视频" with description "Sora、Veo、Seedance 等模型"
  - "AI 图像" with description "文字描述生成图像"
  - "电商图片" with description "基于产品素材快速生成"
  - "产品素材库" with description "产品图片识别与管理"
  - "生成记录" with description "查看历史生成内容"
  - "图像编辑" with description "多图参考编辑 (Gemini)"
  - "管理后台" with description "用户管理与系统统计"

### Requirement: Card Hover Effects
The system SHALL provide visual feedback when users hover over feature cards.

#### Scenario: Hover state
- **WHEN** a user hovers over a feature card
- **THEN** the card SHALL lift slightly (translateY)
- **AND** the card SHALL display enhanced shadow
- **AND** optionally display a subtle gradient background tint matching the icon colors
