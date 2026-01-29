# Stage 1 - 每日简报需求架构实现文档 (MVP)

## 1. 目标 (Goal)
Implement a usable MVP with "Daily Brief" skill, featuring a robust architecture and configuration system.
构建一个可用的 MVP，以“每日简报”Skill 为核心，验证容器化 Agent 架构，并在此基础上实现**可配置、可扩展、易维护**的基础设施层，从“Demo”走向“Product”。

## 2. 核心架构升级 (Architecture Upgrade)

为了提升 MVP 的易用性和长期维护性，引入以下架构分层：

### 2.1 基础设施层 (Infrastructure Layer)
在 `packages/brain/` 下新增 `core` 模块，作为所有 Skills 的通用 SDK。

```text
packages/brain/
├── core/               # [新增] 核心 SDK
│   ├── __init__.py
│   ├── logger.py       # 统一的 JSON 日志配置，支持 Sidecar 格式
│   ├── client.py       # 封装与 Sidecar 的通信 (HTTP/MCP)，AI Client 初始化
│   ├── workflow.py     # LangGraph/Workflow 通用封装或 BaseAgent 基类
│   └── config.py       # 统一配置加载器 (Env/JSON)
├── runtime/            # 运行时环境配置
└── Dockerfile          # 统一镜像构建
```

**价值：**
*   **解耦**：业务逻辑 (Skill) 与底层通信/配置逻辑分离。
*   **复用**：一次开发，所有 Skill 受益 (如统一升级 Sidecar 通信协议)。

## 3. 配置管理体系 (Configuration System)

### 3.1 基础设施配置 (Infrastructure Config)
全局系统级配置，由 Sidecar 管理，通过环境变量注入容器。
*   **配置源**：`config.json` (位于宿主机 Sidecar 根目录)。
*   **UI 入口**：Desktop App -> Settings -> Advanced (专家模式)。
*   **关键字段**：
    *   `ai_provider`: (Google/OpenAI/Anthropic)
    *   `ai_api_key`: (加密存储)
    *   `proxy_url`: (解决网络问题)
    *   `log_level`: (DEBUG/INFO)

### 3.2 Skill 策略配置 (Skill Policy)
每个 Skill 独有的业务配置，支持动态渲染 UI。
*   **Manifest 机制**：每个 Skill 包含 `manifest.json`，描述其配置项 Schema。
*   **注入机制**：Sidecar 运行时读取用户配置，通过环境变量 `SKILL_CONFIG` 注入容器。

**Example `manifest.json` for Daily Brief:**
```json
{
  "id": "daily-brief",
  "name": "每日简报",
  "config_schema": {
    "topics": { "type": "array", "label": "关注话题", "default": ["Technology", "AI"] },
    "sources": { "type": "array", "label": "限定来源", "default": [] },
    "dedup_strategy": { "type": "select", "options": ["strict", "semantic"], "default": "semantic" }
  }
}
```

## 4. 每日简报 Skill 设计 (Daily Brief Design)

基于新架构的 Skill 实现逻辑：

1.  **Load Config**: 使用 `brain.core.config` 读取用户关注的 `topics` 和 `sources`。
2.  **Search**: 基于配置调用搜索工具 (DDGS/SerpAPI)。
3.  **Process**:
    *   **Dedup**: 根据配置策略去重。
    *   **Filter**: 过滤掉非目标源内容。
4.  **Summarize**: 使用 `brain.core.client` 获取统一配置的 AI Client 进行总结。
5.  **Notify**: 使用 `brain.core.client` 发送结果给 Sidecar。

## 5. 项目目录结构设计 (Updated Project Structure)

```text
contex/
├── apps/
│   ├── desktop/           # [L1] Tauri Desktop
│   └── sidecar/           # [L2] Python Sidecar (Host)
├── packages/
│   ├── brain/             # [L3] Container Context
│   │   ├── core/          # [New] Infrastructure SDK
│   │   └── Dockerfile
│   └── skills/            # [Skill]
│       └── daily-brief/
│           ├── main.py
│           └── manifest.json # [New] Config Schema
├── docs/
└── README.md
```

## 6. 用户动线设计 (User Journey) - Updated

*   **Step 1 (配置):** 用户在 Desktop App 设置页面，看到根据 `manifest.json` 渲染的“每日简报”设置卡片。
*   **Step 2 (个性化):** 用户修改“关注话题”为 "Rust, Tauri, AI"，点击保存。
*   **Step 3 (运行):** 每日定时或手动触发。
*   **Step 4 (执行):** Sidecar 将配置打包注入容器 -> `daily-brief` 读取配置 -> 抓取特定话题 -> 生成简报。
*   **Step 5 (反馈):** 收到符合个人兴趣的精准简报。

### 3.4 Storage Module (New)
- **Path**: `packages/brain/core/storage.py`
- **Responsibility**: 
  - 提供基于 SQLite 的轻量级持久化存储
  - 记录已处理文章的历史 (URL, Title, Source, Date)
  - 支持文章去重 (Deduplication) 以减少上下文开销
  - 自动管理数据库文件和表结构初始化

### 3.5 Skill Specification (New)
- **Reference**: [Claude MCP Skills](https://code.claude.com/docs/en/skills)
- **Implementation**: 
  - 每个 Skill 目录下包含 `SKILL.md`
  - 使用 YAML Frontmatter 定义 Skill 元数据 (Name, Description, Input Schema)
  - 保持与通用 Skill 规范的一致性，便于未来扩展和兼容

## 4. 开发计划 (Development Plan)

### Phase 1: Core Framework Extraction & Standardization (Refactoring)
- [x] 创建 `packages/brain/core` 目录结构
- [x] 提取 `logger.py` 到 core
- [x] 实现 `Manifest` 解析加载逻辑 (pydantic model)
- [x] 实现 `Workflow` 模块 (基于 LangGraph，包含 Evaluate/Filter/Dedup/Notify 节点)
- [x] 实现 `Storage` 模块 (SQLite 持久化与去重支持)

### Phase 2: "Daily Brief" Skill Refactoring (v2)
- [x] 重组 `daily-brief` 目录结构 (main.py, manifest.yaml, prompt.yaml)
- [x] 更新 `manifest.yaml` 适配新 Core 规范
- [x] 重构 `main.py` 继承/使用 Core Workflow
- [x] 实现标准 `if __name__ == "__main__":` 入口便于测试
- [x] 添加 `SKILL.md` (符合 Claude Skill 规范)

### Phase 3: Docker Environment Standardization
- [x] 更新 `packages/brain/Dockerfile` 包含 Core 路径和依赖 (langgraph, sqlite等)
- [x] 验证本地 Docker 构建和运行

### Phase 4: Sidecar Integration & E2E Testing
- [x] 更新 Sidecar `SkillManager` 适配新目录结构和 Manifest
- [x] 实现 `config.json` 注入逻辑 (Sidecar -> Docker Env)
- [x] E2E 测试: React Frontend 触发 -> Sidecar -> Docker (Daily Brief) -> 结果返回 (Verified via scripts/e2e_test_mvp.py)

## 8. 当前进度 (Current Status)

| 模块 | 状态 | 说明 |
| :--- | :--- | :--- |
| **Monorepo** | ✅ Ready | 基础结构已就绪 |
| **Sidecar** | ✅ Ready | API & Mock Docker Client Ready |
| **Infra (Brain Core)** | ✅ Ready | 核心 SDK 与 Workflow 已实现 |
| **Skill (Daily Brief)** | ✅ Ready | 已适配新架构与 Manifest |
| **Config UI** | ✅ Ready | Settings 页面与 API 已对接 |
