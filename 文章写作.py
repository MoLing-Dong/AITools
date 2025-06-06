from ai_client import AIClient
from prompting.loader import load_all_chat_prompts

prompts = load_all_chat_prompts()
summary_prompt = prompts['article_transcription']
formatted = summary_prompt.format()

# 添加 user 消息
formatted.append({
    "role": "user",
    "content": "创作一篇ai发展的文章。"
})
client = AIClient(model="doubao-1.5-pro-32k-250115")
message = client.chat(formatted)
print(message)
with open("output.md", "w", encoding="utf-8") as f:
    f.write(message)
