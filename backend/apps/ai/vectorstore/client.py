"""Truy vấn vector.

Quy mô đồ án (vài trăm CV / tin) nên vector lưu ngay trong PostgreSQL (bảng cv_embeddings, job_embeddings) và
cosine tính bằng Python, như db.top_k_similar của TestAI. Khi dữ liệu lớn có thể thay bằng pgvector / ChromaDB mà
giữ nguyên các hàm dưới đây.
"""
import math


def cosine(a, b) -> float:
    """Vector đã chuẩn hóa độ dài 1 (embeddings._unit) nên cosine chính là tích vô hướng."""
    if len(a) != len(b):
        return 0.0
    return math.sumprod(a, b)


def top_k(query, vectors: dict, k: int | None = None) -> list[tuple[object, float]]:
    """vectors: {khóa: vector}. Trả về [(khóa, cosine)] giảm dần; k=None: tất cả."""
    scored = sorted(((key, cosine(query, vector)) for key, vector in vectors.items()), key=lambda kv: -kv[1])
    return scored if k is None else scored[:k]
