# API AI cho ứng viên: chấm điểm CV, gợi ý sửa CV, gợi ý việc làm

Module `apps/ai` đưa pipeline của prototype `TestAI/` vào hệ thống, dùng **cùng model và API key Gemini**, theo
khuôn chung `urls → views (mỏng) → serializers → services / selectors → models`.

Luồng của ứng viên:

1. Tải CV lên (app `cvs` bóc tách văn bản, không dùng AI) → bấm **Chấm điểm bằng AI**: điểm 0-100 theo 5 tiêu chí,
   điểm mạnh / điểm cần cải thiện; đồng thời AI bóc tách thông tin CV (kỹ năng, kinh nghiệm, học vấn...).
2. **Gợi ý sửa CV**: AI đối chiếu CV với tin mục tiêu (nếu chọn) và 20 việc làm phù hợp nhất với CV, chỉ ra cần
   sửa gì kèm ví dụ trước / sau và từ khóa còn thiếu.
3. **Việc làm phù hợp**: xếp các tin đang tuyển theo độ phù hợp với CV; bấm **AI đánh giá chi tiết** để AI chấm
   riêng một tin.

Swagger: `http://localhost:8000/api/docs/`, nhóm **Candidate - AI**.

---

## 1. Phạm vi và giả định

- Chỉ phía **ứng viên**, gồm 3 chức năng trên. Chưa làm: AI xếp hạng ứng viên cho nhà tuyển dụng
  (`services/candidate_matching.py`, `prompts/candidate_matching.py` vẫn rỗng), AI đánh giá nhanh khi bấm ứng tuyển,
  provider OpenAI (`providers/openai_provider.py` rỗng).
- AI chỉ phân tích CV app `cvs` đã đọc được chữ (`parse_status = completed`). CV dạng ảnh scan chưa được Gemini đọc
  thay như `TestAI/llm.py pdf_to_text`.
- Gọi Gemini **đồng bộ** trong request (chưa có Celery), mỗi thao tác mất vài giây. Kết quả **lưu DB**: mở lại trang
  chỉ đọc DB, không gọi AI lại.
- Vector lưu ngay trong PostgreSQL (JSON), cosine tính bằng Python như `TestAI/db.py`, đủ cho vài trăm CV / tin.
  Chưa dùng ChromaDB / pgvector.
- Tin tuyển dụng đã có cấu trúc trong DB (kỹ năng bắt buộc / ưu tiên, cấp bậc, số năm kinh nghiệm) nên **không gọi
  LLM chuẩn hóa JD** như `TestAI ingest_jd`, chỉ tạo embedding.
- Prompt giữ nguyên TestAI (schema, thang điểm, trọng số). Chỉ sửa: ví dụ và mô tả tiêu chí cho mọi ngành nghề,
  trả lời tiếng Việt, gợi ý gọi tin bằng chức danh thay vì "JD #1".

## 2. Cấu hình (`backend/.env`)

Cùng tên biến với `TestAI/.env`:

| Biến | Mặc định | Ý nghĩa |
|---|---|---|
| `LLM_PROVIDER` | `gemini` | Hiện chỉ hỗ trợ `gemini` |
| `GEMINI_API_KEY` | (trống) | Key Gemini. **Chỉ điền vào `.env`**, không ghi vào `.env.example` |
| `GEMINI_CHAT_MODEL` | `gemini-3.5-flash-lite,gemini-3.1-flash-lite,gemini-3.6-flash` | Model chat; model đầu quá tải / hết quota / không tồn tại thì tự chuyển model sau |
| `GEMINI_EMBED_MODEL` | `gemini-embedding-001` | Model embedding |
| `AI_REQUEST_TIMEOUT` | `60` | Giây chờ tối đa mỗi lần gọi Gemini |

Cài thư viện: `pip install -r requirements.txt` (thêm `google-genai`), rồi `python manage.py migrate` (4 bảng mới) và
`python manage.py embed_jobs` (embedding sẵn các tin đang tuyển, xem mục 4.3).
Lỗi tạm thời (429, 5xx) được thử lại 2-3 lần, chờ 2s rồi 4s. Mỗi ứng viên gọi tối đa **60 lần / giờ** (throttle `ai`).

## 3. Kiến trúc (đối chiếu TestAI)

