# 提案：新增营销视觉策划（策略路线 + 8 张图规划）

## Change ID
`add-marketing-visual-planning`

## 为什么
现有电商图生成以“场景/角度/风格”模板为主，缺少面向营销传播的策略化策划能力，导致海报级视觉方向与成套内容规划依赖人工。需要一个以“产品”为中心的两阶段生成流程，提升策划效率与一致性。

## 变更内容
- 新增独立“营销策划”两阶段流程：阶段一输出产品分析 + 3 条策略路线 + 每条 3 个海报提示词；阶段二基于选定路线输出 8 张图内容规划。
- 新增后端 API：`POST /api/v1/marketing/strategy` 与 `POST /api/v1/marketing/plan`，使用 StructLLM 严格产出结构化 JSON。
- 新增前端页面 `/marketing-planner`，提供输入、路线选择与内容规划展示。
- 输出严格遵循 `prompt.md` 的结构、数量与字数约束；不引入品牌信息输入与持久化存储。

## 影响范围
- 影响规格：`marketing-visual-strategy`、`marketing-content-plan`
- 影响代码（拟）：`app/api/v1/`、`app/clients/llm_client.py`、`app/core/`、`frontend/src/pages/`、`frontend/src/shared/`
- 数据：本阶段不新增持久化（仅会话态）
