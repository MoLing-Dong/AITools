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
        OUTPUT_PATH = "./output/article_transcription.md"
        DEEP_THINK = "disabled"

        prompts = load_all_chat_prompts()
        article_transcription_prompt = prompts["article_transcription"]

        logger.info(f"Loading article information: {ARTICLE_PATH}")

        article_info = ""  # Predefined to avoid UnboundLocalError

        if not os.path.exists(ARTICLE_PATH):
            # File does not exist, create an empty file
            with open(ARTICLE_PATH, "w", encoding="utf-8") as f:
                pass
            logger.warning(
                f"{ARTICLE_PATH} does not exist, an empty file has been created. Please provide content:"
            )
            user_input = input(
                "Please enter the article content (press Enter to skip and continue):\n"
            )
            if user_input.strip() == "":
                logger.info("User chose to skip, continuing...")
            else:
                with open(ARTICLE_PATH, "w", encoding="utf-8") as f:
                    f.write(user_input)
                article_info = user_input
                logger.info(f"Content has been written to {ARTICLE_PATH}")
        elif os.path.getsize(ARTICLE_PATH) == 0:
            # File exists but is empty
            logger.warning(f"{ARTICLE_PATH} is an empty file, please provide content:")
            user_input = input(
                "Please enter the article content (press Enter to skip and continue):\n"
            )
            if user_input.strip() == "":
                logger.info("User chose to skip, continuing...")
            else:
                with open(ARTICLE_PATH, "w", encoding="utf-8") as f:
                    f.write(user_input)
                article_info = user_input
                logger.info(f"Content has been written to {ARTICLE_PATH}")
        else:
            # File exists and is not empty
            with open(ARTICLE_PATH, "r", encoding="utf-8") as f:
                article_info = f.read()

        logger.info(
            f"Article information loaded (length: {len(article_info)} characters)"
        )

        # Step 1: Article analysis
        analysis_client = AIClient(model=MODEL_NAME)
        analysis_messages = article_transcription_prompt.format()
        if article_info:
            analysis_messages.append({"role": "user", "content": article_info})
        # User input to determine the basic tone and content of the article
        user_input = input(
            "Please confirm the basic tone and writing content of the article"
        )
        if user_input.strip():
            analysis_messages.append({"role": "user", "content": user_input})
        logger.info("Generating preliminary article analysis...")
        first_response = await analysis_client.chat(
            analysis_messages, deep_think=DEEP_THINK
        )

        if not first_response or len(first_response.strip()) == 0:
            logger.error(
                "Preliminary analysis result is empty, please check the input content or model configuration"
            )
            return
        else:
            logger.info(f"Preliminary analysis result length: {len(first_response)}")

        # Step 2: Format layout
        layout_agent = ArticleLayoutAgent(model=MODEL_NAME)
        logger.info("Formatting analysis result...")
        final_response = await layout_agent.format(first_response)

        # 新增：确保输出目录存在
        os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

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
