# Change: Enhance Target Prompt Template System

## Why
当前"生成目标"模块存在以下问题：
1. **提示词生成不智能** - 直接将目标名称（如"主图"）拼接到提示词中，缺乏引导性描述
2. **无法自定义目标类型** - 目标选项硬编码在前端，用户无法添加/管理自定义类型
3. **缺乏提示词模板关联** - 每个目标类型没有对应的提示词引导模板，用户不知道应该填写什么

## What Changes

### 1. 后端 - 目标类型管理 API
新增数据模型和 API：
- `target_types` 表：存储目标类型（id, name, placeholder, default_template, sort_order）
- `GET /api/v1/target-types` - 获取目标类型列表
- `POST /api/v1/target-types` - 创建目标类型（管理员）
- `PUT /api/v1/target-types/:id` - 更新目标类型（管理员）
- `DELETE /api/v1/target-types/:id` - 删除目标类型（管理员）

### 2. 前端 - 智能提示词填充
改变"生成目标"模块的交互逻辑：
- **单选改造** - 目标类型从多选改为单选
- **动态 placeholder** - 选择目标后，提示词输入框显示对应的引导占位文本
- **默认模板填充** - 选择目标时自动填充默认提示词模板，用户可编辑
- **分离显示** - 目标名称不再直接拼接到提示词，而是作为独立的"生成用途"字段传递

### 3. 管理后台 - 目标类型配置界面
在 Admin 页面新增目标类型管理：
- 可视化界面创建/编辑/删除目标类型
- 为每个类型配置：名称、占位提示、默认模板

## Impact
- Affected code:
  - 后端：新增 `app/models/target_type.py`、`app/api/v1/target_types.py`
  - 前端：修改 `frontend/src/pages/ecommerce-image/ecommerce-image-page.vue`
  - 前端：修改 `frontend/src/legacy/admin-legacy.ts`
- 数据库：新增 `target_types` 表
- 需要数据迁移脚本初始化默认目标类型
