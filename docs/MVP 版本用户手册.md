# Contex MVP User Manual (Stage 1)

本文档旨在指导用户完成 Contex MVP 版本的安装、配置、启动及验证流程。

## 1. 前置要求 (Prerequisites)

在开始之前，请确保您的开发环境满足以下要求：

*   **操作系统**: macOS (推荐), Linux, 或 Windows (WSL2)
*   **Python**: >= 3.10
*   **Node.js**: >= 18.0 (推荐使用 `npm` 或 `bun`)
*   **Rust**: 最新稳定版 (用于构建 Tauri Desktop)
*   **Google Gemini API Key**: 用于 AI 摘要生成 (必须)

## 2. 环境安装 (Installation)

### 2.1 克隆代码
```bash
git clone <repository-url> contex
cd contex
```

### 2.2 安装 Sidecar & Skill 依赖
由于 MVP 版本默认使用 **Mock Docker** 模式（直接在宿主机运行 Python 脚本），因此需要在宿主机安装 Skill 所需的 Python 库。

```bash
# 建议创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装 Sidecar 依赖
pip install -r apps/sidecar/requirements.txt

# 安装 Skill & Brain Core 运行时依赖 (MVP Mock 模式必需)
pip install duckduckgo-search google-genai langchain langgraph beautifulsoup4 pandas playwright
playwright install chromium
```

### 2.3 安装 Desktop App 依赖
```bash
cd apps/desktop
npm install
# 或者
bun install
```

## 3. 配置 (Configuration)

### 3.1 设置 API Key
出于安全性考虑，建议通过环境变量设置 Google Gemini API Key，而非直接写入配置文件。

**推荐方式**: 在激活虚拟环境后，设置环境变量：
```bash
export GOOGLE_API_KEY="your_actual_api_key_here"
```

**备选方式**: 在项目根目录 (`contex/`) 创建或修改 `config.json` 文件（但请注意：此方式不安全，密钥可能被意外提交）。

**文件路径**: `/path/to/contex/config.json`

```json
{
  "log_level": "INFO"
}
```
> **安全警告**: 切勿将真实的 API 密钥提交到版本控制系统。使用环境变量或 .env 文件，并确保 .env 文件在 .gitignore 中。

## 4. 启动流程 (Startup)

需要同时启动 **Sidecar (后端)** 和 **Desktop App (前端)**。

### 4.1 启动 Sidecar
打开一个新的终端窗口 (Terminal 1)：

```bash
# 确保在项目根目录
cd contex
source venv/bin/activate  # 如果使用了虚拟环境

# 启动 Sidecar 服务 (监听 127.0.0.1:12345)
python3 apps/sidecar/api/main.py
```
*成功标志*: 看到 `Uvicorn running on http://127.0.0.1:12345`。

### 4.2 启动 Desktop App
打开另一个终端窗口 (Terminal 2)：

```bash
cd contex/apps/desktop

# 启动 Tauri 开发模式
npm run tauri dev
```
*成功标志*: 桌面应用窗口弹出，显示 "Contex MVP" 仪表盘。

## 5. 操作与验证 (Usage & Verification)

### 5.1 验证连接状态
1.  查看 Desktop App 右上角的 **状态指示器**。
2.  应显示绿色的 **"Sidecar Connected"**。
    *   如果是红色 "Disconnected"，请检查 Sidecar 是否正常启动。

### 5.2 配置技能 (Skill Configuration)
1.  点击 Dashboard 右上角的 **"Settings"** 按钮。
2.  在左侧列表选择 **"每日简报"**。
3.  在右侧表单中配置：
    *   **关注话题**: 例如输入 "DeepSeek", "SpaceX"。
    *   **简报语言**: 选择 "中文" 或 "English"。
    *   **抓取数量**: 默认为 3。
4.  点击 **"Save Configuration"**，确认出现 "Saved successfully!" 提示。

### 5.3 运行任务 (Run Task)
1.  回到 **Dashboard** (点击左上角 "Back to Dashboard")。
2.  在 "Daily Brief Agent" 卡片中，点击 **"Run Task"** 按钮。
3.  **观察日志控制台 (Log Console)**：
    *   此时 Sidecar 会调用 Python 脚本执行任务。
    *   你应该能看到类似以下的日志流：
        *   `[sidecar.api] Received request to run task: daily-brief`
        *   `[skill.daily-brief] === Starting Daily Brief Agent ===`
        *   `[skill.daily-brief] Searching news for topics...`
        *   `[skill.daily-brief] Workflow executed successfully.`

### 5.4 查看结果
*   目前 MVP 版本的结果通过日志输出。
*   如果配置了有效的 API Key，日志中将包含 "Final Brief Length: ..." 等信息，表明摘要已生成。
*   (后续版本将在 UI 中直接展示生成的 Markdown 简报)

## 6. 常见问题 (FAQ)

**Q: 点击 "Run Task" 后没有任何反应？**
A: 请检查 Sidecar 终端是否有报错。常见原因是 Python 依赖未安装全 (如缺少 `langgraph`)。

**Q: 提示 "Configuration Missing"？**
A: 请确保根目录存在 `config.json` 且包含 `GOOGLE_API_KEY`。修改后重启 Sidecar。

**Q: 搜索结果为空？**
A: 可能是 DuckDuckGo 访问受限，或者关键词无相关新闻。尝试更换关键词 (如 "Apple")。

---
**Enjoy Contex MVP!**
