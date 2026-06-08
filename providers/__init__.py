from config import settings
from providers.base import VisionProvider
from providers.mock import MockVisionProvider
from providers.qwen import QwenVisionProvider


def get_provider(
    provider_name: str | None = None,
    api_key: str | None = None,
    model: str | None = None,
    base_url: str | None = None,
) -> VisionProvider:
    name = (provider_name or settings.ai_provider).lower()
    if name == "mock":
        return MockVisionProvider()
    if name == "qwen":
        return QwenVisionProvider(api_key=api_key, model=model, base_url=base_url)
    raise ValueError(f"未知 AI 提供商: {name}。可选: qwen, mock")
