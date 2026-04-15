# 集成 Skill · 详细参考（reference）

本文为「集成 skill」的补充说明，包含环境检查、后端/前端/可视化实现要点与常见坑。

---

## 环境检查

- 项目根目录必须存在：`server.py`、`index.html`、`css/`、`demos/`。
- 若缺失，先请用户初始化或由 Agent 创建上述结构。
- 阅读「前端后端架构 skill」确认：
  - 后端路由顺序（`/`、`/api/demo/xxx`、`/<path:path>`），避免静态路由覆盖 API。
  - 端口使用 5001（避免 macOS AirPlay 占 5000 导致 403）。
  - 前端必须通过同一后端地址打开（如 `http://localhost:5001/`），避免 `file://` 导致 fetch 失败。

---

## 后端实现要点

- **只追加**代码，不删除或覆盖已有路由。
- 建议结构：
  1. 配置常量或环境变量（API Key、Secret、业务 URL）。
  2. 鉴权函数（如 `_get_baidu_access_token()`），按「厂商 API 调用 skill」实现。
  3. 业务路由：`@app.route('/api/demo/<unique_name>', methods=['POST'])`。
- 入参：从 `request.files`（上传文件）和 `request.form`（URL、选项等）读取。
- 图片上传且厂商对格式敏感：用 Pillow 转 JPEG 再 base64，减少“图片格式错误”。
- JSON 请求体中的 base64：多数厂商在 JSON 下只需**原始 base64 字符串**，不要 urlencode。
- **异步接口**：先调“创建任务”拿 `task_id`，再循环“获取结果”；轮询返回“处理中”（如百度 `error_code: 1`, `Pending`）时**继续轮询**，不要当错误返回 400。
- 成功：`return jsonify(data)`；业务/厂商错误：`return jsonify(厂商返回), 400`。
- 新增依赖写入 `requirements.txt`。

---

## 前端实现要点

### 前端参数与技术文档

用户会提供 API 技术文档链接（如 `https://ai.baidu.com/ai-doc/OCR/xxx`）。实现时必须：

- **参数名**：与文档中的请求参数名完全一致（如 `language_type`、`detect_direction`、`pdf_file_num`）。
- **可选值**：下拉框、单选框的取值与文档「可选值范围」一致（如 `CHN_ENG`/`ENG`、`true`/`false`）。
- **覆盖**：文档中列出的**所有**请求参数（必选与可选）均需在前端提供对应控件，不得遗漏。
- 可选参数：可提供「默认」或留空选项，用户不选择时不向接口传递，由 API 使用默认值。

### 其他前端要点

- 在 `demos/` 下新建独立 HTML（如 `baidu-essay.html`）。
- 页面需包含：标题与说明、表单（含上述全部参数）、提交按钮、结果区域。
- **防重复硬规则**：新增/修改 `demos/*.html` 后，必须校验 `<!DOCTYPE html>` 在该文件中仅出现 **1 次**；若出现多次，说明发生整页拼接，必须先修复为单页结构。
- 请求使用**相对路径**：`fetch('/api/demo/xxx', { method: 'POST', body: formData })`。
- 提交时：按钮禁用、显示“处理中…”或“正在轮询结果…”。
- 在 `index.html` 侧栏 `#menu-list` 中、`<!-- -->` 注释上方新增：`<a href="demos/新页面.html" target="demo-frame">展示名</a>`。
- 页面需支持滚动：iframe 内 `body { height: 100%; overflow-y: auto }`；可提供“回到顶部”按钮。


### 命名约定（体现厂商）

不同厂商可能提供同名能力（如「智能作业批改」），命名时**统一带厂商**，便于区分：

- **展示名**（侧栏菜单、页面标题/h1）：带厂商前缀，如「百度云 智能作业批改」「腾讯云 某某识别」。
- **文件名**：`demos/<厂商缩写>-<能力简称>.html`，如 `baidu-correct-edu.html`、`tencent-xxx.html`。
- **后端路由**：`/api/demo/<厂商缩写>_<能力简称>`，如 `baidu_correct_edu`，与前端 `fetch` 路径一致。

---

## 可视化要点

- 按「visualization-skill」实现：左侧 JSON 正常显示（含一键复制、一键下载）；右侧按通用原则：理解 JSON 输出结构，结合其中的信息在输入图上进行可视化，将结果放入右侧。

---

## 常见坑

- **Pending 当错误**：百度 get_result 返回 `error_code: 1`, `error_msg: "Pending"` 时表示未完成，应继续轮询，不要返回 400。
- **file:// 无法请求**：必须通过 `http://localhost:5001/` 打开入口，再在 iframe 中打开 demo。
- **端口 5000 返回 403**：多为系统占用，改用 5001。
- **欢迎页显示离线**：欢迎页检测后端时要用相对路径 `fetch('/')`，不要写死 `localhost:5000`。
- **图片格式错误 216201**：JSON 下 image 传原始 base64；或后端用 Pillow 转 JPEG 再提交。

---

作者：kal 修改时间：2026-02-27 17:00（修改时请更新为当前日期时间 YYYY-MM-DD HH:MM）
