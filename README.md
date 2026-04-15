# API 集成平台（动态版）

将第三方云端 API（以 OCR、文档与教育场景能力为主）封装为**浏览器内可切换的 Demo**：统一入口、左 JSON 右可视化、便于验证与演示。

## 新人先看什么

- **业务背景、价值与使用场景** → 请阅读根目录 **[业务文档.md](./业务文档.md)**  
- **如何接入 / 下架 Demo、厂商调用与可视化约定** → 见 **[skills/](./skills/)** 下各 Skill

## 本地运行

```bash
cd /path/to/集成平台
pip install -r requirements.txt
cp .env.example .env
# 编辑 .env，填入百度云 API Key 与 Secret Key
python server.py
```

浏览器访问终端提示的地址（一般为 `http://127.0.0.1:5000`），从左侧菜单选择 Demo。

### 上传到 GitHub

1. 在 [GitHub](https://github.com) 新建空仓库（不要勾选添加 README，避免首次推送冲突）。
2. 在项目目录执行：

```bash
git init
git add .
git commit -m "Initial commit: API 集成平台"
git branch -M main
git remote add origin https://github.com/<你的用户名>/<仓库名>.git
git push -u origin main
```

**安全说明**：密钥仅放在本地 `.env`，已通过 `.gitignore` 忽略。若仓库曾含明文密钥，请在百度云控制台**轮换/作废旧密钥**后再公开仓库。

## 配置说明

| 变量 | 说明 |
|------|------|
| `BAIDU_ESSAY_API_KEY` | 百度云应用 API Key |
| `BAIDU_ESSAY_SECRET_KEY` | 百度云应用 Secret Key |

也可不设 `.env`，直接在终端用 `export BAIDU_ESSAY_API_KEY=...` 等方式注入环境变量。

## 仓库结构（简要）

| 路径 | 说明 |
|------|------|
| `server.py` | 后端入口与 API |
| `index.html` / `css/` | 前端入口与样式 |
| `demos/` | 各 Demo 页面 |
| `skills/` | 架构、集成、厂商、可视化、删除等规范文档 |
