from pathlib import Path

PROMPT_DIR = Path(__file__).parent / "prompt"


class PromptLoader:
    def __init__(self, prompt_dir: Path = PROMPT_DIR) -> None:
        self.prompt_dir = prompt_dir

    def load_file(self, filename: str) -> str:
        path = self.prompt_dir / filename
        if not path.exists():
            raise FileNotFoundError(f"Prompt file not found: {path}")
        return path.read_text(encoding="utf-8").strip()

    def load_system_prompt(self) -> str:
        """
        加载 system prompt
        参考的是 Cline 的 system prompt（可以自己本地尝试抓取）
        """
        return self.load_file("system.md")

    def load_user_prompt(self) -> str:
        """
        加载用户 prompt
        参考的是 Cline 的 user prompt（可以自己本地尝试抓取）
        """
        return self.load_file("user.md")

    def load_environment_prompt(self) -> str:
        """
        加载环境 prompt
        参考的是 Cline 的 user prompt（可以自己本地尝试抓取）
        """
        return self.load_file("environment.md")
