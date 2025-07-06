from utils.ai_client import AIClient
from prompting.loader import load_all_chat_prompts
import os

MAIN_CONTROLLER = "doubao-1.5-pro-32k-250115"
REFERENCE_FILE = "reference.md"
OUTPUT_FILE = "output.md"


def load_prompt_messages() -> list:
    """加载并格式化提示词"""
    prompts = load_all_chat_prompts()
    prompt_template = prompts.get("article_transcription")
    return prompt_template.format()


def load_reference_article(path: str) -> str:
    """读取参考文章内容"""
    if not os.path.exists(path):
        raise FileNotFoundError(f"参考文件不存在：{path}")
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def compose_messages(reference: str, base_messages: list) -> list:
    """构建对话消息序列"""
    base_messages.append({"role": "assistant", "content": reference})
    base_messages.append({"role": "system", "content": "学习这篇文章的风格和内容。"})
    base_messages.append({"role": "user", "content": "从新创作一篇 AI 发展的文章。"})
    return base_messages


def generate_article(messages: list, model: str) -> str:
    """调用 AI 模型生成文章内容"""
    client = AIClient(model=model)
    return client.chat(messages)


def save_to_file(content: str, path: str) -> None:
    """保存生成结果"""
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"✅ 已保存输出至：{os.path.abspath(path)}")


def main():
    try:
        messages = load_prompt_messages()
        reference = load_reference_article(REFERENCE_FILE)
        messages = compose_messages(reference, messages)
        output = generate_article(messages, MAIN_CONTROLLER)
        print(output)
        save_to_file(output, OUTPUT_FILE)
    except Exception as e:
        print(f"❌ 出现错误：{e}")


if __name__ == "__main__":
    main()
