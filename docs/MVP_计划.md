# Contex MVP 版本计划 (v0.1)

## 1. 需求评估与合理性分析 (Assessment)

### 1.1 核心特性评估

| 特性 | 评估意见 | 潜在风险与对策 |
| :--- | :--- | :--- |
| **1. 一键安装 (含 Docker)** | **高难度，高价值**。这是 "Zero Terminal" 体验的核心。但在 macOS/Windows 上静默安装 Docker Desktop 极其困难（涉及权限与许可）。 | **对策：** 采用“检测+引导+自动化”策略。若未安装，自动下载安装包并挂载，引导用户完成最后一步授权。应用内集成 Docker Client 库进行状态轮询。 |
| **2. 每日新闻简报 (Search-based)** | **逻辑闭环**。验证了容器内 Agent 的外部网络访问能力、定时任务调度能力及 LLM 总结能力。 | **对策：** 需预置免费搜索工具 (如 DuckDuckGo Lite) 以降低冷启动门槛。需考虑 LLM API Key 的配置流程。 |
| **3. Sidecar 推送桌面提醒** | **架构验证**。验证了 `Container -> Sidecar -> Desktop` 的反向通信链路，比微信小程序更适合作为第一步 MVP。 | **对策：** 采用 Tauri 的 Sidecar 模式，Python 服务通过 `stdout` 或本地 HTTP 回调触发 Tauri 的系统通知 API。 |

### 1.2 结论
MVP 范围界定合理，覆盖了“安装-运行-输出”的完整闭环，且避开了复杂的外部生态（微信）接入，专注于验证核心架构的可行性。

---

## 2. 项目目录结构设计 (Project Structure)

为了保证长期演进的稳定性，采用 **Monorepo** 结构，明确分层：

```text
contex/
├── apps/
│   ├── desktop/           # [L1] Tauri 桌面端 (Client Wrapper)
│   │   ├── src-tauri/     # Rust 后端 (负责进程管理、系统托盘) [Pending]
│   │   └── src/           # React 前端 (仪表盘、配置页)
│   └── sidecar/           # [L2] Python 桥接服务 (MCP Host)
│       ├── api/           # FastAPI 接口定义
│       ├── core/          # 核心逻辑 (权限校验、Docker 客户端)
│       └── requirements.txt
├── packages/
│   ├── brain/             # [L3] 容器构建上下文 (Dockerfile)
│   │   ├── runtime/       # 预置运行时配置 (pip.conf, npmrc)
│   │   └── tools/         # 基础工具链脚本
│   └── skills/            # [Skill] 预置技能包
│       └── daily-brief/   # 新闻简报 Agent (LangGraph 代码)
├── scripts/               # 工程化脚本 (CI/CD, 本地调试启动)
├── docs/                  # 文档
└── README.md
```

**设计亮点：**
*   **解耦：** `apps` 存放宿主机运行的程序，`packages/brain` 存放容器内运行的环境，互不干扰。
*   **扩展性：** 新增 Skill 只需在 `packages/skills` 下添加目录，易于管理。

---

## 3. 用户动线设计 (User Journey)

### 3.1 阶段一：安装与初始化 (Onboarding)
*   **Step 1 (启动):** 用户双击 App，进入“初始化向导”。
*   **Step 2 (环境检查):** 
    *   App 检查 Docker Engine。
    *   *Case A (已安装):* 亮绿灯，进入下一步。
    *   *Case B (未安装):* 提示“正在下载依赖环境”，下载 Docker DMG/EXE，自动打开安装器，通过 UI 轮询检测安装完成状态。
*   **Step 3 (配置):** 用户输入 LLM API Key (支持跳过，使用模拟数据体验)。
*   **Step 4 (就绪):** 自动拉取 `contex-brain` 镜像（显示进度条）。完成后进入 Dashboard。

### 3.2 阶段二：日常使用 (Daily Loop)
*   **Trigger:** 每日 08:00 AM (或用户点击“立即运行”)。
*   **Action:** 
    1.  Tauri 唤醒 Sidecar（如果休眠）。
    2.  Sidecar 启动 Docker 容器内的 `daily-brief` 任务。
    3.  **Container:** 搜索新闻 -> LLM 总结 -> 生成 Markdown。
    4.  **Container:** 调用 Sidecar API `notify_user(content)`。
*   **Feedback:** 
    1.  Sidecar 收到请求，转发给 Tauri。
    2.  电脑右下角弹出系统通知：“今日简报已生成”。
    3.  用户点击通知，Tauri 窗口打开，展示 Markdown 简报内容。

---

## 4. 单元测试与验收策略 (Testing Strategy)

为了保证质量，测试需覆盖关键路径：

| 测试层级 | 测试对象 | 覆盖场景 | 关键指标 |
| :--- | :--- | :--- | :--- |
| **Unit Test** | **Sidecar (Python)** | 测试 `notify_user` 接口能否正确解析请求并触发回调。 | 接口响应 < 100ms |
| **Unit Test** | **Skill (Agent)** | 测试新闻搜索工具在无网/无结果时的异常处理；测试 LLM 的 Prompt 模板输出格式。 | 零崩溃 |
| **E2E Test** | **Install Flow** | 模拟 Docker 未安装、安装中、安装失败的三种状态，验证 UI 引导逻辑（Mock Docker Client）。 | 状态流转无死锁 |
| **Integration** | **Container -> Host** | 验证容器内 `host.docker.internal` 网络连通性及 Sidecar 鉴权逻辑。 | 通信成功率 100% |

---

## 5. 开发计划 (Dev Plan)

*   **Week 1:** 搭建 Monorepo 骨架；实现 Tauri + Sidecar (Python) 的基础通信（Hello World）。
*   **Week 2:** 完成 Docker 镜像构建 (`packages/brain`) 及 Tauri 的 Docker 生命周期管理模块。
*   **Week 3:** 开发 `daily-brief` Skill；实现容器内调用 Sidecar API 发送通知。
*   **Week 4:** 完善“一键安装”引导逻辑（下载与检测）；UI 整合与联调。

---

## 6. 当前进度 (Current Status)

**最后更新时间:** 2026-01-29

| 模块 | 状态 | 说明 |
| :--- | :--- | :--- |
| **Monorepo 架构** | ✅ 已完成 | 包含 Sidecar, Desktop, Brain, Skills 的完整目录结构已就绪。 |
| **Sidecar (Python)** | ✅ 已完成 | 实现了 FastAPI 服务，支持任务触发 (`/run-task`) 和通知回调 (`/notify`)。集成 Mock Docker Client。 |
| **Skill: Daily Brief** | ✅ 已完成 | 实现了基于 DDGS 搜索 + Gemini 2.0 Flash 总结的新闻简报逻辑。解决 SSL/LibreSSL 兼容性问题。 |
| **集成验证** | ✅ 已通过 | `scripts/verify_mvp.py` 验证脚本运行成功。跑通了 Sidecar -> Skill -> Sidecar 通知的完整闭环。 |
| **Docker 支持** | 🚧 模拟中 | 目前使用 Mock Docker Client 验证逻辑，后续需接入真实 Docker API。 |
| **Tauri 前端** | 🚧 开发中 | React 前端框架已初始化 (`apps/desktop`)，Rust 后端 (`src-tauri`) 尚未集成。 |
| **配置管理** | 🚧 开发中 | 支持 API Key 的持久化存储与容器运行时注入。 |