| TestAI | `apps/ai` |
|---|---|
| `llm.py` (`GeminiLLM`, retry, fallback model, `_parse_json`) | `llm/providers/gemini_provider.py`, `llm/base.py` (interface), `llm/factory.py`, `llm/exceptions.py`, `llm/schemas.py` |
| `prompts.py` | `prompts/cv_analysis.py`, `prompts/cv_suggestion.py`, `prompts/job_recommendation.py` |
| `pipeline.ingest_cv` (bước LLM parse) | `services/cv_analysis.ensure_profile` |
| `pipeline.score_cv` | `services/cv_analysis.score_cv` |
| `pipeline.suggest_cv` | `services/cv_suggestion.suggest_cv` |
| `pipeline.recommend_jobs`, `_match(rerank=True)` | `services/job_recommendation.recommend_jobs`, `evaluate_job` |
| `cv_to_embed_text`, `jd_to_embed_text`, `db.top_k_similar` | `vectorstore/embeddings.py`, `vectorstore/indexer.py`, `vectorstore/client.py` |
| `_skill_overlap` (so trùng chuỗi) | `nlp/skill_extractor.py` (tên gọi khác trong danh mục, bỏ dấu, khớp trọn từ) |
| `extract.py` | app `cvs` (đã có từ giai đoạn 2) |

- `llm/schemas.py` chuẩn hóa JSON model trả về: ép kiểu, kẹp điểm trong thang, bỏ phần tử rỗng. Chỉ báo lỗi
  `ai_invalid_output` khi thiếu phần cốt lõi (vd. không có điểm nào).
- `receivers.py`: CV bị xóa (`cvs.signals.cv_deleted`) thì xóa luôn kết quả AI và vector của CV đó; tin được đăng /
  sửa (`jobs.signals.job_published`, `job_updated`) thì embedding tin đó.
- `management/commands/embed_jobs.py`: embedding các tin đang tuyển có sẵn (xem mục 4.3).
- Test thay LLM bằng provider giả (`factory.get_llm`); `settings/test.py` để `GEMINI_API_KEY` rỗng nên test không
  bao giờ gọi Gemini thật.

## 4. Chức năng

### 4.1. Chấm điểm CV

LLM đọc văn bản CV (tối đa 20.000 ký tự), chấm 5 tiêu chí (`prompts/cv_analysis.SCORE_CRITERIA`):

| Tiêu chí | Tối đa | Nội dung |
|---|---|---|
| `completeness` — Đầy đủ thông tin | 20 | Liên hệ, học vấn, kinh nghiệm, kỹ năng |
| `experience` — Kinh nghiệm | 25 | Độ liên quan, có kết quả đo lường được |
| `skills` — Kỹ năng | 20 | Rõ ràng, phù hợp chức danh |
| `projects` — Dự án / thành tích | 15 | Dự án, thành tích, hoạt động nổi bật; vai trò, công cụ, kết quả |
| `presentation` — Trình bày | 20 | Ngắn gọn, nhất quán, động từ hành động |

Tổng điểm được **cộng lại từ các tiêu chí** (không dùng `total` model tự cộng). Nếu chưa có thông tin trích xuất, AI
bóc tách song song cùng lúc chấm điểm (2 lời gọi chạy đồng thời); bóc tách lỗi không làm hỏng kết quả chấm điểm.

### 4.2. Gợi ý sửa CV

Prompt gồm văn bản CV + tin mục tiêu (nếu có, đánh dấu "MỤC TIÊU", đứng đầu) + **20 việc làm được gợi ý cho CV**:
đúng danh sách, điểm và thứ tự của trang "Việc làm phù hợp" (mục 4.3), thay vì 3 tin gần nhất như TestAI. Mỗi tin
gửi kèm:

- thông tin tin (chức danh, cấp bậc, kỹ năng bắt buộc / ưu tiên, yêu cầu, mô tả; tin tham chiếu rút gọn còn 8 dòng
  mô tả / yêu cầu, tin mục tiêu 20 dòng);
- `match_score`, `cv_has_skills`, `cv_missing_skills` (kết quả so khớp embedding + kỹ năng);
- cuối prompt: **kỹ năng CV còn thiếu lặp lại nhiều nhất** trong tin mục tiêu và các tin có điểm từ 50 (tin điểm thấp,
  thường khác ngành, không tính để AI không khuyên học kỹ năng của ngành khác).

Prompt yêu cầu mỗi gợi ý bám vào một đoạn cụ thể của CV và một yêu cầu cụ thể của tin (không gợi ý chung chung), ưu
tiên kỹ năng lặp lại ở nhiều tin điểm cao. Mỗi gợi ý có `section`, `issue`, `suggestion`, `example_before` /
`example_after`, `priority` (high / medium / low) và `job_ids` (tin là căn cứ). Kèm `missing_keywords`: từ khóa có
trong tin nhưng CV chưa thể hiện. Không có tin nào thì AI gợi ý theo chất lượng CV nói chung.

### 4.3. Gợi ý việc làm

