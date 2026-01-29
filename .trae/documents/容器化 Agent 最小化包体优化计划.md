# 优化容器化 Agent 最小化包体方案

## 1. 环境清理 (Cleanup)
- **目标**: 释放存储空间，为新构建做准备。
- **操作**: 执行 `docker rmi` 清理旧版 `contex-brain` 镜像及相关悬空镜像。

## 2. 依赖标准化 (Standardization)
- **目标**: 将硬编码在 Dockerfile 中的依赖移至标准配置文件。
- **操作**: 创建 `packages/brain/requirements.txt`，包含以下核心依赖：
  - `requests`
  - `duckduckgo-search`
  - `langgraph`
  - `langchain`
  - `supervisor`
  - `playwright`
  - `google-generativeai`

## 3. 进程管理配置 (Configuration)
- **目标**: 使用 Supervisor 接管容器进程，确保服务稳定性。
- **操作**: 创建 `packages/brain/supervisord.conf`，配置以下服务：
  - `code-server`: IDE 后端服务 (端口 8080)。
  - (可选) `agent-ready`: 一个简单的占位进程或日志输出，表明容器已就绪。

## 4. Dockerfile 重构 (Optimization)
- **目标**: 实施 "Debian Slim 多阶段构建" 方案。
- **操作**: 重写 `packages/brain/Dockerfile`：
  - **Base Image**: `debian:bookworm-slim`。
  - **Build Stage**: 安装编译工具，pip install 依赖，下载 code-server。
  - **Runtime Stage**:
    - 仅安装运行时系统库 (`git`, `supervisor`, `chromium`, `procps`)。
    - 复制 Python 环境和 Code Server。
    - 配置 `PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1` 和 `PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH` 复用系统 Chromium。
  - **Entrypoint**: `CMD ["supervisord", "-c", "/etc/supervisord.conf"]`。

## 5. 构建与验证 (Verification)
- **目标**: 验证镜像体积是否达标 (~400MB) 及功能是否正常。
- **操作**:
  - 执行 `docker build`。
  - 检查镜像大小 (`docker images`)。
  - 启动容器并验证 `git`, `python`, `supervisor`, `playwright` (连接系统 Chrome) 是否工作正常。
