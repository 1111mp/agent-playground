from actuator import run_restricted
from anyio import to_thread
from crud import get_tool_by_name, load_tools
from fastapi import FastAPI
from pydantic import BaseModel
from tool import Tool
from utils import NWS_API_BASE, format_alert, make_nws_request

app = FastAPI()


class AgentTool(BaseModel):
    type: str
    function: Tool


@app.get("/tools")
async def get_tools() -> list[AgentTool]:
    tools = load_tools()
    data = [AgentTool(type="function", function=tool) for tool in tools]
    return data


class ToolCallDto(BaseModel):
    name: str
    arguments: dict


@app.post("/tools/{tool_name}")
async def call_tool(tool_name: str, args: ToolCallDto):
    tool = get_tool_by_name(tool_name)
    if not tool:
        return {"error": "Tool not found"}

    try:
        result = await to_thread.run_sync(
            run_restricted,
            tool.code,
            args.arguments,
            # 这里传入工具函数可能需要的额外函数和常量
            # 目前写死，后续可以改成工具定义里指定需要哪些函数和常量
            # 或者借助一些 rules 工具来自动分析工具代码里用到了哪些函数和常量
            {
                "NWS_API_BASE": NWS_API_BASE,
                "make_nws_request": make_nws_request,
                "format_alert": format_alert,
            },
        )
        return {"result": result}
    except Exception as e:
        return {"error": str(e)}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
