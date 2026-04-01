import json
from pathlib import Path
from typing import List

from tool import Tool

BASE_DIR = Path(__file__).parent


def load_tools() -> List[Tool]:
    """Load tools from the tools.json file and return a list of Tool instances."""
    with open(BASE_DIR / "tools.json", "r", encoding="utf-8") as f:
        tools_data = json.load(f)
    tools = [Tool.model_validate(t) for t in tools_data]
    return tools


def get_tool_by_name(name: str) -> Tool | None:
    """Get a tool by its name."""
    tools = load_tools()
    for tool in tools:
        if tool.name == name:
            return tool
    return None
