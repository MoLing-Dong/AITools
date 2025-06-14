import time
from utils.ai_client import AIClient


def test_stream_output():
    """测试流式输出功能"""

    # 构造对话消息
    messages = [
        {"role": "system", "content": "你是一个专业的编程助手，请用中文回答"},
        {"role": "user", "content": "请用Python写一个快速排序算法，并详细解释每一行的作用"}
    ]

    # 支持的模型示例
    models_to_test = [
        "doubao-1.5-pro-32k-250115",  # 豆包
        "gpt-3.5-turbo",  # OpenAI
    ]

    for model in models_to_test:
        try:
            print(f"\n{'=' * 60}")
            print(f"🤖 测试模型: {model}")
            print(f"{'=' * 60}")

            client = AIClient(model=model)

            # 显示模型信息
            info = client.get_model_info()
            print(f"📊 模型信息: {info}")
            print(f"\n🔄 开始流式生成...\n")

            start_time = time.time()
            char_count = 0

            # 流式输出
            for chunk in client.chat(
                    messages=messages,
                    stream=True,
                    temperature=0.7,
                    max_tokens=2000
            ):
                print(chunk, end="", flush=True)
                char_count += len(chunk)

            end_time = time.time()
            elapsed = end_time - start_time

            print(f"\n\n✅ 生成完毕")
            print(f"📈 统计: {char_count} 字符，耗时 {elapsed:.2f} 秒")
            print(f"⚡ 平均速度: {char_count / elapsed:.1f} 字符/秒")

        except Exception as e:
            print(f"❌ 模型 {model} 测试失败: {e}")
            continue


def test_non_stream_output():
    """测试非流式输出"""

    messages = [
        {"role": "user", "content": "请简单介绍一下Python的优点"}
    ]

    try:
        client = AIClient(model="doubao-1.5-pro-32k-250115")

        print("\n🔄 非流式模式测试...\n")

        response = client.chat(messages=messages, stream=False, temperature=0.5)
        print(f"📝 完整回复:\n{response}")

    except Exception as e:
        print(f"❌ 非流式测试失败: {e}")


def interactive_chat():
    """交互式聊天测试"""

    print("\n💬 交互式聊天模式 (输入 'quit' 退出)")
    print("-" * 50)

    client = AIClient(model="doubao-1.5-pro-32k-250115")
    messages = [
        {"role": "system", "content": "你是一个友好的AI助手"}
    ]

    while True:
        try:
            user_input = input("\n👤 你: ").strip()
            if user_input.lower() in ['quit', 'exit', '退出']:
                print("👋 再见!")
                break

            if not user_input:
                continue

            messages.append({"role": "user", "content": user_input})

            print("🤖 AI: ", end="", flush=True)
            response_content = ""

            for chunk in client.chat(messages=messages, stream=True, temperature=0.8):
                print(chunk, end="", flush=True)
                response_content += chunk

            messages.append({"role": "assistant", "content": response_content})
            print()  # 换行

        except KeyboardInterrupt:
            print("\n👋 再见!")
            break
        except Exception as e:
            print(f"\n❌ 出错了: {e}")


def main():
    """主函数"""
    print("🚀 AI 客户端流式输出测试")

    # 选择测试模式
    while True:
        print("\n请选择测试模式:")
        print("1. 流式输出测试")
        print("2. 非流式输出测试")
        print("3. 交互式聊天")
        print("4. 退出")

        choice = input("\n请输入选项 (1-4): ").strip()

        if choice == "1":
            test_stream_output()
        elif choice == "2":
            test_non_stream_output()
        elif choice == "3":
            interactive_chat()
        elif choice == "4":
            print("👋 再见!")
            break
        else:
            print("❌ 无效选项，请重新输入")


if __name__ == "__main__":
    main()