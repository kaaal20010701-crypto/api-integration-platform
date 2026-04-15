# 厂商 API 调用 Skill · 百度云（Baidu Cloud）

---

## 鉴权（所有百度 AI 开放平台接口通用）

- **方式**：OAuth 2.0 客户端凭证，先获取 `access_token`，再在业务请求中携带。
- **Token 接口**：`GET https://aip.baidubce.com/oauth/2.0/token`
- **参数**（Query）：`grant_type=client_credentials`，`client_id={API_KEY}`，`client_secret={SECRET_KEY}`。
- **响应**：JSON，含 `access_token`、`expires_in`。取 `access_token` 用于后续请求。
- **业务请求**：在业务 URL 后追加 `?access_token={token}`；请求体按具体 API（多为 JSON）。

---

## 手写作文识别（多模态）— 异步接口

- **创建任务**：`POST .../rest/2.0/ocr/v1/handwriting_composition/create_task?access_token={token}`
  - Body：JSON。可选：`image`（base64 字符串，**不要** urlencode）、`url`、`pdf_file`；`recognize_granularity`：`none` / `line` / `word`。
  - 返回：`result.task_id`。
- **获取结果**：`POST .../rest/2.0/ocr/v1/handwriting_composition/get_result?access_token={token}`
  - Body：JSON，`{ "task_id": "xxx" }`。
- **轮询约定**：
  - 建议间隔 **5～10 秒**。
  - **处理中**：`error_code: 1`，`error_msg: "Pending"`，`result.status` 为 `Pending` / `processing`。**继续轮询**，不要返回 400。
  - **成功**：`result.status === "success"`（或 `"Success"`），返回完整 result。
  - **失败**：`result.status === "failed"` 或其他 error_code，可返回 400。

---

## 文档解析（PaddleOCR-VL）— 异步接口

- **创建任务**：`POST https://aip.baidubce.com/rest/2.0/brain/online/v2/paddle-vl-parser/task?access_token={token}`
  - Content-Type：`application/x-www-form-urlencoded`
  - Body：`file_data`（base64）或 `file_url` 二选一；`file_name` 必填；可选 `analysis_chart`、`merge_tables`、`relevel_titles`、`recognize_seal`、`return_span_boxes`（bool）。
  - 返回：`result.task_id`。
- **获取结果**：`POST .../paddle-vl-parser/task/query?access_token={token}`
  - Body：`task_id`。
- **轮询约定**：
  - 建议间隔 **5～10 秒**。
  - **处理中**：`status` 为 `pending` / `processing`，继续轮询。
  - **成功**：`status === "success"`，返回 `markdown_url`、`parse_result_url`（可下载解析 JSON）。
  - **失败**：`status === "failed"`。

---

## 银行卡识别 — 同步接口

- **接口**：`POST https://aip.baidubce.com/rest/2.0/ocr/v1/bankcard?access_token={token}`
- **Content-Type**：`application/x-www-form-urlencoded`
- **Body 参数**：`image` / `url` 二选一；可选 `location`（true/false 返回卡号位置坐标）、`detect_quality`（true/false 质量检测）
- **返回**：同步返回 `result` 含 `bank_card_number`、`valid_date`、`bank_card_type`、`bank_name`、`holder_name`；`location=true` 时含 `bank_card_number_location`；`detect_quality=true` 时含 `card_quality`

---

## 试卷切题识别 — 同步接口

- **接口**：`POST .../rest/2.0/ocr/v1/paper_cut_edu?access_token={token}`
- **Content-Type**：`application/x-www-form-urlencoded`
- **Body 参数**：`image` / `url` / `pdf_file` 三选一；可选 `pdf_file_num`、`language_type`（CHN_ENG/ENG）、`detect_direction`、`words_type`（handprint_mix/handwring_only）、`splice_text`、`enhance`、`only_split`
- **返回**：同步返回 `qus_result_num`、`qus_result`、`qus_figure` 等；`qus_result` 含 `qus_location`（题目四角点坐标）、`qus_type`、`elem_text` 等

---

## 图片格式与 body 注意点

- 文档中“base64 后 urlencode”多指 **form 表单**；用 **JSON** 时，`image` 传**原始 base64 字符串**即可。
- 若返回“图片格式错误”（如 216201），可在后端用 Pillow 将上传图转为 JPEG 再 base64 提交。

---

作者：kal 修改时间：2026-03-12 14:30（修改时请更新为当前日期时间 YYYY-MM-DD HH:MM）