1. **Lọc nhanh** (mỗi lần mở trang): embedding hồ sơ CV và từng tin đang tuyển (cùng một khuôn văn bản: vị trí,
   kinh nghiệm, kỹ năng...). Tính cosine `sim` và `skill_overlap`: tỉ lệ kỹ năng bắt buộc của tin có trong CV; tin
   chỉ có kỹ năng ưu tiên thì tính trên tất cả; tin không khai kỹ năng = 0,5.
   **Điểm = 60·sim + 40·skill_overlap** (công thức TestAI khi không rerank).
2. **AI đánh giá chi tiết** (khi ứng viên bấm, từng tin): LLM đọc hồ sơ CV (đã bỏ email / số điện thoại) + tin, trả
   điểm 0-100, kỹ năng khớp / thiếu, nhận xét. **Điểm = 0,5·llm + 30·sim + 20·skill_overlap** (công thức TestAI khi
   rerank).

Vector của tin được băm theo nội dung (`content_hash`): tin mới hoặc vừa sửa thì embedding lại (gộp nhiều tin trong
một lần gọi API), các tin khác dùng lại vector cũ. Kết quả AI đánh giá hết hiệu lực khi CV được đọc lại hoặc nội dung
tin thay đổi.

**Embedding tin tuyển dụng trước khi ứng viên dùng AI** (để ứng viên đầu tiên không phải chờ cả loạt tin):

1. **Dữ liệu có sẵn**: chạy một lần `python manage.py embed_jobs` (tin nạp từ `seed.sql`, `seed_demo` không đi qua
   tín hiệu đăng tin). Chạy lại được: tin đã có vector còn mới thì bỏ qua.
2. **Tin mới / tin được sửa**: `receivers.on_job_changed` nghe `job_published`, `job_updated` của app `jobs` và
   embedding ngay sau commit. Chỉ embedding tin đang tuyển; sửa tin mà văn bản embedding không đổi (vd. chỉ đổi hạn
   nộp, lương) thì không gọi API. Lỗi (Gemini quá tải, hết quota, chưa có key) chỉ ghi log, không làm hỏng việc đăng
   tin.
3. **Dự phòng**: tin nào chưa có vector thì được embedding ở lần ứng viên gọi gợi ý đầu tiên.

Vector của CV chỉ được tạo khi chính ứng viên đó dùng gợi ý việc làm / gợi ý sửa CV.

## 5. Bảng dữ liệu (migration `ai/0001_initial`)

| Bảng | Nội dung |
|---|---|
| `cv_analyses` | Một dòng / CV: thông tin trích xuất (`profile`, `source_hash` của văn bản CV), điểm (`score_total`, `score_breakdown`, `strengths`, `weaknesses`), gợi ý (`suggestions`, `missing_keywords`, `reference_jobs`, `target_job`) |
| `cv_embeddings` | Vector hồ sơ CV (`content_hash`, `model`, `vector`) |
| `job_embeddings` | Vector tin tuyển dụng |
| `match_results` | AI đánh giá CV - tin (`score`, `matched_skills`, `missing_skills`, `reason`, `cv_hash`, `job_hash`), duy nhất theo (cv, job) |

## 6. Danh sách API

Tất cả dưới `/api/v1/`, chỉ cho **ứng viên**, cần `Authorization: Bearer <access>`. CV của người khác → 404.

| Method | Đường dẫn | Mô tả |
|---|---|---|
| GET | `candidate/cv-analyses/` | Kết quả AI đã lưu của các CV của tôi (không gọi AI, không phân trang) |
| POST | `candidate/cvs/{cv_id}/analysis/score/` | AI chấm điểm CV |
| POST | `candidate/cvs/{cv_id}/analysis/suggestions/` | AI gợi ý sửa CV. Body `{"job_id": "<uuid>" \| null}` |
| GET | `candidate/cvs/{cv_id}/recommended-jobs/` | Việc làm phù hợp, điểm cao trước. `?limit=1-50` (mặc định 20) |
| POST | `candidate/cvs/{cv_id}/recommended-jobs/{job_id}/evaluate/` | AI đánh giá chi tiết CV với một tin đang tuyển |

Kết quả phân tích một CV (`GET cv-analyses` trả danh sách; hai API POST đầu trả một phần tử):

