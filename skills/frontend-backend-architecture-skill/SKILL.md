---
name: frontend-backend-architecture-skill
description: 介绍集成平台（API 集成平台动态版）的前端与后端代码架构、目录结构、路由约定与静态资源方式。供「集成 skill」在接入新 API 时查阅，确保新 demo 符合现有架构。
---

# 前端后端架构 Skill（集成平台代码结构）

本 skill 描述集成平台的前后端分工与约定。**集成 skill** 在接入新 API Demo 前应先阅读本 skill。本 skill 由 **四部分** 组成。

## 四部分文件说明

| 文件 | 用途 |
|------|------|
| **SKILL.md**（本文件） | 主入口：目录结构总览、何时查阅、四部分索引。 |
| **[backend.md](backend.md)** | 后端架构：server.py 技术栈、路由表、请求与响应、端口与 CORS。 |
| **[frontend.md](frontend.md)** | 前端架构：index.html 布局、css/style.css、demos 组织、iframe 与滚动。 |
| **[reference.md](reference.md)** | 快速参考：路由一览、文件清单、新增 Demo 时的修改点汇总。 |

## 项目根目录结构

```
集成平台/
├── server.py          # 后端入口，Flask 应用
├── requirements.txt   # Python 依赖
├── index.html         # 前端入口，左侧菜单 + 右侧 iframe
├── css/
│   └── style.css     # 全局样式
└── demos/
    ├── welcome.html   # 欢迎页
    └── xxx.html       # 各 API Demo 页
```

- 后端逻辑集中在 `server.py`；前端入口为 `index.html`，各 demo 为 `demos/` 下独立 HTML，通过 iframe 加载。

## 何时查阅

- 接入新 Demo 前：读本 skill 的 [backend.md](backend.md) 与 [frontend.md](frontend.md)，再改代码。
- 需要快速查路由或修改点：读 [reference.md](reference.md)。

---

作者：kal 修改时间：2025-02-12 00:00（修改时请更新为当前日期时间 YYYY-MM-DD HH:MM）
