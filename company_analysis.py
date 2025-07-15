import asyncio
from loguru import logger
from agents.article_layout_agent import ArticleLayoutAgent
from utils.ai_client import AIClient
from prompting.loader import load_all_chat_prompts


async def main():
    try:
        MODEL_NAME = "doubao-seed-1-6-250615"
        COMPANY_INFO_PATH = "company_info.md"
        OUTPUT_PATH = "./output/company_analysis.md"

        prompts = load_all_chat_prompts()
        company_analysis_prompt = prompts["company_analysis"]

        logger.info(f"Loading company information: {COMPANY_INFO_PATH}")
        with open(COMPANY_INFO_PATH, "r", encoding="utf-8") as f:
            company_info = f.read()
        logger.info(f"Company information loaded: {company_info}")
        # Step 1: Company analysis
        analysis_client = AIClient(model=MODEL_NAME)
        analysis_messages = company_analysis_prompt.format()

        analysis_messages.append({"role": "user", "content": company_info})

        logger.info("Generating preliminary company analysis...")
        first_analysis = await analysis_client.chat(
            analysis_messages, deep_think="disabled"
        )
        # Check if empty, print content length
        if not first_analysis or len(first_analysis) == 0:
            logger.error(
                "Preliminary analysis result is empty, please check the input content or model configuration"
            )
            return
        else:
            logger.info(f"Preliminary analysis result length: {len(first_analysis)}")
        # Step 2: Format layout
        format_analysis = ArticleLayoutAgent(model=MODEL_NAME)
        logger.info("Formatting analysis result...")
        final_response = await format_analysis.format(first_analysis)

        with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
            f.write(final_response)
        logger.success(f"Analysis report has been saved to: {OUTPUT_PATH}")

    except FileNotFoundError as e:
        logger.critical(f"File not found: {e.filename}")
        raise
    except Exception as e:
        logger.exception("An unknown error occurred during processing")
        raise


if __name__ == "__main__":
    asyncio.run(main())
