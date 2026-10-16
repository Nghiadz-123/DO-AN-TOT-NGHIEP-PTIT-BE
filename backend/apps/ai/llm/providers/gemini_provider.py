"""Gemini qua thư viện google-genai, cùng cách gọi với prototype TestAI/llm.py.

- GEMINI_CHAT_MODEL có thể gồm nhiều model (cách nhau dấu phẩy): model đầu quá tải, hết quota hoặc không
  tồn tại thì tự chuyển sang model sau.
- Lỗi tạm thời (429, 5xx) được thử lại với thời gian chờ tăng dần; số lần ít hơn TestAI vì ứng viên đang chờ
  response của API.
"""
import logging
import time

import httpx
from google import genai
from google.genai import errors, types

from ..base import JSONResult, LLMProvider
from ..exceptions import AIError, AIInvalidOutputError, AINotConfiguredError, AIUnavailableError
from ..schemas import parse_json

logger = logging.getLogger(__name__)

RETRY_STATUS = {429, 500, 502, 503, 504}  # quá tải / vượt quota tạm thời
FALLBACK_STATUS = RETRY_STATUS | {404}  # 404: model không tồn tại với API key này
RETRY_BASE_DELAY = 2  # giây, nhân đôi sau mỗi lần thử lại
ATTEMPTS_WITH_FALLBACK = 2  # còn model dự phòng thì không chờ lâu
ATTEMPTS_LAST_MODEL = 3
# batchEmbedContents nhận tối đa 100 đoạn văn bản mỗi lần gọi
EMBED_BATCH_SIZE = 100


class GeminiProvider(LLMProvider):
    def __init__(self, *, api_key: str, chat_models: list[str], embed_model: str, timeout: int):
        if not api_key:
            raise AINotConfiguredError()
        if not chat_models:
            raise AINotConfiguredError('Chưa khai báo model chat (GEMINI_CHAT_MODEL trong backend/.env).')
        self.chat_models = list(chat_models)
        self.embed_model = embed_model
        self._client = genai.Client(api_key=api_key, http_options=types.HttpOptions(timeout=timeout * 1000))

    def generate_json(self, system: str, user: str) -> JSONResult:
        config = types.GenerateContentConfig(
            system_instruction=system,
            response_mime_type='application/json',
            temperature=0.2,
            # Không dùng function calling: tắt để SDK không ghi log "AFC is enabled" mỗi lần gọi
            automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
        )
        response, model = self._generate(user, config)
        try:
            data = parse_json(response.text)
        except ValueError as exc:
            logger.warning('Model %s trả về JSON không hợp lệ: %.300s', model, response.text)
            raise AIInvalidOutputError() from exc
        return JSONResult(data=data, model=model)

    def embed(self, texts: list[str]) -> list[list[float]]:
        vectors = []
        for start in range(0, len(texts), EMBED_BATCH_SIZE):
            batch = texts[start:start + EMBED_BATCH_SIZE]
            try:
                response = _with_retry(
                    self._client.models.embed_content, attempts=ATTEMPTS_LAST_MODEL,
                    model=self.embed_model, contents=batch,
                )
            except errors.APIError as exc:
                raise _translate(exc, self.embed_model) from exc
            except httpx.HTTPError as exc:
                raise AIUnavailableError() from exc
            vectors.extend(list(embedding.values) for embedding in response.embeddings)
        if len(vectors) != len(texts):
            raise AIInvalidOutputError()
        return vectors

    def _generate(self, contents, config):
        for index, model in enumerate(self.chat_models):
            is_last = index == len(self.chat_models) - 1
            try:
                response = _with_retry(
                    self._client.models.generate_content,
                    attempts=ATTEMPTS_LAST_MODEL if is_last else ATTEMPTS_WITH_FALLBACK,
                    model=model, contents=contents, config=config,
                )
                return response, model
            except errors.APIError as exc:
                if is_last or exc.code not in FALLBACK_STATUS:
                    raise _translate(exc, model) from exc
                logger.warning('[AI] %s lỗi %s, chuyển sang %s', model, exc.code, self.chat_models[index + 1])
            except httpx.HTTPError as exc:  # hết thời gian chờ / lỗi mạng
                if is_last:
                    raise AIUnavailableError() from exc
                logger.warning('[AI] %s lỗi mạng (%s), chuyển sang %s', model, exc, self.chat_models[index + 1])


def _with_retry(fn, *, attempts: int, **kwargs):
    """Gọi lại với thời gian chờ tăng dần (2, 4s...) khi server báo lỗi tạm thời."""
    for attempt in range(1, attempts + 1):
        try:
            return fn(**kwargs)
        except errors.APIError as exc:
            if exc.code not in RETRY_STATUS or attempt == attempts:
                raise
            wait = RETRY_BASE_DELAY * 2 ** (attempt - 1)
            logger.warning('[AI] Lỗi %s, thử lại sau %ss (%s/%s)', exc.code, wait, attempt, attempts - 1)
            time.sleep(wait)


def _translate(exc: errors.APIError, model: str) -> AIError:
    """Đổi lỗi của Gemini thành lỗi có thông điệp cho người dùng."""
    message = str(exc)
    if exc.code in (401, 403) or (exc.code == 400 and 'api key' in message.lower()):
        return AINotConfiguredError('API key Gemini không hợp lệ hoặc không có quyền dùng model đã cấu hình.')
    if exc.code == 404:
        return AINotConfiguredError(f'Không tìm thấy model Gemini "{model}". Kiểm tra cấu hình model trong backend/.env.')
    if exc.code in RETRY_STATUS:
        return AIUnavailableError()
    logger.error('Gemini báo lỗi %s (model %s): %s', exc.code, model, message)
    return AIError()
