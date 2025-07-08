import asyncio
from loguru import logger
from agents.article_layout_agent import ArticleLayoutAgent
from utils.ai_client import AIClient
from prompting.loader import load_all_chat_prompts


async def main():
    try:
        MODEL_NAME = "doubao-seed-1-6-250615"
        ARTICLE_PATH = "company_info.md"
        OUTPUT_PATH = "article_transcription.md"

        prompts = load_all_chat_prompts()
        article_transcription_prompt = prompts["article_transcription"]

        logger.info(f"正在加载文章信息: {ARTICLE_PATH}")
        with open(ARTICLE_PATH, "r", encoding="utf-8") as f:
            article_info = f.read()
        logger.info(f"文章信息加载完成{article_info}")
        # 第一步：文章分析
        analysis_client = AIClient(model=MODEL_NAME)
        analysis_messages = article_transcription_prompt.format()

        analysis_messages.append({"role": "user", "content": article_info})

        logger.info("正在生成文章初步分析...")
        first_response = await analysis_client.chat(
            analysis_messages, deep_think="disabled"
        )
        # 是否为空 打印获取内容长度
        if not first_response or len(first_response) == 0:
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
