"""DeepSeek provider adapter."""

import json
import os
import urllib.error
import urllib.request


class DeepSeekClient:
    """Minimal DeepSeek chat client using the OpenAI-compatible API."""

    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None,
        base_url: str = "https://api.deepseek.com",
        timeout_seconds: int = 60,
    ) -> None:
        self.api_key = api_key or os.environ.get("DEEPSEEK_API_KEY")
        self.model = model or os.environ.get("DEEPSEEK_MODEL", "deepseek-v4-flash")
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds

    def chat_json(self, system_prompt: str, user_prompt: str, max_tokens: int = 1200) -> dict:
        if not self.api_key:
            raise RuntimeError("DEEPSEEK_API_KEY is not set.")

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "response_format": {"type": "json_object"},
            "max_tokens": max_tokens,
            "stream": False,
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
                body = response.read().decode("utf-8")
        except urllib.error.HTTPError as exc:
            error_body = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"DeepSeek API HTTP {exc.code}: {error_body}") from exc
        except urllib.error.URLError as exc:
            raise RuntimeError(f"DeepSeek API request failed: {exc.reason}") from exc

        data = json.loads(body)
        content = data["choices"][0]["message"]["content"]
        if not content:
            raise RuntimeError("DeepSeek API returned empty JSON content.")
        return json.loads(content)
