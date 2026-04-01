import asyncio
import json

from dotenv import load_dotenv

from llm.deepseek import DeepSeekLLM
from tools.base import (
    call_tool_on_local,
    call_tool_on_server,
    get_tools_from_local,
    get_tools_from_server,
)

load_dotenv()

# 获取明天纽约的天气，并将结果写入到 "/Users/zhangyifan/Documents/projects/agent-playground/weather.md" 文件中


class Agent:
    def __init__(self, llm) -> None:
        self.llm = llm
        self.local_tools = []
        self.server_tools = []
        self.messages = [
            {
                "role": "system",
                "content": """
								你是一个智能助手，可以帮助用户完成各种任务。你可以调用一些工具来获取信息或执行操作。请根据用户的需求选择合适的工具，并正确使用它们。
								一旦你完成了用户的任务，你必须使用 attempt_completion 工具向用户展示任务结果。
								如果任务不可操作，你可以使用 attempt_completion 工具向用户解释为什么无法完成任务，或者如果用户只是寻求简单回答，则提供简单答案。
                """,
            }
        ]

    async def load_tools(self):
        """
        加载工具列表

        1. 本地加载
        2. 从 server 加载
        """
        tools_from_local = get_tools_from_local()
        self.local_tools.extend(tools_from_local)
        tools_from_server = await get_tools_from_server()
        self.server_tools.extend(tools_from_server)

    async def tool_call(self, tool_name: str, arguments: dict) -> str:
        """调用工具"""
        # 1. 先在本地工具里找
        if tool_name in [tool["function"]["name"] for tool in self.local_tools]:
            return call_tool_on_local(tool_name, arguments)

        # 2. 如果本地没有，再调用服务器工具
        if tool_name in [tool["function"]["name"] for tool in self.server_tools]:
            return await call_tool_on_server(tool_name, arguments)

        return "Tool not found."

    async def agent_loop(self):
        while True:
            print("\n🤖 DeepSeek says: thinking...\n\n", end="", flush=True)
            full_reply = ""
            tool_calls = None
            is_completion_streaming = False

            async for chunk in self.llm.stream_chat(
                messages=self.messages, tools=self.local_tools + self.server_tools
            ):
                if isinstance(chunk, str):
                    full_reply += chunk
                    print(chunk, end="", flush=True)
                elif isinstance(chunk, dict):
                    chunk_type = chunk.get("type")

                    # 实时流式输出 attempt_completion 的内容（最接近 Cline 的效果）
                    if chunk_type == "completion_stream":
                        content = chunk.get("content", "")
                        if content:
                            if not is_completion_streaming:
                                print("\n🤖 最终回答:\n", end="", flush=True)
                                is_completion_streaming = True
                            print(content, end="", flush=True)

                    # 完整的 tool_calls（流结束后的最终信号）
                    elif chunk_type == "tool_calls":
                        tool_calls = chunk["tool_calls"]
                        print("\n[工具调用处理中...]", end="", flush=True)
                        break

            # 换行
            print()

            # ====================== 如果有 full_reply，则添加消息并继续对话 ======================
            if full_reply and not tool_calls:
                self.messages.append({"role": "assistant", "content": full_reply})
                return

            # ====================== 如果有 tool_calls，则执行工具并继续对话 ======================
            if tool_calls:
                # 1. 把 assistant 的 tool_calls 加入历史
                self.messages.append({"role": "assistant", "tool_calls": tool_calls})

                # 2. 执行所有工具（支持并行）
                for tc in tool_calls:
                    tool_name = tc["function"]["name"]
                    try:
                        tool_args = (
                            json.loads(tc["function"]["arguments"])
                            if tc["function"]["arguments"]
                            else {}
                        )
                    except json.JSONDecodeError:
                        tool_args = {}
                        print(
                            f"[Warning] 参数解析失败: {tc['function']['arguments']}\n"
                        )

                    if tool_name != "attempt_completion":
                        print(f"tool_call: {tc} \n")
                        print(f"→ 调用工具: {tool_name}({tool_args})\n")

                    result = await self.tool_call(
                        tool_name=tool_name, arguments=tool_args
                    )

                    self.messages.append(
                        {"role": "tool", "tool_call_id": tc["id"], "content": result}
                    )

                    if tool_name == "attempt_completion":
                        # 已经实时打印过了，这里只需收尾
                        print("✅ 任务已完成")
                        return

                    print("📨 工具返回:", result, "\n")

    async def run_loop(self):
        """主循环，处理用户输入和 Agent 推理流程"""
        while True:
            # 1️⃣ 从终端读取输入（阻塞）
            user_input = input("\n👤 You: ")

            # 2️⃣ 退出条件
            if user_input.lower() in ["exit", "quit"]:
                print("👋 Bye!")
                break

            self.messages.append({"role": "user", "content": user_input})

            await self.agent_loop()


async def main():
    llm = DeepSeekLLM(model="deepseek-reasoner")
    agent = Agent(llm=llm)
    # 记载所有工具（本地 + server）
    await agent.load_tools()
    print(f"本地工具: {agent.local_tools}\n")
    print(f"服务器工具: {agent.server_tools}\n")

    await agent.run_loop()


if __name__ == "__main__":
    asyncio.run(main())
