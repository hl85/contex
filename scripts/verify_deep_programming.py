import os
import sys
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent

def check_file(path: Path, description: str) -> bool:
    if path.exists():
        print(f"✅ {description} found: {path.relative_to(PROJECT_ROOT)}")
        return True
    else:
        print(f"❌ {description} MISSING: {path.relative_to(PROJECT_ROOT)}")
        return False

def check_skills():
    print("\n--- Checking Skills ---")
    skills_dir = PROJECT_ROOT / "packages/skills"
    if not skills_dir.exists():
        print(f"❌ Skills directory missing: {skills_dir}")
        return

    for skill in skills_dir.iterdir():
        if skill.is_dir() and not skill.name.startswith("__"):
            print(f"Checking skill: {skill.name}")
            check_file(skill / "SKILL.md", "MCP Documentation (SKILL.md)")
            check_file(skill / "manifest.json", "UI Manifest (manifest.json)")
            check_file(skill / "main.py", "Entry point (main.py)")

def check_config():
    print("\n--- Checking Configuration ---")
    check_file(PROJECT_ROOT / ".trae/project_rules.md", "Trae Project Rules (.trae/project_rules.md)")
    check_file(PROJECT_ROOT / ".trae/mcp.json", "Trae MCP Config (.trae/mcp.json)")
    check_file(PROJECT_ROOT / "config.json", "Global Config (config.json)")

def main():
    print("🔍 Starting Deep Programming Environment Verification...\n")
    check_config()
    check_skills()
    print("\nVerification Complete.")

if __name__ == "__main__":
    main()
