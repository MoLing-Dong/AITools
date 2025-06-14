import os

import yaml

from .base import ChatPrompt


def load_chat_prompt_from_yaml(file_path: str) -> ChatPrompt:
    with open(file_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
        return ChatPrompt(system=data['system'])


def load_all_chat_prompts() -> dict:
    # 先获取当前文件所在目录
    base_dir = os.path.dirname(os.path.abspath(__file__))
    prompts_dir = os.path.join(base_dir, 'prompts')

    prompts = {}
    if not os.path.exists(prompts_dir):
        raise FileNotFoundError(f"目录不存在: {prompts_dir}")
    for filename in os.listdir(prompts_dir):
        if filename.endswith('.yml') or filename.endswith('.yaml'):
            name = filename.rsplit('.', 1)[0]
            path = os.path.join(prompts_dir, filename)
            prompts[name] = load_chat_prompt_from_yaml(path)
    return prompts
