from utils.ai_client import AIClient
from prompting.loader import load_all_chat_prompts


class ArticleLayoutAgent:
    def __init__(self, model: str = "qwen-plus"):
        self.model = model
        self.client = AIClient(model=self.model)
        self.prompt_template = load_all_chat_prompts()["article_layout"]

    async def format(self, raw_analysis: str) -> str:
        """
        接收未格式化的公司分析内容，返回排版后的 markdown 格式文章
        """
        messages = self.prompt_template.format()
        messages.append({"role": "user", "content": raw_analysis})
        response = await self.client.chat(messages)
        return response
