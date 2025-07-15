from utils.ai_client import AIClient
from prompting.loader import load_all_chat_prompts


class ArticleLayoutAgent:
    def __init__(self, model: str = "qwen-plus", deep_think: str = "disabled"):
        self.model = model
        self.deep_think = deep_think
        self.client = AIClient(model=self.model)
        self.prompt_template = load_all_chat_prompts()["article_layout"]

    async def format(self, raw_analysis: str) -> str:
        """
        Receive unformatted company analysis content and return formatted articles in markdown format
        """
        messages = self.prompt_template.format()
        messages.append({"role": "user", "content": raw_analysis})
        response = await self.client.chat(messages, deep_think=self.deep_think)
        return response
