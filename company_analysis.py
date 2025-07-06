from utils.ai_client import AIClient
from prompting.loader import load_all_chat_prompts
from utils.common import append_file_content
import os

MAIN_CONTROLLER = "doubao-1.5-pro-32k-250115"
DATA_FILE = "company_financials.txt"
OUTPUT_FILE = "company_analysis.md"


def load_prompt_messages() -> list:
    """加载并格式化分析提示词"""
    prompts = load_all_chat_prompts()
    summary_prompt = prompts.get("company_analysis")
    return summary_prompt.format()


def ensure_financial_data(messages: list) -> None:
    """
    尝试从文件添加公司财务信息，如失败则进入手动输入模式。
    信息将以 assistant 的角色形式追加到 messages 中。
    """
    try:
        success = append_file_content(DATA_FILE, messages, role="assistant")
        if not success:
            raise FileNotFoundError(f"{DATA_FILE} 文件为空或不存在")
    except Exception as e:
        print(f"⚠️ 无法加载公司财务数据：{e}")
        manual_input = input("请输入公司财务信息：").strip()
        if manual_input:
            messages.append({"role": "assistant", "content": manual_input})
            print("✅ 已添加手动输入的内容")
        else:
            print("⚠️ 手动输入为空，将仅使用默认提示词进行分析")


def analyze_company(messages: list, model: str) -> str:
    """调用 AI 客户端生成公司分析报告"""
    client = AIClient(model=model)
    messages.append({"role": "user", "content": "分析该公司全景画像"})
    return client.chat(messages)


def save_report(content: str, path: str) -> None:
    """保存分析结果到文件"""
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"✅ 分析完成，结果已保存至：{os.path.abspath(path)}")


def main():
    messages = load_prompt_messages()
    ensure_financial_data(messages)
    report = analyze_company(messages, MAIN_CONTROLLER)
    save_report(report, OUTPUT_FILE)


if __name__ == "__main__":
    main()
