"""JD Image Parser — extract JD text from a screenshot using a vision API.

Reads VISION_API_KEY and VISION_API_PROVIDER from .env.
Falls back gracefully if no key is configured.
"""

from __future__ import annotations

import os
from pathlib import Path


def _load_env() -> tuple[str | None, str | None, str | None]:
    """Load vision API config from .env files (project root, then user home).

    Returns (api_key, provider, base_url).
    """
    candidates = [
        Path(__file__).resolve().parent.parent.parent / ".env",
        Path.home() / ".env",
    ]
    for env_path in candidates:
        if env_path.exists():
            lines = env_path.read_text(encoding="utf-8").splitlines()
            key = None
            provider = None
            base_url = None
            for line in lines:
                line = line.strip()
                if line.startswith("VISION_API_KEY="):
                    key = line.split("=", 1)[1].strip().strip("\"'")
                elif line.startswith("VISION_API_PROVIDER="):
                    provider = line.split("=", 1)[1].strip().strip("\"'")
                elif line.startswith("DEEPSEEK_API_BASE=") or line.startswith("QWEN_API_BASE="):
                    base_url = line.split("=", 1)[1].strip().strip("\"'")
            if key:
                return key, provider, base_url

    # Fall back to environment variables
    return (
        os.environ.get("VISION_API_KEY"),
        os.environ.get("VISION_API_PROVIDER"),
        os.environ.get("DEEPSEEK_API_BASE"),
    )


def parse_jd_image(image_path: str) -> str:
    """Extract JD text from a screenshot using the configured vision API.

    Returns
    -------
    str
        Extracted JD text.

    Raises
    ------
    RuntimeError
        If no vision API key is configured or parsing fails.
    """
    api_key, provider, base_url = _load_env()

    if not api_key:
        raise RuntimeError(
            "No VISION_API_KEY found. "
            "To use screenshot parsing, create a .env file with:\n"
            "  VISION_API_KEY=sk-your-key\n"
            "  VISION_API_PROVIDER=anthropic\n"
            "Without a configured API key, paste the JD text manually instead."
        )

    provider = (provider or "openai").lower().strip()

    # DeepSeek uses OpenAI-compatible API
    if provider == "deepseek" or (provider == "openai" and base_url and "deepseek" in base_url):
        return _parse_with_openai(image_path, api_key, base_url or "https://api.deepseek.com")
    elif provider == "anthropic":
        return _parse_with_anthropic(image_path, api_key)
    elif provider == "openai":
        return _parse_with_openai(image_path, api_key)
    else:
        raise ValueError(f"Unsupported vision API provider: {provider}")


def _parse_with_anthropic(image_path: str, api_key: str) -> str:
    """Parse JD image using Anthropic Claude vision API."""
    import httpx
    import base64

    with open(image_path, "rb") as f:
        image_data = base64.b64encode(f.read()).decode("utf-8")

    # Detect media type from extension
    ext = Path(image_path).suffix.lower()
    media_type = {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".webp": "image/webp",
    }.get(ext, "image/png")

    response = httpx.post(
        "https://api.anthropic.com/v1/messages",
        headers={
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        json={
            "model": "claude-sonnet-4-20250514",
            "max_tokens": 4096,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": (
                                "You are a precise OCR tool. "
                                "Extract ALL text from this job description screenshot "
                                "in its original language. Preserve formatting, section headers, "
                                "bullet points, and numbers as much as possible. "
                                "Output ONLY the extracted text, no commentary."
                            ),
                        },
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": media_type,
                                "data": image_data,
                            },
                        },
                    ],
                }
            ],
        },
    )
    response.raise_for_status()
    data = response.json()
    text_content = ""
    for block in data.get("content", []):
        if block.get("type") == "text":
            text_content += block.get("text", "")
    return text_content.strip()


def _parse_with_openai(image_path: str, api_key: str, base_url: str | None = None) -> str:
    """Parse JD image using an OpenAI-compatible vision API.

    Supports OpenAI GPT-4o, DeepSeek, and any OpenAI-compatible endpoint.
    """
    import httpx
    import base64

    endpoint = (base_url or "https://api.openai.com").rstrip("/")
    url = f"{endpoint}/v1/chat/completions"

    with open(image_path, "rb") as f:
        image_data = base64.b64encode(f.read()).decode("utf-8")

    ext = Path(image_path).suffix.lower()
    media_type = {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".webp": "image/webp",
    }.get(ext, "image/png")

    data_uri = f"data:{media_type};base64,{image_data}"

    payload = {
        "model": "deepseek-chat",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": (
                            "You are a precise OCR tool. "
                            "Extract ALL text from this job description screenshot "
                            "in its original language. Preserve formatting, section headers, "
                            "bullet points, and numbers as much as possible. "
                            "Output ONLY the extracted text, no commentary."
                        ),
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url": data_uri, "detail": "high"},
                    },
                ],
            }
        ],
    }

    # DeepSeek doesn't support stream mode for vision
    if "deepseek" in endpoint:
        payload["stream"] = False

    response = httpx.post(
        url,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json=payload,
        timeout=60,
    )
    response.raise_for_status()
    data = response.json()
    text_content = ""
    for choice in data.get("choices", []):
        if choice.get("message"):
            text_content += choice["message"].get("content", "")
    return text_content.strip()
