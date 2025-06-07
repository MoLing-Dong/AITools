from prompting.loader import load_all_chat_prompts

prompts = load_all_chat_prompts()
summary_prompt = prompts['article_transcription']

formatted = summary_prompt.format()
print(formatted)
