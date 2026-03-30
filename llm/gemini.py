import os
from typing import AsyncGenerator, Dict, Optional, Union

from google import genai
from google.genai import types

from .base import LLM


class GeminiLLM(LLM):
    """Gemini LLM provider"""

    def __init__(self, model: str = "gemini-2.0-flash", api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set")

        self.client = genai.Client(api_key=self.api_key)
        self.model = model

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> str:
        """生成文本"""

        contents = []

        if system_prompt:
            contents.append(
                types.Content(
                    role="system", parts=[types.Part.from_text(text=system_prompt)]
                )
            )

        contents.append(
            types.Content(role="user", parts=[types.Part.from_text(text=prompt)])
        )

        response = self.client.models.generate_content(
            model=self.model,
            contents=contents,
            config=types.GenerateContentConfig(
                temperature=temperature, max_output_tokens=max_tokens
            ),
        )

        if not response.text:
            raise RuntimeError("Gemini returned empty response")

        return response.text

    async def stream_chat(
        self,
        messages: list,
        tools: list = [],
        temperature: float = 1.3,
        max_tokens: int = 1024,
    ) -> AsyncGenerator[Union[str, Dict], None]:
        """流式聊天"""
        contents = []
        for message in messages:
            contents.append(
                types.Content(
                    role=message["role"],
                    parts=[types.Part.from_text(text=message["content"])],
                )
            )

        # https://github.com/googleapis/python-genai?tab=readme-ov-file#manually-declare-and-invoke-a-function-for-function-calling
        formated_tools = []
        for tool in tools:
            function = types.FunctionDeclaration(
                name=tool["name"],
                description=tool["description"],
                parameters_json_schema=tool["parameters_json_schema"],
            )
            formated_tools.append(types.Tool(function_declarations=[function]))

        async for chunk in await self.client.aio.models.generate_content_stream(
            model=self.model,
            contents=contents,
            config=types.GenerateContentConfig(
                temperature=temperature,
                max_output_tokens=max_tokens,
                tools=formated_tools,
            ),
        ):
            if not chunk.text:
                continue
            yield chunk.text
