## Context
电商图生成工具需要根据不同的"生成目标"（主图、详情页、海报等）生成不同风格的图片。当前实现过于简单，仅将目标名称作为提示词的一部分，缺乏针对性的引导。

### 目标用户
- 电商运营人员：需要快速生成不同用途的产品图
- 管理员：需要配置和管理目标类型

### 约束条件
- 保持与现有模板系统的兼容性
- 不改变图片生成 API 的核心逻辑
- 支持多用户环境下的数据共享

## Goals / Non-Goals

### Goals
- 让用户选择目标后获得明确的提示词填写引导
- 管理员可以自定义目标类型及其提示词模板
- 提升生成图片与目标用途的匹配度

### Non-Goals
- 不实现基于目标类型的自动参数调整（如分辨率）
- 不实现目标类型的权限控制

## Decisions

### Decision 1: 数据库模型设计

```sql
CREATE TABLE target_types (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,           -- 目标类型名称，如"主图"
    placeholder TEXT,             -- 输入框占位文本，如"请描述主图的展示重点..."
    default_template TEXT,        -- 默认提示词模板，如"适合电商主图展示的产品图，突出产品整体外观"
    sort_order INTEGER DEFAULT 0, -- 排序顺序
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**初始数据**：
| id | name | placeholder | default_template |
|----|------|-------------|------------------|
| target-main | 主图 | 请描述主图的展示重点，如产品摆放方式、突出的卖点... | 适合电商主图展示的产品图，突出产品整体外观，简洁大方 |
| target-detail | 详情页 | 请描述详情页需要展示的产品细节或使用场景... | 适合详情页的产品展示图，展现产品细节和使用场景 |
| target-poster | 海报 | 请描述海报的主题和风格，如促销活动、节日氛围... | 具有视觉冲击力的营销海报风格，适合活动推广 |
| target-white | 白底图 | 请描述白底图的拍摄角度和展示方式... | 纯白色背景的产品图，适合平台商品展示 |
| target-scene | 场景图 | 请描述期望的使用场景和环境氛围... | 产品在真实使用场景中的展示图，增强代入感 |

### Decision 2: 前端交互流程

```
┌─ 生成目标 ─────────────────────────────────────────────┐
│                                                         │
│  ○ 主图    ○ 详情页    ○ 海报    ○ 白底图    ○ 场景图  │
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │ 请描述主图的展示重点，如产品摆放方式、突出的卖点...│   │
│  │                                                   │   │
│  │ 适合电商主图展示的产品图，突出产品整体外观，简洁大方│   │
│  │ █                                                 │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

**交互逻辑**：
1. 用户点击单选一个目标类型
2. 下方输入框 placeholder 更新为该类型的 `placeholder`
3. 输入框内容自动填充 `default_template`（用户可编辑）
4. 用户输入的内容作为"目标描述"加入提示词

### Decision 3: 提示词生成逻辑

**当前逻辑**（废弃）：
```
产品名，场景：xx，拍摄角度：xx，生成目标：主图
```

**新逻辑**：
```
产品名，场景：xx，拍摄角度：xx，[用户输入的目标描述内容]
```

目标类型名称不再出现在提示词中，取而代之的是用户基于引导填写的具体描述。

### Decision 4: API 设计

```typescript
// GET /api/v1/target-types
interface TargetType {
  id: string;
  name: string;
  placeholder: string;
  default_template: string;
  sort_order: number;
}

// Response
{
  target_types: TargetType[]
}

// POST /api/v1/target-types (Admin only)
interface CreateTargetTypeRequest {
  name: string;
  placeholder?: string;
  default_template?: string;
  sort_order?: number;
}

// PUT /api/v1/target-types/:id (Admin only)
interface UpdateTargetTypeRequest {
  name?: string;
  placeholder?: string;
  default_template?: string;
  sort_order?: number;
}
```

### Decision 5: 管理后台界面

在 Admin 页面新增"目标类型管理"标签页：
- 表格展示所有目标类型
- 支持拖拽排序
- 每行支持编辑/删除操作
- 顶部"添加目标类型"按钮

## Risks / Trade-offs

| 风险 | 缓解措施 |
|------|----------|
| 旧数据兼容 - 用户已保存的模板使用旧格式 | 迁移时保留 localStorage 中的 target 选项，前端做兼容处理 |
| 单选限制 - 用户可能想同时生成多种类型 | 未来可考虑批量生成功能，当前保持简单 |
| 数据库依赖 - 离线无法加载目标类型 | 前端内置默认类型作为 fallback |

## Open Questions
无
