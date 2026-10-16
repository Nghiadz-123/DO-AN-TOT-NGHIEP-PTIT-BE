"""Interface chung cho LLM provider. Code nghiệp vụ (services) chỉ dùng interface này, không gọi SDK trực tiếp."""
from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class JSONResult:
    data: dict
    model: str  # model đã trả lời (có thể là model dự phòng)


class LLMProvider(ABC):
    embed_model: str = ''

    @abstractmethod
    def generate_json(self, system: str, user: str) -> JSONResult:
        """Gửi prompt (system + nội dung), trả về JSON object model sinh ra."""

    @abstractmethod
    def embed(self, texts: list[str]) -> list[list[float]]:
        """Embedding cho từng đoạn văn bản, cùng thứ tự với `texts`."""
