# 前端后端架构 Skill · 前端（frontend）

本文描述集成平台前端的结构：入口页、样式、demo 页与 iframe。

---

## 入口：index.html

- **布局**：左侧固定宽度侧栏（`#sidebar`）+ 右侧 iframe（`#demo-frame`）。
- **侧栏**：`#menu-list` 内为链接列表，每条 `href="demos/xxx.html"`，`target="demo-frame"`，在 iframe 中打开。
- **新增 Demo**：在 `<!-- -->` 注释上方增加：`<a href="demos/新页面.html" target="demo-frame">展示名</a>`。

---

## 全局样式：css/style.css

- `html, body`：`height: 100%`，`overflow: hidden`，整页不滚动。
- `#sidebar`：固定宽度、`max-height: 100vh`、`overflow-y: auto`，菜单多时可滚动。
- `#demo-frame`：`flex: 1`，`height: 100vh`，承载 demo 页。

---

## Demo 页（demos/*.html）

- **独立页面**：每个 demo 是完整 HTML，可引用 `../css/style.css`。
- **运行方式**：必须通过**同一后端**打开（如 `http://localhost:5001/`），再点侧栏进入 demo，这样 `fetch('/api/demo/xxx')` 同源，不会因 `file://` 导致 “Failed to fetch”。
- **滚动**：iframe 内内容过长时，在 demo 页内实现滚动。推荐：`html { overflow: hidden }`，`body { height: 100%; overflow-y: auto }`，body 为滚动容器。
- **请求**：使用相对路径 `fetch('/api/demo/xxx', …)`，不写死 `localhost:5000` 或端口。

---

作者：kal 修改时间：2025-02-12 00:00（修改时请更新为当前日期时间 YYYY-MM-DD HH:MM）
