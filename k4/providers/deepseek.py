"""DeepSeek provider adapter."""

import json
import logging
import os
import urllib.error
import urllib.request

logger = logging.getLogger(__name__)

# 安全限制
MAX_RESPONSE_SIZE = 1024 * 1024  # 最大响应1MB
MAX_CONTENT_LENGTH = 512 * 1024  # 最大内容长度512KB
DEFAULT_TIMEOUT = 30  # 默认超时30秒
MAX_RETRIES = 1  # 最多重试1次


def _mask_api_key(key: str) -> str:
    """脱敏API Key，只显示前4后4位"""
    if not key or len(key) < 8:
        return "****"
    return f"{key[:4]}...{key[-4:]}"


class DeepSeekClient:
    """Minimal DeepSeek chat client using the OpenAI-compatible API."""

    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None,
        base_url: str = "https://api.deepseek.com",
        timeout_seconds: int = DEFAULT_TIMEOUT,
    ) -> None:
        self.api_key = api_key or os.environ.get("DEEPSEEK_API_KEY")
        self.model = model or os.environ.get("DEEPSEEK_MODEL", "deepseek-v4-flash")
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = min(timeout_seconds, 120)  # 最大超时120秒

        # 安全日志：不记录完整API Key
        if self.api_key:
            logger.debug(f"DeepSeek client initialized with key: {_mask_api_key(self.api_key)}")

    def chat_json(self, system_prompt: str, user_prompt: str, max_tokens: int = 1200) -> dict:
        if not self.api_key:
            raise RuntimeError("DeepSeek API key is not configured")

        # 限制max_tokens范围
        max_tokens = max(100, min(max_tokens, 4096))

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "response_format": {"type": "json_object"},
            "max_tokens": max_tokens,
            "stream": False,
            "temperature": 0.1,  # 低温度减少幻觉
        }

        request = urllib.request.Request(
            f"{self.base_url}/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )

        try:
            with urllib.request.urlopen(request, timeout=self.timeout_seconds) as response:
                # 检查Content-Length防止超大响应
                content_length = response.getheader("Content-Length")
                if content_length and int(content_length) > MAX_RESPONSE_SIZE:
                    raise RuntimeError("DeepSeek API response too large")

                body = response.read(MAX_RESPONSE_SIZE + 1).decode("utf-8")
                if len(body) > MAX_RESPONSE_SIZE:
                    raise RuntimeError("DeepSeek API response exceeds size limit")

        except urllib.error.HTTPError as exc:
            # 错误信息脱敏，不返回完整响应
            exc.read()  # 读取但不记录错误体，防止敏感信息泄露
            raise RuntimeError(f"DeepSeek API request failed with HTTP {exc.code}") from exc
        except urllib.error.URLError as exc:
            raise RuntimeError(f"DeepSeek API connection failed") from exc
        except TimeoutError:
            raise RuntimeError("DeepSeek API request timed out") from None

        try:
            data = json.loads(body)
        except json.JSONDecodeError:
            raise RuntimeError("DeepSeek API returned invalid JSON") from None

        try:
            content = data["choices"][0]["message"]["content"]
        except (KeyError, IndexError) as e:
            raise RuntimeError("DeepSeek API returned unexpected response format") from e

        if not content:
            raise RuntimeError("DeepSeek API returned empty content")
        if len(content) > MAX_CONTENT_LENGTH:
            raise RuntimeError("DeepSeek API content too large")

        try:
            return json.loads(content)
        except json.JSONDecodeError:
            raise RuntimeError("DeepSeek API did not return valid JSON content") from None
