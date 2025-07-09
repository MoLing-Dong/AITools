import asyncio
from loguru import logger
from agents.article_layout_agent import ArticleLayoutAgent
from utils.ai_client import AIClient
from prompting.loader import load_all_chat_prompts


async def main():
    try:
        MODEL_NAME = "doubao-seed-1-6-250615"
        COMPANY_INFO_PATH = "company_info.md"
        OUTPUT_PATH = "company_analysis.md"

        prompts = load_all_chat_prompts()
        company_analysis_prompt = prompts["company_analysis"]

        logger.info(f"正在加载公司信息: {COMPANY_INFO_PATH}")
        with open(COMPANY_INFO_PATH, "r", encoding="utf-8") as f:
            company_info = f.read()
        logger.info(f"公司信息加载完成{company_info}")
        # 第一步：公司分析
        analysis_client = AIClient(model=MODEL_NAME)
        analysis_messages = company_analysis_prompt.format()
        
        analysis_messages.append({"role": "user", "content": company_info})

        logger.info("正在生成公司初步分析...")
        first_analysis = await analysis_client.chat(
            analysis_messages, deep_think="disabled"
        )
        # 是否为空 打印获取内容长度
        if not first_analysis or len(first_analysis) == 0:
            logger.error("初步分析结果为空，请检查输入内容或模型配置")
            return
        else:
            logger.info(f"初步分析结果长度: {len(first_analysis)}")
        # 第二步：格式化布局
        format_analysis = ArticleLayoutAgent(model=MODEL_NAME)
        logger.info("正在格式化分析结果...")
        final_response = await format_analysis.format(first_analysis)

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
