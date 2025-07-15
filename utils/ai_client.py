# -*- coding: utf-8 -*-
import json
import os
from loguru import logger
from typing import List, Dict, Any, AsyncGenerator, Optional

import httpx
from dotenv import load_dotenv

# Import model config
from utils.model_config import detect_provider, get_provider_env, get_provider_parser

load_dotenv()


class AIClient:
    def __init__(self, model: str):
        self.model = model
        self.provider = detect_provider(model)
        self.api_key, self.api_url = self._load_provider_env()
        self.parser = get_provider_parser(self.provider)

    def _load_provider_env(self) -> tuple[str, str]:
        env_config = get_provider_env(self.provider)
        api_key_env = env_config.get("api_key")
        api_url_env = env_config.get("api_url")

        if not api_key_env or not api_url_env:
            raise EnvironmentError(
                f"Missing environment variable configuration for provider {self.provider}"
            )

        api_key = os.getenv(api_key_env)
        api_url = os.getenv(api_url_env)

        if not api_key or not api_url:
            raise EnvironmentError(
                f"Missing environment variable: {api_key_env} or {api_url_env}"
            )

        return api_key, api_url

    def _get_headers(self) -> Dict[str, str]:
        base_headers = {"Content-Type": "application/json; charset=utf-8"}
        provider_config = get_provider_env(self.provider)
        provider_headers = provider_config.get("headers", {})

        if self.provider == "anthropic":
            base_headers["x-api-key"] = self.api_key
        elif not provider_config.get("key_in_query"):
            base_headers["Authorization"] = f"Bearer {self.api_key}"

        base_headers.update(provider_headers)
        return base_headers

    def _build_payload(
        self, messages: List[Dict[str, str]], stream: bool, **kwargs
    ) -> Dict[str, Any]:
        base_payload = {"model": self.model, "stream": stream, **kwargs}

        if self.provider == "anthropic":
            system_msg = next(
                (msg["content"] for msg in messages if msg["role"] == "system"), ""
            )
            user_messages = [msg for msg in messages if msg["role"] != "system"]

            base_payload.update(
                {
                    "max_tokens": kwargs.get("max_tokens", 4000),
                    "messages": user_messages,
                }
            )
            if system_msg:
                base_payload["system"] = system_msg
        else:
            base_payload["messages"] = messages

        # ✅ Volcengine: Add deepthink support
        if self.provider == "volcengine":
            deepthink_type = kwargs.pop("deep_think", None)
            if deepthink_type in {"enabled", "disabled", "auto"}:
                base_payload["thinking"] = {"type": deepthink_type}
            else:
                # Add default value "disabled"
                base_payload["thinking"] = {"type": "disabled"}
            # Remove deep_think parameter from base_payload
            base_payload.pop("deep_think", None)
        return base_payload

    async def chat(
        self, messages: List[Dict[str, str]], stream: bool = False, **kwargs: Any
    ) -> Any:
        headers = self._get_headers()
        payload = self._build_payload(messages, stream, **kwargs)
        url = self.api_url
        if get_provider_env(self.provider).get("key_in_query"):
            url = f"{self.api_url}?key={self.api_key}"

        try:
            async with httpx.AsyncClient(timeout=1800) as client:
                response = await client.post(url, headers=headers, json=payload)

                if response.status_code != 200:
                    return f"[Request Failed] {response.status_code} - {response.text}"

                if stream:
                    return self._stream_response(response)
                else:
                    return self._parse_non_stream_response(response)

        except httpx.TimeoutException:
            return "[Error] Request timed out, please try again later"
        except httpx.RequestError as e:
            return f"[Request Failed] {e}"
        except Exception as e:
            return f"[Unknown Error] {e}"

    def _parse_non_stream_response(self, response: httpx.Response) -> str:
        try:
            data = response.json()
            # Check if reasoning_content is output
            if data["choices"][0]["message"].get("reasoning_content"):
                logger.debug(
                    f"reasoning_content: {data['choices'][0]['message']['reasoning_content']}"
                )
            else:
                logger.debug("No reasoning_content field detected")

            if self.parser and "non_stream" in self.parser:
                return self.parser["non_stream"](data)

            return data["choices"][0]["message"]["content"]

        except (KeyError, IndexError, json.JSONDecodeError) as e:
            return f"[Parse Error] Abnormal return format: {e}\nRaw response: {response.text[:500]}"

    async def _stream_response(
        self, response: httpx.Response
    ) -> AsyncGenerator[str, None]:
        buffer = ""

        try:
            async for line in response.aiter_lines():
                if not line or line.strip() == "":
                    continue

                content = self._extract_stream_content(line.strip())
                if content:
                    buffer += content
                    yield content

        except Exception as e:
            yield f"\n[Stream Parse Exception] {e}"

        if not buffer.strip():
            yield "[Warning] No valid content received"

    def _extract_stream_content(self, line: str) -> Optional[str]:
        try:
            if line.startswith("data:"):
                line = line[5:].strip()

            if line in ["[DONE]", "data: [DONE]"]:
                return None

            chunk = json.loads(line)

            if self.parser and "stream" in self.parser:
                return self.parser["stream"](chunk)

            choices = chunk.get("choices", [])
            if choices:
                delta = choices[0].get("delta", {})
                return delta.get("content", "")

        except json.JSONDecodeError:
            pass
        except Exception as e:
            return f"[Parse Error: {e}]"

        return None

    def get_model_info(self) -> Dict[str, str]:
        return {
            "model": self.model,
            "provider": self.provider,
            "api_url": self.api_url,
            "has_api_key": "true" if self.api_key else "false",
        }
