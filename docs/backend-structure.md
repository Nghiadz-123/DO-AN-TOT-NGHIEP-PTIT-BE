# Cấu trúc thư mục Backend

Stack: Django + Django REST Framework + PostgreSQL, Celery + Redis (xử lý bất đồng bộ các tác vụ AI), ChromaDB (vector store), LLM API (OpenAI / Gemini).

> **Trạng thái**: giai đoạn 1 (chức năng Nhà tuyển dụng) đã triển khai trong `config`, `common`, `accounts`, `catalog`, `employers`, `jobs`, `applications` — xem [employer-api.md](employer-api.md). Giai đoạn 2 (chức năng Ứng viên: đăng ký, hồ sơ, tải lên CV, ứng tuyển) đã triển khai trong `candidates`, `cvs` và phần `candidate/applications` của `applications` — xem [candidate-api.md](candidate-api.md). Mở rộng: tìm ứng viên công khai CV và ứng viên phù hợp với tin (`talents`), thư mời ứng tuyển (`invitations`) — xem [talent-invitation-api.md](talent-invitation-api.md). AI cho ứng viên (`ai`: chấm điểm CV, gợi ý sửa CV, gợi ý việc làm bằng Gemini) — xem [ai-api.md](ai-api.md); các file còn rỗng trong `ai/` (xếp hạng ứng viên cho NTD, OpenAI, Celery task) thuộc giai đoạn sau. Không chạy `django-admin startproject` / `startapp` đè lên; điền nội dung trực tiếp vào các file đã có.
>
> Ngoài các file chuẩn bên dưới, một số app có thêm: `workflow.py` (bảng chuyển trạng thái), `signals.py` (domain event cho module khác lắng nghe), `permissions.py`; `accounts/registry.py` (app theo vai trò đăng ký phần `profile` của `/auth/me/`).

## Tổng quan

```text
DO-AN-TOT-NGHIEP-PTIT-BE/
├── backend/
│   ├── manage.py
│   ├── requirements.txt
│   ├── .env.example
│   ├── Dockerfile
│   ├── conftest.py
│   ├── config/                 # Cấu hình Django project
│   ├── common/                 # Thành phần dùng chung
│   └── apps/                   # Các module nghiệp vụ
│       ├── accounts/           # Authentication
│       ├── catalog/            # Danh mục dùng chung (kỹ năng, ngành nghề, tỉnh/thành)
│       ├── candidates/         # Ứng viên
│       ├── employers/          # Nhà tuyển dụng / công ty
│       ├── cvs/                # CV
│       ├── jobs/               # Tin tuyển dụng
│       ├── applications/       # Ứng tuyển (ATS)
│       ├── favorites/          # Việc làm / công ty ứng viên yêu thích
│       ├── invitations/        # Thư mời ứng tuyển: NTD mời ứng viên nộp hồ sơ vào tin
│       ├── talents/            # NTD chủ động tìm ứng viên: kho CV công khai, ứng viên phù hợp với tin
│       └── ai/                 # AI / LLM
├── database/
│   └── schema.sql
├── docs/
├── docker-compose.yml
└── README.md
```

## Gốc `backend/`

| File | Trách nhiệm |
|---|---|
| `manage.py` | Entry point lệnh Django (migrate, runserver, ...). |
| `requirements.txt` | Danh sách thư viện Python. |
| `.env.example` | Mẫu biến môi trường (DB, Redis, API key LLM, ...). Commit file này, **không** commit `.env`. |
| `Dockerfile` | Đóng gói image backend dùng cho cả API và Celery worker. |
| `conftest.py` | Fixture pytest dùng chung (user mẫu, API client đã đăng nhập, mock LLM). |

## `config/` — Django project

| File | Trách nhiệm |
|---|---|
| `settings/base.py` | Cấu hình chung: INSTALLED_APPS, DRF, JWT, database, Celery, AI. |
| `settings/dev.py` | Cấu hình môi trường dev: DEBUG, CORS mở. |
| `settings/prod.py` | Cấu hình production: bảo mật, logging, static/media, allowed hosts. |
| `settings/test.py` | Cấu hình khi chạy test: mock LLM, Celery chạy đồng bộ. |
| `urls.py` | URL gốc: admin, docs API (Swagger), include `api/v1/`. |
| `api_urls.py` | Gom `urls.py` của các app vào `api/v1/` để quản lý versioning. |
| `celery.py` | Khởi tạo Celery app. |
| `asgi.py` / `wsgi.py` | Entry point cho server production (gunicorn / uvicorn). |

## `common/` — Dùng chung, không chứa nghiệp vụ

| File | Trách nhiệm |
|---|---|
| `models.py` | Abstract model gốc (`created_at`, `updated_at`, UUID, soft delete). |
| `permissions.py` | Permission dùng chung: `IsCandidate`, `IsEmployer`, `IsOwner`, ... |
| `pagination.py` | Phân trang chuẩn cho mọi API. |
| `exceptions.py` | Exception handler để mọi response lỗi có cùng format. |
| `storage.py` | Abstraction lưu file (local khi dev, S3/MinIO khi production). |
| `validators.py` | Validator dùng chung (kích thước file, định dạng, ...). |
| `utils.py` | Hàm tiện ích nhỏ, không phụ thuộc app nào. |

