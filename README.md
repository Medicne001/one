SmartWealth Agent Demo (MCP + LangGraph + Skills + Agent)
========================================================

概述
----
这是一个最小可运行的 demo，演示以智能体为核心的编排：
- MCP (Management Control Plane) - 技能注册、下发 policy、审计
- LangGraph - 图式流程执行器（按节点顺序调用技能）
- Skills - demo skills: risk_calc, allocate, pdf_export（在启动时会向 MCP 注册）
- Agent - orchestration worker：拉取策略、调用 LangGraph 执行、合并结果并上报审计
- Frontend - 简单静态页面，一键触发 demo

目录结构
----------
- docker-compose.yml
- mcp/
- langgraph/
- skills/
- agent/
- backend/
- frontend/

快速运行
--------
1. 复制 .env.example 为 .env，并（可选）填入 OPENAI_API_KEY：
   cp .env.example .env
   # 编辑 .env 填入你的 OpenAI Key（可选）

2. 启动：
   docker-compose up --build

3. 打开演示页面：
   http://localhost:3000

4. 点击 "Run Demo"。前端会调用 agent 的 /run_demo，agent 会：
   - 从 MCP 获取 demo graph
   - 解析技能注册信息（从 MCP /skills）
   - 调用 LangGraph 执行 graph（顺序执行 skill-runner 的 risk_calc -> allocate -> pdf_export）
   - 尝试调用 OpenAI（若配置）生成自然语言解释
   - 将执行证据上报到 MCP /audit
   - 返回结果给前端，前端会在新窗口打开生成的 plan HTML（示意 PDF）

演示台词（面试时使用）
---------------------
1) 开场（15s）
"我准备了一个以智能体为核心的 demo，包含治理层 MCP、graph-based orchestrator（LangGraph）、独立技能容器与 agent worker。接下来我用一个典型场景演示：用户想在 5 年内买房，agent 会按策略触发风险评估、资产分配并生成可导出的计划。"

2) 演示（60-90s）
- 点击 Run Demo
- 讲解流程：
  - "MCP 是治理层，技能在启动时向 MCP 注册；我可以在 MCP 下发不同的 graph policy（这里是 demo_policy）。"
  - "Agent 拉取 policy，构造 graph 并交给 LangGraph 执行，LangGraph 会按节点顺序调用技能。"
  - 展示前端输出与在新窗口打开的 plan HTML（说明 pdf_export 返回 HTML 作为演示）
  - 强调：执行过程会把 evidence/audit 写回 MCP（用于合规与回溯）

3) 技术深潜（面试问答要点）
- Prompt/模型治理如何做？ -> MCP 管理 prompt/template、模型版本与审计链
- 如何防止 LLM 幻觉？ -> 事实性数据由技能或 RAG 检索返回，LLM 只负责自然语言组织；且在控制平面做校验
- 技能安全如何保证？ -> 技能运行在各自容器/沙箱，输入做白名单校验并且通过 MCP 的能力与权限管理（demo 中简化）
- 扩展性 -> 技能可水平扩展，MCP 可下发更复杂 graph（条件、并行、补偿），LangGraph 可改造成有状态工作流引擎

扩展建议（生产化方向）
-----------------------
- 将 MCP 的注册/审计持久化到 Postgres，并做认证/授权
- LangGraph 增加条件分支、并行、超时和重试策略
- 技能做能力声明与最小权限、并在容器层沙箱化（gVisor 或 K8s pod security）
- Agent 引入任务队列（RabbitMQ/Kafka）与 worker 池
- LLM 使用企业合约或私有部署并做 prompt 管控、模型版本化与成本限制

许可证
-------
示例代码仅作学习/演示用途
