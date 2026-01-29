# Stage 1 架构深化与重构计划 (Revised)

根据您的最新指示，我在 `brain.core` 中补充了 **SQLite 持久化存储** 支持，用于历史记录去重和上下文优化。以下是更新后的计划：

## 1. 核心工作流重构 (Workflow Re-engineering)
**目标**: 构建基于 **LangGraph** 的生产级流水线，集成 **SQLite 持久化**、质量评估与去重机制。

*   **引入 `langgraph`**: 在 `brain.core` 中封装标准图模式。
*   **数据持久化 (Storage)**:
    *   **新增 `brain.core.storage`**: 封装 `sqlite3`。
    *   **Schema**: `articles (url PRIMARY KEY, title, published_date, embedding, created_at)`。
    *   **用途**:
        1.  **历史去重**: 检查 URL 是否已在过去 N 天内处理过。
        2.  **内容指纹**: (可选) 存储 Title/Summary 的 Hash 或 Embedding，防止不同 URL 但内容相同的新闻重复推送。
*   **定义标准 State**:
    *   `articles`: `List[Article]`
    *   `config`: 任务配置
    *   `brief`: 最终 Markdown
*   **实现核心 Nodes**:
    *   **`SearchNode`**: 执行搜索。
    *   **`HistoryFilterNode` (新增)**: 查询 SQLite，过滤掉已处理过的 URL/标题。
    *   **`EvaluateNode`**: LLM 评分 (Relevance & Quality)，过滤低分内容。
    *   **`DedupNode`**: 批次内语义去重。
    *   **`SummarizeNode`**: 生成简报。
    *   **`PersistNode` (新增)**: 将成功采纳的文章元数据写入 SQLite。

## 2. Skill 规范一致性设计
**目标**: 对齐 Claude Skill 规范。
*   **目录结构**: 保持 `packages/skills/<name>`。
*   **描述文件**: 新增 `SKILL.md` (包含 Frontmatter)，作为 Skill 的“说明书”和 Prompt 接口。
*   **Manifest**: 保持 `manifest.json` 用于 UI 配置，但在设计上尽量复用 Frontmatter 的字段定义。

## 3. 执行步骤

### Phase 1: Core Storage & Workflow Upgrade
1.  **实现 `brain.core.storage`**: 创建 SQLite 连接管理与 CRUD 接口。
2.  **重写 `brain.core.workflow`**:
    *   定义 `NewsGraph`。
    *   实现 `check_history`, `evaluate`, `deduplicate`, `save_history` 等原子方法。
3.  **更新 Dockerfile**: 确保 SQLite 数据目录 (`/app/data`) 可持久化 (挂载 Volume)。

### Phase 2: Daily Brief Skill Refactor (v2)
1.  **迁移逻辑**: 使用 `NewsGraph` 重写 `main.py`。
2.  **配置评分与去重**: 在 `manifest.json` 中增加 `lookback_days` (历史去重回溯天数) 等配置。
3.  **添加 `SKILL.md`**。

### Phase 3: Verification
1.  **持久化验证**: 运行任务两次，第二次应自动过滤掉第一次已处理的文章。
2.  **质量验证**: 检查评分逻辑是否生效。

---
**即刻开始执行 Phase 1。**