## `apps/` — Các module nghiệp vụ

### File chuẩn trong mỗi app

| File | Trách nhiệm |
|---|---|
| `apps.py` | Khai báo AppConfig (`name = "apps.<tên_app>"`). |
| `models.py` | Định nghĩa bảng dữ liệu. |
| `admin.py` | Đăng ký model với Django Admin. |
| `serializers.py` | Validate input và định dạng output của API. **Không** chứa nghiệp vụ. |
| `views.py` | Nhận request, kiểm tra quyền, gọi service rồi trả response. Giữ mỏng. |
| `urls.py` | Route của app. |
| `services.py` | **Business logic** và các thao tác ghi dữ liệu (create/update/workflow). |
| `selectors.py` | Các truy vấn **đọc** phức tạp (filter, annotate, tối ưu query). |
| `migrations/` | Migration của database. |
| `tests/` | Test của app. |

Luồng xử lý chuẩn: `urls → views → serializers (validate) → services / selectors → models`.

### `accounts/` — Authentication

Quản lý User (custom user model, có `role`: candidate / employer / admin), đăng ký, đăng nhập/refresh/logout bằng JWT, đổi/quên mật khẩu, endpoint `me`.

- `managers.py`: custom UserManager (tạo user/superuser bằng email).
- `services.py`: đăng ký (tạo User và profile tương ứng theo role), reset mật khẩu.

### `candidates/` — Ứng viên

Hồ sơ ứng viên: thông tin cá nhân, học vấn, kinh nghiệm, kỹ năng, mong muốn công việc. Ứng viên chỉ quản lý dữ liệu của chính mình.

### `employers/` — Nhà tuyển dụng

Công ty (Company) và hồ sơ nhà tuyển dụng (Recruiter thuộc Company), xác thực công ty, quản lý thành viên công ty.

### `cvs/` — CV

Upload và quản lý file CV, trích xuất text, lưu dữ liệu đã bóc tách. **Không** gọi LLM trực tiếp.

- `validators.py`: kiểm tra định dạng (PDF/DOCX, theo nội dung file) và dung lượng file.
- `parsers/pdf_parser.py`, `parsers/docx_parser.py`: chuyển file thành raw text (không dùng AI); `parsers/__init__.py` chuẩn hóa văn bản, trích email/SĐT/link.
- `tasks.py`: sau khi upload, chạy task bóc tách (hiện chạy sau commit trong cùng tiến trình; giai đoạn AI đổi sang Celery) rồi phát `signals.cv_parsed` cho `ai` phân tích.
- `signals.py`: domain event `cv_uploaded`, `cv_parsed`, `cv_deleted`.
- `management/commands/parse_cvs.py`: bóc tách lại CV đang chờ / bị lỗi.

### `jobs/` — Tin tuyển dụng

Tin tuyển dụng (JD), ngành nghề, kỹ năng yêu cầu, địa điểm, mức lương, trạng thái (draft/published/closed).

- `filters.py`: bộ lọc tìm kiếm job (django-filter).
- Danh bạ công ty công khai (`companies/`) cũng đặt ở đây vì cần đếm tin đang tuyển (jobs phụ thuộc employers, không ngược lại).

### `favorites/` — Yêu thích

Ứng viên đánh dấu yêu thích việc làm và công ty (`candidate/favorites/...`). App đứng trên `candidates`, `jobs`, `employers`; các app đó không import ngược lại.

### `talents/` — Tìm ứng viên

Nhà tuyển dụng chủ động tìm ứng viên. Không có model: điểm tính khi gọi API.

- Tìm ứng viên (`employer/talents/`): mọi ứng viên công khai CV (`candidates.selectors.public_candidates`), kèm CV chính; tìm theo từ khóa (cả nội dung CV), địa điểm, cấp bậc.
- Ứng viên phù hợp với một tin (`employer/jobs/{id}/suggested-candidates/`), xếp theo điểm 0-100. Nguồn ứng viên: `candidates.selectors.discoverable_candidates(company)` — công khai CV hoặc đã ứng tuyển vào công ty; so khớp bằng CV mặc định.
- `matching.py`: chấm điểm bằng quy tắc (kỹ năng + tên gọi khác, bỏ dấu tiếng Việt; kinh nghiệm; cấp bậc; địa điểm), kèm lý do. Module AI sau này có thể thay bằng embedding + LLM, giữ nguyên API.

### `invitations/` — Thư mời ứng tuyển

Nhà tuyển dụng gửi thư mời ứng viên nộp hồ sơ vào một tin đang tuyển của công ty (mỗi tin một thư cho mỗi ứng viên, thu hồi được khi chưa phản hồi). Ứng viên xem thư, từ chối, hoặc nộp hồ sơ theo luồng ứng tuyển thường.

