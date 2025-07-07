import asyncio
from loguru import logger
from utils.ai_client import AIClient
from prompting.loader import load_all_chat_prompts


async def main():
    try:
        MODEL_NAME = "qwen-plus"
        COMPANY_INFO_PATH = "company_info.md"
        OUTPUT_PATH = "company_analysis.md"

        prompts = load_all_chat_prompts()
        company_analysis_prompt = prompts["company_analysis"]
        article_layout_prompt = prompts["article_layout"]

        logger.info(f"正在加载公司信息: {COMPANY_INFO_PATH}")
        with open(COMPANY_INFO_PATH, "r", encoding="utf-8") as f:
            company_info = f.read()

        # 第一步：公司分析
        analysis_client = AIClient(model=MODEL_NAME)
        analysis_messages = company_analysis_prompt.format()
        analysis_messages.append({"role": "assistant", "content": company_info})
        analysis_messages.append({"role": "user", "content": "分析该公司全景画像"})

        logger.info("正在生成公司初步分析...")
        first_response = await analysis_client.chat(analysis_messages)

        # 第二步：格式化布局
        layout_client = AIClient(model=MODEL_NAME)
        layout_messages = article_layout_prompt.format()
        layout_messages.append({"role": "user", "content": first_response})

        logger.info("正在格式化分析结果...")
        final_response = await layout_client.chat(layout_messages)

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
