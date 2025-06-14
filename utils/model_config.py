# model_config.py
from typing import Dict, Optional, Callable, Any

# 模型前缀到提供商的映射
MODEL_PROVIDER_MAPPING = {
    "gpt-": "openai",
    "glm": "zhipu",
    "zhipu": "zhipu",
    "doubao": "volcengine",
    "qwen": "qwen",
    "claude": "anthropic",
    "gemini": "google",
}

# 提供商到环境变量的映射
PROVIDER_ENV_MAPPING = {
    "openai": {
        "api_key": "OPENAI_KEY",
        "api_url": "OPENAI_URL",
    },
    "zhipu": {
        "api_key": "ZHIPU_KEY",
        "api_url": "ZHIPU_URL",
    },
    "volcengine": {
        "api_key": "VOLCENGINE_KEY",
        "api_url": "VOLCENGINE_URL",
    },
    "qwen": {
        "api_key": "QWEN_KEY",
        "api_url": "QWEN_URL",
    },
    "anthropic": {
        "api_key": "ANTHROPIC_KEY",
        "api_url": "ANTHROPIC_URL",
        "headers": {"anthropic-version": "2023-06-01"},
    },
    "google": {
        "api_key": "GOOGLE_KEY",
        "api_url": "GOOGLE_URL",
        "key_in_query": True,  # Google API 使用查询参数传递 key
    },
}

# 提供商到响应解析器的映射（如果有特殊解析逻辑）
PROVIDER_PARSER_MAPPING = {
    "anthropic": {
        "non_stream": lambda data: data["content"][0]["text"],
        "stream": lambda chunk: (
            chunk.get("delta", {}).get("text", "")
            if chunk.get("type") == "content_block_delta"
            else ""
        ),
    },
    "google": {
        "non_stream": lambda data: data["candidates"][0]["content"]["parts"][0]["text"],
        "stream": lambda chunk: next(
            (
                part.get("text", "")
                for candidate in chunk.get("candidates", [])
                for part in candidate.get("content", {}).get("parts", [])
            ),
            "",
        ),
    },
    # 添加其他模型提供商的解析器
    "openai": {
        "non_stream": lambda data: data["choices"][0]["message"]["content"],
        "stream": lambda chunk: chunk.get("choices", [{}])[0]
        .get("delta", {})
        .get("content", ""),
    },
    "zhipu": {
        "non_stream": lambda data: data["choices"][0]["message"]["content"],
        "stream": lambda chunk: chunk.get("choices", [{}])[0]
        .get("delta", {})
        .get("content", ""),
    },
    "volcengine": {
        "non_stream": lambda data: data["choices"][0]["message"]["content"],
        "stream": lambda chunk: chunk.get("choices", [{}])[0]
        .get("delta", {})
        .get("content", ""),
    },
    
}


def detect_provider(model_name: str) -> str:
    """根据模型名称检测提供商"""
    for prefix, provider in MODEL_PROVIDER_MAPPING.items():
        if model_name.startswith(prefix):
            return provider
    raise ValueError(f"无法识别的模型前缀：{model_name}")


def get_provider_env(provider: str) -> Dict[str, Any]:
    """获取提供商的环境变量配置"""
    return PROVIDER_ENV_MAPPING.get(provider, {})


def get_provider_parser(provider: str) -> Optional[Dict[str, Callable]]:
    """获取提供商的响应解析器"""
    return PROVIDER_PARSER_MAPPING.get(provider)
