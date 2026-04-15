---
name: vendor-api-skill
description: 记录各云厂商 API 的鉴权方式与调用模式（同步/异步、轮询规则）。供「集成 skill」在接入新厂商或新接口时查阅，确保后端实现符合厂商规范。
---

# 厂商 API 调用 Skill

本 skill 记录各厂商的**鉴权方式**与**调用模式**（同步/异步、轮询）。**集成 skill** 在实现新 Demo 前应先查阅此处。本 skill 由 **四部分** 组成。

## 四部分文件说明

| 文件 | 用途 |
|------|------|
| **SKILL.md**（本文件） | 主入口：厂商列表、使用方式、四部分索引。 |
| **[baidu.md](baidu.md)** | 百度云：鉴权、手写作文识别（异步）接口、轮询约定、图片与 base64 注意点。 |
| **[tencent.md](tencent.md)** | 腾讯云：预留，鉴权与调用方式待补充。 |
| **[reference.md](reference.md)** | 通用约定：异步轮询模板、错误码处理、新增厂商时的书写格式。 |

## 厂商列表

- **百度云**：详见 [baidu.md](baidu.md)。鉴权 Token；作文识别为异步（create_task → 轮询 get_result）。
- **腾讯云**：详见 [tencent.md](tencent.md)。预留。
- 其他厂商：在 [reference.md](reference.md) 中按相同格式补充。

## 使用方式（给集成 skill）

1. 根据用户说的厂商名称找到对应文件（如 baidu.md）。
2. 按该文件实现鉴权与业务请求；若为异步，按“轮询约定”实现，并注意“处理中”状态不要当错误返回。
3. 将 Key/Secret 放在 server.py 或环境变量，依赖写入 requirements.txt。

---

作者：kal 修改时间：2025-02-12 00:00（修改时请更新为当前日期时间 YYYY-MM-DD HH:MM）
