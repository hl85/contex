# Stage 1 产品化开发执行计划 (Autonomous Mode)

感谢您的确认。已根据您的指示将所有任务调整为**全自主执行**模式。我将连续执行以下阶段，每完成一个阶段会进行自我验证。

## Phase 1: 基础设施层建设 (Infrastructure Layer)
**动作**:
1.  创建 `packages/brain/core` 目录。
2.  实现 `logger.py` (JSON日志), `config.py` (配置加载), `client.py` (Sidecar通信), `workflow.py` (基类)。
3.  更新 `Dockerfile` 以包含核心库。
**自主验证**: 编写并运行 Python 脚本测试 `config` 加载和 `logger` 输出。

## Phase 2: Skill 重构与配置化 (Skill Refactor)
**动作**:
1.  创建 `packages/skills/daily-brief/manifest.json`。
2.  重构 `daily-brief/main.py` 对接 `brain.core`。
**自主验证**: 模拟环境变量运行 Skill 脚本，验证参数读取。

## Phase 3: Sidecar 逻辑升级 (Sidecar Logic)
**动作**:
1.  更新 `apps/sidecar/api`，添加 `GET /skills` 和 `POST /config` 接口。
2.  升级 `docker_client.py`，实现从 `config.json` 读取 `skill_configs` 并注入容器。
**自主验证**: 使用 `curl` 验证接口连通性及配置注入逻辑。

## Phase 4: 桌面端 UI 集成 (Desktop UI)
**动作**:
1.  在 `apps/desktop` 安装 `react-router-dom` 和 `@rjsf/core`。
2.  编写 `Settings` 页面代码，实现动态表单渲染。
3.  修改 `App.tsx` 增加路由导航。
**自主验证**: 检查前端代码编译无误 (Lint Check)。

## Phase 5: 产品化交付 (Productization)
**动作**:
1.  创建 `.github/workflows/release.yml` 配置打包流程。
2.  在前端添加简单的 API Key 检查引导逻辑。
**自主验证**: 验证 Workflow 文件语法正确性。

---
**即刻开始执行 Phase 1。**
