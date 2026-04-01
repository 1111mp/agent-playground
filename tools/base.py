import httpx

from .file import read_file, write_file

SERVER_BASE_URL = "http://localhost:8000"


def attempt_completion(result: str = "") -> str:
    """标记任务完成，并返回最终结果给用户"""
    if result:
        return result
    return "任务已完成。"


LOCAL_TOOLS_MAP = {
    "read_file": read_file,
    "write_to_file": write_file,
    "attempt_completion": attempt_completion,
}
LOCAL_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Request to read the contents of a file at the specified path. Use this when you need to examine the contents of an existing file you do not know the contents of, for example to analyze code, review text files, or extract information from configuration files. Automatically extracts raw text from PDF and DOCX files. May not be suitable for other types of binary files, as it returns the raw content as a string. Do NOT use this tool to list the contents of a directory. Only use this tool on files.",
            "strict": False,
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "The path of the file to read (relative to the current working directory /Users/zhangyifan/Documents/projects/weather) Use @workspace:path syntax (e.g., @frontend:src/index.ts) to specify a workspace.",
                    },
                },
                "required": ["path"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "write_to_file",
            "description": "[IMPORTANT: Always output the absolutePath first] Request to write content to a file at the specified path. If the file exists, it will be overwritten with the provided content. If the file doesn't exist, it will be created. This tool will automatically create any directories needed to write the file.",
            "strict": False,
            "parameters": {
                "type": "object",
                "properties": {
                    "absolutePath": {
                        "type": "string",
                        "description": "The absolute path to the file to write to.",
                    },
                    "content": {
                        "type": "string",
                        "description": "After providing the path so a file can be created, then use this to provide the content to write to the file.",
                    },
                },
                "required": ["absolutePath", "content"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "attempt_completion",
            "description": "Once you've completed the user's task, use this tool to present the final result to the user, including a brief and very short (1-2 paragraph) summary of the task and what was done to resolve it. Provide the basics, hitting the highlights, but do delve into the specifics. You should only call this tool when you have completed all tasks in the task_progress list, and completed all changes that are necessary to satisfy the user's request. You should not provide the contents of the task_progress list in the result parameter, it must be included in the task_progress parameter.",
            "strict": False,
            "parameters": {
                "type": "object",
                "properties": {
                    "result": {
                        "type": "string",
                        "description": "A clear, brief and very short (1-2 paragraph) summary of the final result of the task.",
                    },
                },
                "required": ["result"],
                "additionalProperties": False,
            },
        },
    },
]


def get_tools_from_local() -> list[dict]:
    """本地加载工具列表"""
    # 这里直接写死了，后续可以改成从配置文件夹动态加载
    return LOCAL_TOOLS


def call_tool_on_local(tool_name: str, arguments: dict) -> str:
    if tool_name in LOCAL_TOOLS_MAP:
        return LOCAL_TOOLS_MAP[tool_name](**arguments)
    raise ValueError(f"Unknown local tool: {tool_name}")


async def get_tools_from_server() -> list[dict]:
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{SERVER_BASE_URL}/tools")
            response.raise_for_status()
            return response.json()
        except Exception:
            return []


async def call_tool_on_server(tool_name: str, arguments: dict) -> str:
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{SERVER_BASE_URL}/tools/{tool_name}",
                json={"name": tool_name, "arguments": arguments},
            )
            response.raise_for_status()
            data = response.json()
            if "result" in data:
                return data["result"]
            else:
                return f"Error calling tool: {data.get('error', 'Unknown error')}"
        except Exception as e:
            return f"Exception during tool call: {str(e)}"
