---
name: integration-skill
description: 将第三方 API（如百度云作文识别）接入集成平台的完整流程。适用于用户要求“加一个某某厂商的某某 demo”时。
---

# 集成 Skill（接入新 API Demo）

当用户要求将某个厂商的 API 做成集成平台上的 Demo 时，按本 skill 执行。每个 skill 由 **二部分** 组成，本部分为主入口。

## 执行前必读（按顺序）

1. **技术文档**：用户会提供 API 技术文档链接。**必须**根据该文档实现：前端参数名、可选值与文档完全一致，且**覆盖**文档中提到的所有请求参数（必选与可选）。详见 [reference.md](reference.md) § 前端参数与技术文档。
2. **前端后端架构 skill**：了解项目根目录、`server.py` 路由、`index.html` 与 `demos/` 组织方式、端口与滚动约定。
3. **厂商 API 调用 skill**：确认该厂商鉴权方式（如百度 Token）、同步/异步、轮询规则。


## 流程五步

| 步骤 | 内容 | 详见 |
|------|------|------|
| 1 | 环境与架构确认 | [reference.md](reference.md) § 环境检查 |
| 2 | 厂商 API 调用方式 | 阅读「厂商 API 调用 skill」对应厂商 |
| 3 | 后端实现（server.py） | [reference.md](reference.md) § 后端实现 |
| 4 | 前端实现（demos + index） | [reference.md](reference.md) § 前端实现 |
| 5 | 结果展示与可视化 | 阅读「可视化 skill」+ [reference.md](reference.md) § 可视化 |

## 四部分文件说明

| 文件 | 用途 |
|------|------|
| **SKILL.md**（本文件） | 主入口：流程总览、必读 skill、五步索引。 |
| **[reference.md](reference.md)** | 详细说明：环境检查、后端/前端/可视化实现要点、常见坑。 |



---

作者：kal 修改时间：2026-02-27 17:00（修改时请更新为当前日期时间 YYYY-MM-DD HH:MM）
