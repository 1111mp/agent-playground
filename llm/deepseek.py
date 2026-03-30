import os
from typing import AsyncGenerator, Dict, List, Optional, Union

from openai import AsyncOpenAI

from .base import LLM


class DeepSeekLLM(LLM):
    """DeepSeek LLM provider"""

    def __init__(self, model: str = "deepseek-chat"):
        self.model = model
        self.client = AsyncOpenAI(
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            base_url="https://api.deepseek.com",
        )

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 1.3,
        max_tokens: int = 1024,
    ) -> str:
        """生成文本"""
        messages = []

        if system_prompt:
            messages.append(
                {
                    "role": "system",
                    "content": system_prompt,
                }
            )

        messages.append(
            {
                "role": "user",
                "content": prompt,
            }
        )

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=False,
        )
        text = response.choices[0].message.content

        if not text:
            raise RuntimeError("DeepSeek returned empty response")

        return text

    async def stream_chat(
        self,
        messages: list,
        tools: list = [],
        temperature: float = 1.3,
        max_tokens: int = 1024,
    ) -> AsyncGenerator[Union[str, Dict], None]:
        """
        流式聊天，支持 tool calls

        Yield:
            str: 普通文本内容（直接展示给用户）
            dict: 当检测到 tool calls 时，yield {"type": "tool_calls", "tool_calls": [...]}
        """
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=tools,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True,
        )

        # 用于累积 tool calls（支持多个 tool call）
        tool_calls: List[Dict] = []

        async for chunk in response:
            if not chunk.choices:
                continue

            delta = chunk.choices[0].delta

            # 1. 普通文本内容（直接 yield 给前端/用户）
            if delta.content:
                yield delta.content

            # 2. 处理 tool calls（流式增量）
            if delta.tool_calls:
                for tool_delta in delta.tool_calls:
                    idx = tool_delta.index

                    # 如果这个 index 的 tool_call 还没创建，就先初始化
                    while len(tool_calls) <= idx:
                        tool_calls.append(
                            {
                                "id": None,
                                "type": "function",
                                "function": {"name": None, "arguments": ""},
                            }
                        )

                    # 当前正在处理的 tool call
                    tc = tool_calls[idx]

                    # 累积 id（通常只出现一次）
                    if tool_delta.id:
                        tc["id"] = tool_delta.id

                    # 累积 function name（通常只出现一次）
                    if tool_delta.function and tool_delta.function.name is not None:
                        tc["function"]["name"] = tool_delta.function.name

                    # 关键：累积 arguments（会分很多小块传来，必须 += 拼接）
                    if tool_delta.function and tool_delta.function.arguments:
                        tc["function"]["arguments"] += tool_delta.function.arguments

        # ====================== 流式结束后处理 ======================
        # 检查是否有有效的 tool call
        valid_tool_calls = [
            tc
            for tc in tool_calls
            if tc.get("function", {}).get("name")  # 有函数名才算有效
        ]

        if valid_tool_calls:
            yield {"type": "tool_calls", "tool_calls": valid_tool_calls}
