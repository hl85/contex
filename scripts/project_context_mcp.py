import os
import sys
import json
import logging
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.append(str(PROJECT_ROOT))

# Attempt to import mcp
try:
    from mcp.server.fastmcp import FastMCP
except ImportError:
    print("MCP SDK not found. Please install it: pip install mcp")
    sys.exit(1)

# Initialize MCP Server
mcp = FastMCP("Contex Project Context")

@mcp.tool()
def list_project_skills() -> str:
    """List all available skills in the project and their descriptions."""
    skills_dir = PROJECT_ROOT / "packages/skills"
    result = []
    if skills_dir.exists():
        for skill in skills_dir.iterdir():
            if skill.is_dir():
                manifest = skill / "manifest.json"
                if manifest.exists():
                    try:
                        data = json.loads(manifest.read_text())
                        result.append(f"- {data.get('name', skill.name)} ({skill.name}): {data.get('description', 'No description')}")
                    except Exception as e:
                        result.append(f"- {skill.name}: Error reading manifest ({e})")
    return "\n".join(result)

@mcp.tool()
def read_system_logs(lines: int = 50) -> str:
    """Read the last N lines of the unified system log."""
    log_file = PROJECT_ROOT / "logs/system.log"
    if not log_file.exists():
        return "Log file not found."
    
    try:
        with open(log_file, 'r') as f:
            all_lines = f.readlines()
            return "".join(all_lines[-lines:])
    except Exception as e:
        return f"Error reading logs: {e}"

@mcp.tool()
def get_project_architecture() -> str:
    """Get a high-level overview of the project architecture."""
    return """
    Contex Architecture:
    1. Apps:
       - Desktop (Tauri + React): User Interface.
       - Sidecar (FastAPI): Local backend, manages Docker.
       - Gateway (FastAPI): Remote access point.
    2. Packages:
       - Brain: Core AI logic, LangGraph workflows.
       - Skills: Pluggable capabilities.
    3. Data:
       - Config: config.json (Root)
       - Logs: logs/system.log
    """

if __name__ == "__main__":
    print("Starting Contex MCP Server...", file=sys.stderr)
    mcp.run()
