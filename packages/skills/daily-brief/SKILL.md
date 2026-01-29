---
name: daily-brief
description: Automatically fetch latest news for specified topics, evaluate quality using AI, and generate a daily summary.
input_schema:
  type: object
  properties:
    topics:
      type: array
      items:
        type: string
      description: List of topics to search for (e.g., ["AI", "Rust"])
    language:
      type: string
      enum: ["中文", "English"]
      default: "中文"
    max_results:
      type: integer
      default: 3
  required: ["topics"]
---

# Daily Brief Skill

This skill runs a LangGraph workflow to:
1. **Search**: Fetch news from DuckDuckGo.
2. **Filter**: Remove previously processed URLs (Persistence Check).
3. **Evaluate**: Use Gemini Flash to score articles based on relevance and information density.
4. **Dedup**: Remove semantic duplicates.
5. **Summarize**: Generate a Markdown summary.
6. **Notify**: Send the result to Sidecar.

## Usage

This skill is intended to be run as a containerized task via Contex Sidecar.
