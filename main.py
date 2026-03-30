import asyncio

from dotenv import load_dotenv
from google.genai.types import json

from llm.deepseek import DeepSeekLLM
from tools.weather import get_forecast

load_dotenv()

# 明天纽约的天气怎么样

tools_map = {"get_forecast": get_forecast}
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_forecast",
            "description": "weather: Get weather forecast for a location.\n\nArgs:\n    latitude: Latitude of the location\n    longitude: Longitude of the location\n",
            "strict": False,
            "parameters": {
                "type": "object",
                "properties": {
                    "latitude": {
                        "type": "number",
                        "description": "",
                        "title": "Latitude",
                    },
                    "longitude": {
                        "type": "number",
                        "description": "",
                        "title": "Longitude",
                    },
                },
                "required": ["latitude", "longitude"],
                "additionalProperties": False,
            },
        },
    }
]


# ================= Agent Loop =================
async def run_agent(llm, messages):
    """
    处理一次用户输入后的完整 Agent 推理流程
    支持无限工具调用
    """

    while True:
        print("\n🤖 DeepSeek says: thinking...\n\n", end="", flush=True)

        full_reply = ""
        tool_calls = None

        # 3️⃣ 调用 LLM & 流式接收
        async for chunk in llm.stream_chat(messages=messages, tools=tools):
            if isinstance(chunk, str):
                full_reply += chunk
                print(chunk, end="", flush=True)
            elif isinstance(chunk, dict) and chunk.get("type") == "tool_calls":
                tool_calls = chunk["tool_calls"]
                print("[工具调用中...]", end="", flush=True)
                break

        print()

        # ====================== 如果有 full_reply，则添加消息并继续对话 ======================
        if full_reply and not tool_calls:
            messages.append({"role": "assistant", "content": full_reply})
            return
        # ====================== 如果有 tool_calls，则执行工具并继续对话 ======================
        if tool_calls:
            # 1. 把 assistant 的 tool_calls 加入历史
            messages.append({"role": "assistant", "tool_calls": tool_calls})
            # 2. 执行所有工具（支持并行）
            for tc in tool_calls:
                print(f"tool_call: {tc} \n")
                tool_name = tc["function"]["name"]
                try:
                    tool_args = (
                        json.loads(tc["function"]["arguments"])
                        if tc["function"]["arguments"]
                        else {}
                    )
                except json.JSONDecodeError:
                    tool_args = {}
                    print(f"[Warning] 参数解析失败: {tc['function']['arguments']}\n")

                print(f"→ 调用工具: {tool_name}({tool_args})\n")

                too_func = tools_map[tool_name]
                result = await too_func(**tool_args)

                print("📨 工具返回:", result, "\n")

                messages.append(
                    {"role": "tool", "tool_call_id": tc["id"], "content": result}
                )


async def main():
    """
    prompt 参考 Cline 的实现，就不自己从 0 到 1 写一份了
    prompt 的质量很大一方面取决于经验
    """
    llm = DeepSeekLLM(model="deepseek-reasoner")
    messages = []

    # prompt_loader = PromptLoader()
    # # 初始化时添加 system prompt
    # system_prompt = prompt_loader.load_system_prompt()
    # messages.append({"role": "system", "content": system_prompt})
    # user_prompt = prompt_loader.load_user_prompt()
    # environment_prompt = prompt_loader.load_environment_prompt()

    print("🤖 DeepSeek Chat 已启动 (输入 exit 退出)")

    while True:
        # 1️⃣ 从终端读取输入（阻塞）
        user_input = input("\n👤 You: ")

        # 2️⃣ 退出条件
        if user_input.lower() in ["exit", "quit"]:
            print("👋 Bye!")
            break

        messages.append({"role": "user", "content": user_input})

        await run_agent(llm, messages)


if __name__ == "__main__":
    asyncio.run(main())