- `receivers.py`: nghe `applications.signals.application_submitted` — ứng viên nộp hồ sơ vào tin được mời thì thư chuyển "đã ứng tuyển".
- Migration `0002_drop_connections_messaging`: xóa bảng của chức năng kết bạn / nhắn tin đã gỡ bỏ.

### `applications/` — Ứng tuyển / ATS

Ứng viên nộp CV vào job, nhà tuyển dụng quản lý pipeline (applied → screening → interview → offer → hired/rejected), lưu lịch sử thay đổi trạng thái.

- `services.py`: kiểm soát chuyển trạng thái hợp lệ (state machine), chống nộp trùng.
- `filters.py`: lọc ứng viên theo trạng thái, điểm match, ...

### `ai/` — AI / LLM

Chứa toàn bộ logic AI. Các app khác chỉ gọi vào `ai/services/` (hoặc `ai/tasks.py`), không gọi LLM trực tiếp.

> Đã triển khai phần ứng viên theo prototype `TestAI` (xem [ai-api.md](ai-api.md)): provider Gemini, prompt, `services/cv_analysis.py`, `services/cv_suggestion.py`, `services/job_recommendation.py`, `nlp/`, `vectorstore/` (vector lưu trong PostgreSQL, cosine bằng Python — chưa dùng ChromaDB), `receivers.py` (xóa dữ liệu AI khi CV bị xóa). Còn rỗng: `services/candidate_matching.py`, `prompts/candidate_matching.py`, `llm/providers/openai_provider.py`, `tasks.py` (gọi AI đang chạy đồng bộ trong request).

| Thành phần | Trách nhiệm |
|---|---|
| `models.py` | Lưu kết quả AI (CV analysis, suggestion, match score) và log request LLM (token, chi phí, latency) để cache và audit. |
| `views.py` / `urls.py` | API kích hoạt hoặc lấy kết quả AI (phân tích CV, gợi ý job, xếp hạng ứng viên). |
| `tasks.py` | Celery task bọc các lời gọi LLM (chậm, có thể lỗi) để chạy nền, có retry. |
| `llm/base.py` | Interface chung cho LLM client (`generate`, `generate_structured`, `embed`). |
| `llm/providers/` | Cài đặt cụ thể cho OpenAI và Gemini. Đổi provider bằng config, không phải sửa code nghiệp vụ. |
| `llm/factory.py` | Chọn provider theo settings. |
| `llm/schemas.py` | Schema (Pydantic) cho output JSON của LLM để validate kết quả trả về. |
| `llm/exceptions.py` | Lỗi chuẩn hóa: timeout, rate limit, output không hợp lệ. |
| `prompts/` | Prompt template cho từng chức năng, tách khỏi code để dễ chỉnh và đánh version. |
| `vectorstore/client.py` | Kết nối ChromaDB. |
| `vectorstore/embeddings.py` | Sinh embedding cho CV và JD. |
| `vectorstore/indexer.py` | Đồng bộ CV/Job vào vector store khi tạo, sửa hoặc xóa. |
| `nlp/preprocessing.py` | Làm sạch, chuẩn hóa text CV/JD trước khi đưa vào LLM. |
| `nlp/skill_extractor.py` | Trích kỹ năng bằng spaCy / rule (rẻ, nhanh) để bổ trợ LLM. |
| `services/cv_analysis.py` | **CV analysis**: bóc tách cấu trúc, chấm điểm CV. |
| `services/cv_suggestion.py` | **CV suggestion**: gợi ý chỉnh sửa CV (tổng quát hoặc theo một JD cụ thể). |
| `services/job_recommendation.py` | **Job recommendation**: lọc nhanh ứng viên-job bằng vector similarity, sau đó LLM rerank và giải thích. |
| `services/candidate_matching.py` | **Candidate matching**: chấm điểm và xếp hạng ứng viên cho một JD. |

## Quy tắc phụ thuộc giữa các module

- `common` không import từ `apps`.
- `accounts` là nền tảng: mọi app được phép phụ thuộc vào nó.
- `candidates`, `employers` → `accounts`.
- `cvs` → `candidates`. `jobs` → `employers`. `applications` → `cvs`, `jobs`.
- `invitations` → `candidates`, `jobs`, `applications`. `talents` → `candidates`, `cvs`, `jobs`, `applications`, `invitations`.
- `ai` được đọc dữ liệu từ `cvs`, `jobs`, `candidates`. Các app nghiệp vụ chỉ gọi `ai` qua `ai/services` hoặc `ai/tasks`.
- Không import `views` của app khác. Giao tiếp giữa các app qua `services` / `selectors`.

## Gốc repo

| Thành phần | Trách nhiệm |
|---|---|
| `database/schema.sql` | Tài liệu thiết kế schema (nguồn chính vẫn là Django migrations). |
| `docs/` | Tài liệu kiến trúc, API, quy ước. |
| `docker-compose.yml` | Chạy local đầy đủ: backend, Celery worker, PostgreSQL, Redis, ChromaDB. |
