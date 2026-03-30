from abc import ABC, abstractmethod
from typing import AsyncGenerator, Dict, Optional, Union


class LLM(ABC):
    """所有大模型的统一接口"""

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> str:
        """生成文本"""
        pass

    @abstractmethod
    def stream_chat(
        self,
        messages: list,
        tools: list = [],
        temperature: float = 1.3,
        max_tokens: int = 1024,
    ) -> AsyncGenerator[Union[str, Dict], None]:
        """流式聊天"""
        pass
