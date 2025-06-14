from utils.ai_client import AIClient
from prompting.loader import load_all_chat_prompts

prompts = load_all_chat_prompts()
summary_prompt = prompts["article_transcription"]
formatted = summary_prompt.format()
# MAIN_CONTROLLER = "doubao-1.5-pro-32k-250115"
MAIN_CONTROLLER = "qwen-plus-latest"
# 添加参考文档
with open("reference.md", "r", encoding="utf-8") as f:
    reference = f.read()
    formatted.append({"role": "assistant", "content": reference})
formatted.append({"role": "system", "content": "学习这篇文章的风格和内容。"})
# 添加 user 消息
formatted.append({"role": "user", "content": "从新创作一篇ai发展的文章。"})

client = AIClient(model=MAIN_CONTROLLER)
message = client.chat(formatted)
print(message)
with open("output.md", "w", encoding="utf-8") as f:
    f.write(message)
