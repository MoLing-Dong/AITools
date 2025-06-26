from utils.ai_client import AIClient
from prompting.loader import load_all_chat_prompts

prompts = load_all_chat_prompts()
summary_prompt = prompts["company_analysis"]
formatted = summary_prompt.format()
# 模型选择
MAIN_CONTROLLER = "doubao-1.5-pro-32k-250115"
# 添加公司信息
with open("company_info.txt", "r", encoding="utf-8") as f:
    company_info = f.read()
    formatted.append({"role": "assistant", "content": company_info})

# 添加 user 消息
formatted.append({"role": "user", "content": "分析该公司全景画像"})

client = AIClient(model=MAIN_CONTROLLER)
message = client.chat(formatted)
with open("company_analysis.md", "w", encoding="utf-8") as f:
    f.write(message)
print("Done. Company analysis saved to company_analysis.md")
