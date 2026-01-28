# Contex

Contex 是一个本地优先的个人 AI 生产力平台，旨在提供零终端（Zero Terminal）体验。它通过 Client Wrapper (Tauri), Sidecar (Python), Brain Container (Docker) 和 Remote Gateway (WeChat) 四层架构，实现安全、高效的 AI 辅助编程与任务执行。

## 核心架构

项目采用 Monorepo 结构：

- **`apps/desktop`**: 用户界面层。基于 Tauri + React 构建，提供设置管理、日志监控和任务交互界面。
- **`apps/sidecar`**: 核心业务逻辑层。基于 Python (FastAPI) 构建，负责配置管理、Docker 容器调度和 Skill 执行。
- **`packages/brain`**: 执行环境层。包含标准化的 Docker 镜像定义，提供安全的沙箱环境。
- **`packages/skills`**: 技能库。定义了 AI 可执行的具体能力（如 `daily-brief`）。

## 环境要求

- **Node.js**: >= 16
- **Rust**: 最新稳定版 (用于构建 Tauri 应用)
- **Python**: >= 3.9
- **Docker**: 必须安装并运行 (用于执行 Brain 容器)

## 快速开始

### 1. 初始化 Sidecar

```bash
# 创建并激活虚拟环境
python3 -m venv .venv
source .venv/bin/activate

# 安装依赖
pip install -r apps/sidecar/requirements.txt
```

### 2. 运行 Sidecar 服务

```bash
# 在根目录下运行
python apps/sidecar/api/main.py
```

### 3. 运行 Desktop 客户端

```bash
cd apps/desktop
npm install
npm run tauri dev
```

## 开发验证

项目包含自动化验证脚本，用于检查 MVP 功能（配置持久化、环境注入、端到端流程）：

```bash
python scripts/verify_mvp_full.py
```

## 设计原则

- **Zero Terminal**: 尽可能减少用户对命令行的直接操作。
- **Privacy First**: 本地优先，数据存储在用户机器上。
- **MCP Protocol**: 使用 Model Context Protocol 连接容器与宿主机。
- **Remote Control**: (规划中) 支持通过微信生态进行远程控制。

## License

[MIT](LICENSE)
