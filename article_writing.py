import asyncio
import os
from loguru import logger
from agents.article_layout_agent import ArticleLayoutAgent
from utils.ai_client import AIClient
from prompting.loader import load_all_chat_prompts


async def main():
    try:
        MODEL_NAME = "doubao-seed-1-6-250615"
        ARTICLE_PATH = "model_essay.md"
        OUTPUT_PATH = "article_transcription.md"

        prompts = load_all_chat_prompts()
        article_transcription_prompt = prompts["article_transcription"]

        logger.info(f"正在加载文章信息: {ARTICLE_PATH}")

        article_info = ""  # 预定义，避免 UnboundLocalError

        if not os.path.exists(ARTICLE_PATH):
            # 文件不存在，创建空文件
            with open(ARTICLE_PATH, "w", encoding="utf-8") as f:
                pass
            logger.warning(f"{ARTICLE_PATH} 不存在，已创建空文件。请提供内容：")
            user_input = input("请输入文章内容（直接按回车跳过并继续执行）：\n")
            if user_input.strip() == "":
                logger.info("用户选择跳过，继续执行...")
            else:
                with open(ARTICLE_PATH, "w", encoding="utf-8") as f:
                    f.write(user_input)
                article_info = user_input
                logger.info(f"内容已写入 {ARTICLE_PATH}")
        elif os.path.getsize(ARTICLE_PATH) == 0:
            # 文件存在但为空
            logger.warning(f"{ARTICLE_PATH} 是空文件，请提供内容：")
            user_input = input("请输入文章内容（直接按回车跳过并继续执行）：\n")
            if user_input.strip() == "":
                logger.info("用户选择跳过，继续执行...")
            else:
                with open(ARTICLE_PATH, "w", encoding="utf-8") as f:
                    f.write(user_input)
                article_info = user_input
                logger.info(f"内容已写入 {ARTICLE_PATH}")
        else:
            # 文件存在且非空
            with open(ARTICLE_PATH, "r", encoding="utf-8") as f:
                article_info = f.read()

        logger.info(f"文章信息加载完成（长度: {len(article_info)} 字符）")

        # 第一步：文章分析
        analysis_client = AIClient(model=MODEL_NAME)
        analysis_messages = article_transcription_prompt.format()
        if article_info:
            analysis_messages.append({"role": "user", "content": article_info})
        # 用户输入确定文章的基本基调和内容
        user_input = input("请确定文章的基础基调和写作内容")
        if user_input.strip():
            analysis_messages.append({"role": "user", "content": user_input})
        logger.info("正在生成文章初步分析...")
        first_response = await analysis_client.chat(
            analysis_messages, deep_think="disabled"
        )

        if not first_response or len(first_response.strip()) == 0:
            logger.error("初步分析结果为空，请检查输入内容或模型配置")
            return
        else:
            logger.info(f"初步分析结果长度: {len(first_response)}")

        # 第二步：格式化布局
        layout_agent = ArticleLayoutAgent(model=MODEL_NAME)
        logger.info("正在格式化分析结果...")
        final_response = await layout_agent.format(first_response)

        with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
            f.write(final_response)
        logger.success(f"分析报告已保存至: {OUTPUT_PATH}")

    except FileNotFoundError as e:
        logger.critical(f"文件不存在: {e.filename}")
        raise
    except Exception as e:
        logger.exception("处理过程中发生未知错误")
        raise


if __name__ == "__main__":
    asyncio.run(main())
