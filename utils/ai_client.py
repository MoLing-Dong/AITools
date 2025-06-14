# -*- coding: utf-8 -*-

import json
import os
from typing import List, Dict, Any, Generator, Optional

import requests
from dotenv import load_dotenv

# 导入模型配置
from utils.model_config import detect_provider, get_provider_env, get_provider_parser

load_dotenv()


class AIClient:
    def __init__(self, model: str):
        self.model = model
        self.provider = detect_provider(model)
        self.api_key, self.api_url = self._load_provider_env()
        self.parser = get_provider_parser(self.provider)

    def _load_provider_env(self) -> tuple[str, str]:
        """加载不同提供商的环境变量"""
        env_config = get_provider_env(self.provider)
        api_key_env = env_config.get("api_key")
        api_url_env = env_config.get("api_url")

        if not api_key_env or not api_url_env:
            raise EnvironmentError(f"提供商 {self.provider} 的环境变量配置缺失")

        api_key = os.getenv(api_key_env)
        api_url = os.getenv(api_url_env)

        if not api_key or not api_url:
            raise EnvironmentError(f"环境变量缺失：{api_key_env} 或 {api_url_env}")

        return api_key, api_url

    def _get_headers(self) -> Dict[str, str]:
        """根据不同提供商构造请求头"""
        base_headers = {"Content-Type": "application/json; charset=utf-8"}

        # 获取特定提供商的头信息
        provider_config = get_provider_env(self.provider)
        provider_headers = provider_config.get("headers", {})

        # 处理认证头
        if self.provider == "anthropic":
            base_headers["x-api-key"] = self.api_key
        elif provider_config.get("key_in_query"):
            # Google API 使用查询参数传递 key，不设置认证头
            pass
        else:
            base_headers["Authorization"] = f"Bearer {self.api_key}"

        # 添加提供商特定的头
        base_headers.update(provider_headers)

        return base_headers

    def _build_payload(self, messages: List[Dict[str, str]], stream: bool, **kwargs) -> Dict[str, Any]:
        """根据不同提供商构造请求载荷"""
        base_payload = {
            "model": self.model,
            "stream": stream,
            **kwargs
        }

        if self.provider == "anthropic":
            # Anthropic 使用不同的消息格式
            system_msg = next((msg["content"] for msg in messages if msg["role"] == "system"), "")
            user_messages = [msg for msg in messages if msg["role"] != "system"]

            base_payload.update({
                "max_tokens": kwargs.get("max_tokens", 4000),
                "messages": user_messages
            })
            if system_msg:
                base_payload["system"] = system_msg
        else:
            base_payload["messages"] = messages

        return base_payload

    def chat(
            self,
            messages: List[Dict[str, str]],
            stream: bool = False,
            **kwargs: Any
    ) -> Any:
        """
        通用 Chat 接口调用，支持流式输出

        :param messages: 对话消息数组
        :param stream: 是否启用流式模式
        :param kwargs: temperature, top_p, max_tokens 等参数
        :return: 完整文本 or 流式生成器
        """
        headers = self._get_headers()
        payload = self._build_payload(messages, stream, **kwargs)

        # 处理 URL（Google API 使用查询参数传递 key）
        url = self.api_url
        if get_provider_env(self.provider).get("key_in_query"):
            url = f"{self.api_url}?key={self.api_key}"

        try:
            response = requests.post(url, headers=headers, json=payload, stream=stream, timeout=60)
            response.encoding = 'utf-8'
            response.raise_for_status()

            if stream:
                return self._stream_response(response)
            else:
                return self._parse_non_stream_response(response)

        except requests.exceptions.Timeout:
            return "[错误] 请求超时，请稍后重试"
        except requests.exceptions.RequestException as e:
            return f"[请求失败] {e}"
        except Exception as e:
            return f"[未知错误] {e}"

    def _parse_non_stream_response(self, response: requests.Response) -> str:
        """解析非流式响应"""
        try:
            data = response.json()

            # 使用提供商特定的解析器（如果有）
            if self.parser and "non_stream" in self.parser:
                return self.parser["non_stream"](data)

            # 通用解析逻辑
            return data["choices"][0]["message"]["content"]

        except (KeyError, IndexError, json.JSONDecodeError) as e:
            return f"[解析错误] 返回格式异常：{e}\n原始响应：{response.text[:500]}"

    def _stream_response(self, response: requests.Response) -> Generator[str, None, None]:
        """
        处理流式响应，适配不同提供商的格式

        :param response: HTTP 响应对象
        :yield: 每一段文本内容
        """
        buffer = ""

        try:
            for line in response.iter_lines(decode_unicode=True):
                if not line or line.strip() == "":
                    continue

                content = self._extract_stream_content(line.strip())
                if content:
                    buffer += content
                    yield content

        except Exception as e:
            yield f"\n[流式解析异常] {e}"

        # 确保完整性
        if not buffer.strip():
            yield "[警告] 未接收到有效内容"

    def _extract_stream_content(self, line: str) -> Optional[str]:
        """从流式响应行中提取内容"""
        try:
            # 移除 "data: " 前缀
            if line.startswith("data:"):
                line = line[5:].strip()

            # 检查结束标志
            if line in ["[DONE]", "data: [DONE]"]:
                return None

            # 尝试解析 JSON
            chunk = json.loads(line)

            # 使用提供商特定的解析器（如果有）
            if self.parser and "stream" in self.parser:
                # 对于有特殊解析逻辑的提供商
                return self.parser["stream"](chunk)

            # 通用解析逻辑
            choices = chunk.get("choices", [])
            if choices:
                delta = choices[0].get("delta", {})
                return delta.get("content", "")

        except json.JSONDecodeError:
            # 有些提供商可能发送非JSON行
            pass
        except Exception as e:
            return f"[解析错误: {e}]"

        return None

    def get_model_info(self) -> Dict[str, str]:
        """获取当前模型信息"""
        return {
            "model": self.model,
            "provider": self.provider,
            "api_url": self.api_url,
            "has_api_key": bool(self.api_key)
        }
