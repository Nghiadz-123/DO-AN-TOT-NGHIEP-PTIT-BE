"""Đồng bộ vector của CV và tin tuyển dụng vào bảng cv_embeddings / job_embeddings.

Văn bản embedding được băm (content_hash) và so với bản đã lưu: tin mới / đã sửa / đổi model embedding thì
embedding lại (gộp vào một lần gọi API), còn lại dùng lại vector cũ. Tin được embedding trước khi ứng viên dùng AI
ở ba chỗ: receivers.on_job_changed (nhà tuyển dụng đăng / sửa tin), lệnh `manage.py embed_jobs` (dữ liệu có sẵn) và
khi ứng viên gọi gợi ý (dự phòng nếu hai chỗ trên bị lỗi).
"""
from ..models import CVEmbedding, JobEmbedding
from . import embeddings


def cv_vector(cv, profile: dict) -> list[float]:
    text = embeddings.cv_text(profile)
    digest = embeddings.content_hash(text)
    stored = CVEmbedding.objects.filter(cv=cv).first()
    if stored and stored.content_hash == digest and stored.model == embeddings.current_model():
        return stored.vector
    (vector,), model = embeddings.embed_texts([text])
    CVEmbedding.objects.update_or_create(cv=cv, defaults={'content_hash': digest, 'model': model, 'vector': vector})
    return vector


def job_vectors(jobs) -> dict:
    """{job.pk: vector} cho mọi tin trong `jobs` (đã prefetch job_skills__skill)."""
    return sync_jobs(jobs)[0]


def sync_jobs(jobs) -> tuple[dict, int]:
    """Đảm bảo mọi tin trong `jobs` có vector còn mới. Trả về ({job.pk: vector}, số tin vừa embedding)."""
    texts = {job.pk: embeddings.job_text(job) for job in jobs}
    if not texts:
        return {}, 0
    digests = {pk: embeddings.content_hash(text) for pk, text in texts.items()}
    model = embeddings.current_model()
    vectors = {
        stored.job_id: stored.vector
        for stored in JobEmbedding.objects.filter(job_id__in=texts, model=model)
        if stored.content_hash == digests[stored.job_id]
    }
    missing = [pk for pk in texts if pk not in vectors]
    if missing:
        new_vectors, model = embeddings.embed_texts([texts[pk] for pk in missing])
        JobEmbedding.objects.bulk_create(
            [
                JobEmbedding(job_id=pk, content_hash=digests[pk], model=model, vector=vector)
                for pk, vector in zip(missing, new_vectors)
            ],
            update_conflicts=True,
            unique_fields=['job'],
            update_fields=['content_hash', 'model', 'vector', 'updated_at'],
        )
        vectors.update(zip(missing, new_vectors))
    return vectors, len(missing)
