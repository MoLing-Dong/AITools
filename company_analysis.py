from utils.ai_client import AIClient
from prompting.loader import load_all_chat_prompts
from utils.common import append_file_content

prompts = load_all_chat_prompts()
summary_prompt = prompts["company_analysis"]
formatted = summary_prompt.format()

# 模型选择
MAIN_CONTROLLER = "doubao-1.5-pro-32k-250115"

# 添加公司信息 - 增强版，支持手动输入
try:
    success = append_file_content("company_financials.txt", formatted, role="assistant")
    if not success:
        raise FileNotFoundError
except (FileNotFoundError, Exception) as e:
    print("未找到数据文件或文件为空，将进入手动输入模式...")
    manual_input = input("请输入公司财务信息：")
    if manual_input.strip():
        formatted.append({"role": "assistant", "content": manual_input.strip()})
        print("已添加手动输入的内容")
    else:
        print("手动输入为空，分析将基于默认提示")

# 添加 user 消息
formatted.append({"role": "user", "content": "分析该公司全景画像"})

client = AIClient(model=MAIN_CONTROLLER)
message = client.chat(formatted)
with open("company_analysis.md", "w", encoding="utf-8") as f:
    f.write(message)
print("Done. Company analysis saved to company_analysis.md")
