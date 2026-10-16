"""Chọn LLM provider theo settings (LLM_PROVIDER). Đổi provider bằng cấu hình, không phải sửa code nghiệp vụ.

Services luôn gọi `factory.get_llm()` (qua module) để test thay được bằng provider giả.
"""
from functools import lru_cache

from django.conf import settings

from .base import LLMProvider
from .exceptions import AINotConfiguredError

SUPPORTED_PROVIDERS = ('gemini',)


def get_llm() -> LLMProvider:
    return _build(
        settings.LLM_PROVIDER,
        settings.GEMINI_API_KEY,
        tuple(settings.GEMINI_CHAT_MODELS),
        settings.GEMINI_EMBED_MODEL,
        settings.AI_REQUEST_TIMEOUT,
    )


@lru_cache(maxsize=4)  # một client cho mỗi cấu hình (lỗi cấu hình không bị cache)
def _build(provider, api_key, chat_models, embed_model, timeout) -> LLMProvider:
    if provider not in SUPPORTED_PROVIDERS:
        raise AINotConfiguredError(f'LLM_PROVIDER "{provider}" chưa được hỗ trợ (hiện chỉ có gemini).')
    from .providers.gemini_provider import GeminiProvider

    return GeminiProvider(api_key=api_key, chat_models=list(chat_models), embed_model=embed_model, timeout=timeout)
