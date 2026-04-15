# 前端后端架构 Skill · 后端（backend）

本文描述集成平台后端（server.py）的架构与约定。

---

## 技术栈

- **Flask** + **flask-cors**：提供 Web 与 CORS。
- **requests**：请求厂商 API。
- **Pillow**（可选）：图片格式转换（如统一转 JPEG）。

---

## 全局与配置

- `ROOT = os.path.dirname(os.path.abspath(__file__))`：项目根目录，用于 `send_from_directory(ROOT, path)`。
- 厂商相关常量（API Key、Secret、Token URL、业务 URL）放在文件顶部，或从环境变量读取。

---

## 路由约定

| 路由 | 方法 | 说明 |
|------|------|------|
| `/` | GET | 返回 `index.html`，作为前端入口（避免 file:// 导致 fetch 失败）。 |
| `/<path:path>` | GET | 静态资源：从 ROOT 下发 path 对应文件（css/、demos/ 等）。**必须最后注册**，避免覆盖 `/api/`。 |
| `/api/demo/<name>` | POST | 各 Demo 的后端接口，接收表单/文件，调用厂商 API，返回 JSON。 |

- 新增 Demo 时**只追加**新路由与函数，不修改已有的 `/` 和 `/<path:path>`。
- **端口**：建议 **5001**（避免 macOS AirPlay 占 5000 导致 403）。

---

## 请求与响应

- Demo 接口从 `request.files`（上传文件）和 `request.form`（URL、选项等）读取参数。
- 成功：`return jsonify(data)`。
- 业务/厂商错误：`return jsonify(厂商返回体), 400`，便于前端展示 `error_msg` 等。

---

作者：kal 修改时间：2025-02-12 00:00（修改时请更新为当前日期时间 YYYY-MM-DD HH:MM）
