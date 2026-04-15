---
name: delete-api-platform-skill
description: 删除集成平台中某一 API Demo 的完整流程。先查阅「前端后端架构 skill」确定该 API 的代码位置，然后按步骤删除后端与前端代码。适用于用户要求「删除某某 API」「下架某某 demo」时。
---

# 删除 API 平台 Skill

当用户要求删除集成平台中的某一 API Demo 时，按本 skill 执行。

## 执行前必读

**前端后端架构 skill**：查阅其 SKILL.md 与 reference.md，用于确定该 API 的代码分布在哪些文件中。

---

## 代码分布一览（来自前端后端架构 skill）

| 位置 | 内容 |
|------|------|
| **server.py** | 后端路由 `@app.route('/api/demo/<name>', ...)`、鉴权函数（若该厂商仅此一个 demo 可一并删除）、业务常量（API Key/Secret/URL 等） |
| **demos/xxx.html** | 该 Demo 的独立页面 |
| **index.html** | `#menu-list` 内对应的 `<a href="demos/xxx.html" ...>展示名</a>` 菜单链接 |

---

## 执行约束（防残留 / 防重复）

1. 删除 `demos/xxx.html` 时，必须执行**物理删除**（删除文件本身），不能只删 `index.html` 菜单。
2. 删除完成后，必须做**全仓检索验证**（见下文“步骤 5”），确认路由、菜单、文件都已不存在。
3. 若后续再次集成同名 Demo，创建 `demos/xxx.html` 时必须使用**整文件覆盖写入**，禁止追加写入整页 `<!DOCTYPE html>...`。
4. 若后续发现同一 HTML 出现多个 `<!DOCTYPE html>`，视为未删干净或重建流程异常，必须先修复为单页结构再继续。

---

## 删除流程（五步）

### 步骤 1：确认待删除 Demo 名称

从用户描述中提取：展示名（如「百度云作文识别」）、路由名（如 `baidu_essay_ocr`）、文件名（如 `baidu-essay.html`）。若不确定，在 `server.py` 中搜索 `api/demo/`，在 `index.html` 中搜索 `demos/`。

### 步骤 2：删除后端代码（server.py）

1. **删除路由与处理函数**：找到 `@app.route('/api/demo/<name>', methods=['POST'])` 及其下方的 `def demo_xxx():`，整块删除（注意：该函数可能较长，到下一 `@app.route` 或文件末尾为止）。
2. **评估鉴权与工具函数**：若该 Demo 为某厂商的**唯一**一个接口，可删除该厂商的鉴权函数（如 `_get_baidu_access_token`）及专属常量（API Key、Secret、业务 URL）；若同一厂商还有其它 Demo 使用，则**保留**。
3. **requirements.txt**：若删除该厂商后，某个依赖不再被任何接口使用，可从 requirements.txt 中移除。

### 步骤 3：删除前端 Demo 页

删除 `demos/<name>.html` 文件。例如删除 `demos/baidu-essay.html`。

### 步骤 4：删除菜单链接（index.html）

在 `index.html` 的 `#menu-list` 内，删除指向该 Demo 的 `<a href="demos/xxx.html" target="demo-frame">展示名</a>` 一行。注意保留 `<!-- -->` 注释及 welcome 等其它链接。

### 步骤 5：删除后验证（必须执行）

按以下顺序验证，三项都通过才算“删干净”：

1. **文件级验证**：`demos/xxx.html` 不存在（目录内不可见，且文件读取失败）。
2. **引用级验证**：`index.html` 中不再存在 `demos/xxx.html` 链接。
3. **路由级验证**：`server.py` 中不再存在 `/api/demo/<name>` 与对应处理函数名（如 `demo_xxx`）。

若任一项未通过，回到对应步骤继续删除，直到验证全通过。

---

## 删除检查清单

- [ ] server.py 中已删除对应 `@app.route` 及处理函数
- [ ] 若为厂商唯一 Demo：已删除鉴权函数与专属常量；否则保留
- [ ] 已删除 `demos/xxx.html` 文件
- [ ] index.html 中已删除对应菜单链接
- [ ] 验证通过：`demos/xxx.html` 文件不存在
- [ ] 验证通过：`index.html` 中无 `demos/xxx.html`
- [ ] 验证通过：`server.py` 中无 `/api/demo/<name>` 与 `demo_xxx`

---

## 示例：删除「百度云作文识别」

- 路由名：`baidu_essay_ocr`，文件：`baidu-essay.html`
- server.py：删除 `@app.route('/api/demo/baidu_essay_ocr', ...)` 及 `demo_baidu_essay_ocr` 函数；因仍有「百度云 智能作业批改」，故**保留** `_get_baidu_access_token` 及 BAIDU_* 常量
- demos：删除 `baidu-essay.html`
- index.html：删除 `<a href="demos/baidu-essay.html" target="demo-frame">百度云作文识别</a>`

---

作者：kal 修改时间：2026-02-27 17:00（修改时请更新为当前日期时间 YYYY-MM-DD HH:MM）