```json
{
  "cv_id": "…",
  "profile": {"full_name": "Nguyễn Văn An", "title": "Nhân viên kinh doanh", "years_of_experience": 1,
              "skills": ["bán hàng", "đàm phán", "chăm sóc khách hàng"], "experiences": [ … ], "educations": [ … ], "…": "…"},
  "score": {
    "total": 78,
    "breakdown": [{"key": "completeness", "label": "Đầy đủ thông tin", "score": 20, "max": 20}, "…"],
    "strengths": ["Kinh nghiệm có số liệu cụ thể (đạt 115% chỉ tiêu)"],
    "weaknesses": ["Thiếu phần dự án / thành tích nổi bật"],
    "scored_at": "2026-10-15T21:33:00+07:00"
  },
  "suggestions": {
    "items": [{"section": "Kinh nghiệm", "issue": "…", "suggestion": "…", "example_before": "…", "example_after": "…",
               "priority": "high", "job_ids": ["…"]}],
    "missing_keywords": ["đi gặp khách hàng"],
    "reference_jobs": [{"id": "…", "title": "Nhân viên kinh doanh khách hàng doanh nghiệp", "company": "…", "score": 88, "is_target": true}],
    "target_job_id": "…",
    "suggested_at": "…"
  },
  "updated_at": "…"
}
```

Chức năng chưa chạy thì `profile` / `score` / `suggestions` là `null`.

Một việc làm được gợi ý:

```json
{
  "job": { "…": "giống danh sách tin công khai (jobs/)" },
  "score": 88,
  "similarity": 0.80,
  "skill_overlap": 1.0,
  "matched_skills": ["Bán hàng", "Đàm phán"],
  "missing_skills": [],
  "reasons": ["Nội dung CV tương đồng 80% với mô tả công việc", "Đáp ứng 4/4 kỹ năng bắt buộc: …"],
  "ai_evaluation": {"score": 90, "matched_skills": ["…"], "missing_skills": ["…"], "reason": "…", "evaluated_at": "…"}
}
```

`ai_evaluation` là `null` khi chưa bấm AI đánh giá (hoặc kết quả đã hết hiệu lực).

### Lỗi

| HTTP | `code` | Khi nào |
|---|---|---|
| 409 | `cv_not_ready` | CV chưa đọc được nội dung (đang xử lý / thất bại) |
| 404 | `not_found` | CV không thuộc ứng viên; tin mục tiêu không tồn tại / là bản nháp; tin cần đánh giá không còn tuyển |
| 503 | `ai_not_configured` | Thiếu / sai `GEMINI_API_KEY`, model không tồn tại |
| 503 | `ai_unavailable` | Mọi model quá tải / hết quota / lỗi mạng sau khi thử lại |
| 502 | `ai_invalid_output` | Model trả về JSON không đúng cấu trúc |
| 429 | `throttled` | Vượt 60 lần gọi / giờ |

## 7. Frontend

- `src/api/aiApi.js` gọi các API trên; `src/api/adapters.js` (`toCVAnalysis`, `toJobRecommendation`).
- `/cv-analysis`: tab **Chấm điểm**, **Gợi ý sửa CV** (tin mục tiêu qua `?jobId=`), **Thông tin AI trích xuất**.
  Tải CV lên xong tự chấm điểm. URL giữ `?cvId=&tab=` để trang khác dẫn link tới.
- `/recommended-jobs`: chọn CV, lọc theo điểm, nút **AI đánh giá chi tiết** và **Gợi ý sửa CV theo tin này**.
- `/cv`: cột **Điểm AI**; trang chi tiết tin: hộp "Mẹo từ AI" dẫn tới gợi ý sửa CV theo tin đó.
- Cờ `FEATURES.candidateAi` (mặc định bật, ẩn bằng `VITE_FEATURE_AI=false`). Phần AI của nhà tuyển dụng vẫn ẩn
  (`FEATURES.ai`).

## 8. Kiểm thử

- `pytest apps/ai`: 21 test với LLM giả (chấm điểm, chuẩn hóa output, CV chưa sẵn sàng, chưa cấu hình key, quyền truy
  cập, xếp hạng việc làm, cache vector, AI đánh giá, gợi ý theo tin mục tiêu, xóa CV, embedding khi đăng / sửa tin,
  lệnh `embed_jobs`).
- Đã chạy thật với Gemini (`gemini-3.5-flash-lite`) trên dữ liệu `seed_demo`: chấm điểm ~3-18 giây, gợi ý việc làm
  lần đầu ~2 giây (embedding 17-18 tin), AI đánh giá ~1 giây, gợi ý sửa CV ~3 giây.

## 9. Hạn chế / hướng phát triển

- Chạy đồng bộ: nhiều người dùng cùng lúc thì nên chuyển sang Celery (`tasks.py`) và để frontend hỏi trạng thái.
- Cosine tính trên toàn bộ tin đang tuyển mỗi lần gợi ý: dữ liệu lớn thì thay bằng pgvector / ChromaDB (giữ nguyên
  `vectorstore/client.py`).
- Trọng số 60/40 và 0,5/30/20 là khởi điểm của TestAI, nên gán nhãn vài cặp CV - tin để chỉnh lại.
- CV dạng ảnh scan: có thể thêm bước cho Gemini đọc thẳng PDF (như `TestAI pdf_to_text`) trong module AI.
