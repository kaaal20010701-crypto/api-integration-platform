# 前端后端架构 Skill · 快速参考（reference）

---

## 路由一览

| 路径 | 方法 | 说明 |
|------|------|------|
| `/` | GET | index.html |
| `/css/style.css` | GET | 样式（经 `/<path:path>`） |
| `/demos/xxx.html` | GET | demo 页（经 `/<path:path>`） |
| `/api/demo/<name>` | POST | Demo 业务接口 |

---

## 文件清单

| 路径 | 角色 |
|------|------|
| server.py | 后端入口、路由、鉴权、厂商调用 |
| requirements.txt | flask, flask-cors, requests, Pillow 等 |
| index.html | 前端入口、侧栏、iframe |
| css/style.css | 布局、侧栏、iframe 样式 |
| demos/welcome.html | 欢迎页 |
| demos/xxx.html | 各 API Demo 页 |

---

## 新增 Demo 时的修改点

1. **server.py**：追加鉴权函数（若新厂商）、追加 `@app.route('/api/demo/xxx', methods=['POST'])` 及实现；必要时在 requirements.txt 增加依赖。
2. **demos/新页面.html**：新建，含表单、提交、结果区与可视化（按「visualization-skill」）。
3. **index.html**：在 `#menu-list` 中、`<!-- -->` 上方增加一条 `<a href="demos/新页面.html" target="demo-frame">展示名</a>`。

---

作者：kal 修改时间：2025-02-12 00:00（修改时请更新为当前日期时间 YYYY-MM-DD HH:MM）
