# API Ứng viên — Giai đoạn 2 (hồ sơ, tải lên CV, ứng tuyển)

Tài liệu cho phần backend dành cho **Ứng viên**, dựng theo đúng khuôn của giai đoạn 1 (Nhà tuyển dụng):
`urls → views (mỏng) → serializers (validate) → services (ghi) / selectors (đọc) → models`,
permission theo vai trò + mixin giới hạn dữ liệu, domain event phát sau commit, test pytest cho từng app.

Swagger: `http://localhost:8000/api/docs/` — nhóm **Candidate - Tài khoản**, **Candidate - CV**, **Candidate - Ứng tuyển**,
**Candidate - Yêu thích**, **Companies (công khai)**.

---

## 1. Phạm vi và giả định

| Use case | Trạng thái |
|---|---|
| UC-01 Đăng ký / đăng nhập (ứng viên) | Đăng ký bằng email + mật khẩu, đăng nhập dùng chung `/auth/login/`. Xác thực email, OAuth, quên mật khẩu: chưa làm (giống phía NTD). |
| UC-02 Quản lý hồ sơ cá nhân | Thông tin cơ bản + mong muốn công việc. Học vấn / kinh nghiệm / kỹ năng tự khai / ảnh đại diện: giai đoạn sau. |
| **UC-03 Tải lên CV** | **Đầy đủ**: upload PDF/DOCX ≤ 5 MB, kiểm tra nội dung file, lưu riêng tư, bóc tách văn bản + liên hệ (không dùng AI), quản lý nhiều CV, CV mặc định, xem/tải file. Phân tích, chấm điểm bằng AI: module `ai` (giai đoạn sau) nghe event `cv_parsed`. |
| UC-08 Ứng tuyển | Nộp bằng CV đã tải lên (hoặc CV mặc định) + thư giới thiệu. Dùng lại đúng service `submit_application` của giai đoạn 1. |
| UC-09 Theo dõi đơn ứng tuyển | Danh sách, chi tiết, lịch sử trạng thái, rút hồ sơ. |
| UC-07 Lưu tin (mở rộng: yêu thích việc làm **và công ty**) | App `favorites`: thêm / bỏ / xem danh sách yêu thích. |
| Xem, tìm kiếm công ty | Danh bạ công ty công khai: tìm theo tên, lọc ngành nghề / tỉnh, hồ sơ công ty + tin đang tuyển. |
| UC-04, 05 (gợi ý sửa CV, việc làm đề xuất) | Giai đoạn sau (module AI). |

Giả định:
- Chưa có Celery: bóc tách CV chạy **ngay sau khi transaction commit, cùng tiến trình** (xem `cvs/tasks.py`).
  Frontend vẫn phải coi là bất đồng bộ (poll khi `parse_status` là `pending`/`processing`) — khi chuyển sang
  Celery chỉ sửa `cvs/tasks.py`, API không đổi.
- CV là dữ liệu cá nhân: lưu ở `PRIVATE_MEDIA_ROOT`, **không có URL công khai**, chỉ tải qua API có kiểm tra quyền.
- Ứng viên **không** thấy ghi chú nội bộ, đánh giá sao, lý do từ chối của nhà tuyển dụng.

## 2. Cấu trúc code

```text
apps/candidates/
  permissions.py   IsCandidate (gắn request.candidate), CandidateAccessMixin — giống IsEmployer/EmployerAccessMixin
  selectors.py     get_candidate_profile(user)
  serializers.py   CandidateRegisterSerializer, CandidateProfileSerializer, build_candidate_profile (cho /auth/me/)
  services.py      register_candidate, update_candidate_profile
  views.py/urls.py candidate/register/, candidate/profile/
  apps.py          ready(): đăng ký phần `profile` của /auth/me/ cho role=candidate (accounts.registry)

apps/cvs/
  models.py        CV + cột kết quả bóc tách (parse_status, parse_error, raw_text, parsed_data, parsed_at)
  migrations/0002_cv_parse_fields.py
  validators.py    validate_cv_file: đuôi .pdf/.docx, ≤ CV_MAX_SIZE, nhận dạng theo NỘI DUNG (chữ ký %PDF / cấu trúc DOCX)
  parsers/         __init__ (điều phối, chuẩn hóa văn bản, trích email/SĐT/link, đoán ngôn ngữ)
                   pdf_parser.py (pypdf), docx_parser.py (zipfile + ElementTree, đọc cả header/footer, bảng)
  tasks.py         enqueue_parse / parse_cv_task — điểm thay bằng Celery
  signals.py       cv_uploaded, cv_parsed, cv_deleted
  services.py      upload_cv, update_cv, set_default_cv, delete_cv, reparse_cv, parse_cv
  selectors.py     candidate_cvs, get_candidate_cv, get_default_cv
  serializers.py / views.py / urls.py   candidate/cvs/...
  admin.py         xem cả CV đã xóa mềm, action "Bóc tách lại"
  management/commands/parse_cvs.py      bóc tách CV cũ / lỗi

apps/applications/   (chỉ BỔ SUNG, không đổi hành vi phía NTD)
  workflow.py      CANDIDATE_WITHDRAWABLE_STATUSES, can_withdraw()
  services.py      withdraw_application()
  selectors.py     candidate_applications(), candidate_application_detail_queryset()
  filters.py       CandidateApplicationFilter
  serializers.py   Candidate* serializers
  views.py/urls.py CandidateApplicationViewSet: candidate/applications/...
```

Quy tắc phụ thuộc giữ nguyên: `candidates → accounts`, `cvs → candidates`, `applications → cvs, jobs`.
`candidates` đếm CV và `cvs` đếm hồ sơ ứng tuyển qua quan hệ ngược của ORM, không import code của app kia.

## 3. Danh sách API

Tất cả nằm dưới `/api/v1/`, cần `Authorization: Bearer <access>` (trừ đăng ký). Lỗi có dạng chung
`{"detail", "code", "errors"?}` như giai đoạn 1.

| Method | Đường dẫn | Mô tả |
|---|---|---|
| POST | `candidate/register/` | Đăng ký ứng viên → 201 `{access, refresh, user}` |
| GET / PATCH | `candidate/profile/` | Xem / sửa hồ sơ (họ tên, SĐT, headline, ngày sinh, mong muốn công việc...) |
| GET | `candidate/cvs/` | Danh sách CV của tôi (CV mặc định đứng đầu, không phân trang) |
| POST | `candidate/cvs/` | **Tải lên CV** (multipart: `file`, `title?`, `is_default?`) → 201 |
| GET | `candidate/cvs/{id}/` | Chi tiết CV + `raw_text`, `parsed_data` |
| PATCH | `candidate/cvs/{id}/` | Đổi tên CV (`title`) |
| DELETE | `candidate/cvs/{id}/` | Xóa CV → 204 |
| POST | `candidate/cvs/{id}/set-default/` | Đặt làm CV mặc định |
| POST | `candidate/cvs/{id}/reparse/` | Bóc tách lại CV bị lỗi |
| GET | `candidate/cvs/{id}/file/` | Xem file (`?download=1` để tải về) |
| GET | `candidate/applications/` | Hồ sơ tôi đã nộp (`?status=applied,screening`, `?q=`, `?ordering=`, phân trang) |
| POST | `candidate/applications/` | Ứng tuyển `{job_id, cv_id?, cover_letter?}` → 201 |
| GET | `candidate/applications/{id}/` | Chi tiết: tin, CV đã nộp, thư giới thiệu, lịch sử trạng thái |
| POST | `candidate/applications/{id}/withdraw/` | Rút hồ sơ `{reason?}` |
| GET | `candidate/favorites/ids/` | `{jobs: [id], companies: [id]}` đang yêu thích (để đánh dấu nút ♥) |
| GET / POST | `candidate/favorites/jobs/` | Việc làm yêu thích (phân trang) / thêm `{job_id}` → 201 (đã có → 200) |
| DELETE | `candidate/favorites/jobs/{job_id}/` | Bỏ yêu thích theo id tin → 204 |
| GET / POST | `candidate/favorites/companies/` | Công ty yêu thích / thêm `{company_id}` → 201 (đã có → 200) |
| DELETE | `candidate/favorites/companies/{company_id}/` | Bỏ yêu thích theo id công ty → 204 |

API công khai (không cần đăng nhập) phục vụ phần xem công ty:

| Method | Đường dẫn | Mô tả |
|---|---|---|
| GET | `companies/` | Danh bạ công ty (`?q=` tên, `?industry=`, `?location=`, phân trang), kèm `open_job_count`; công ty nhiều tin đang tuyển đứng trước |
| GET | `companies/{id}/` | Hồ sơ công ty (không gồm mã số thuế, email / SĐT liên hệ) |
| GET | `jobs/?company={id}` | Tin đang tuyển của một công ty |
| GET | `jobs/?posted_within=1\|3\|7\|14\|30` | Tin đăng trong N ngày gần đây (kết hợp được với `industry`, `level`, `location`, `job_type`, `q`) |

`GET /auth/me/` của ứng viên có `profile = {candidate_id, headline, is_open_to_work, cv_count}`
(`cv_count = 0` → frontend đưa ứng viên tới trang tải CV).

## 4. Tải lên CV

```bash
curl -X POST http://localhost:8000/api/v1/candidate/cvs/ \
  -H "Authorization: Bearer $ACCESS" \
  -F "file=@NgoBaDat_CV.docx" -F "title=CV Backend (DOCX)"
```

Kiểm tra file (lỗi 400, nằm ở `errors.file`):
- Chỉ `.pdf`, `.docx`; file rỗng hoặc > 5 MB (`CV_MAX_SIZE`) bị từ chối.
- Định dạng xác định theo nội dung, không tin đuôi file / Content-Type: file đổi đuôi, `.doc` cũ, ảnh,
  zip khác (xlsx...), DOCX chứa macro (`.docm` đổi đuôi) đều bị từ chối.

Response (201, rút gọn — dữ liệu thật khi chạy thử):

```json
{
  "id": "e62864e8-...", "title": "CV Backend (DOCX)", "original_filename": "NgoBaDat_CV.docx",
  "mime_type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
  "file_size": 37549, "language": "vi", "is_default": false,
  "parse_status": "completed", "parse_error": "", "parsed_at": "2026-10-09T00:30:32+07:00",
  "application_count": 0,
  "file_url": "http://localhost:8000/api/v1/candidate/cvs/e62864e8-.../file/",
  "raw_text": "Ngô Bá Đạt — dat.ngo@example.com — 0987 654 321\n\nMỤC TIÊU NGHỀ NGHIỆP\n...",
  "parsed_data": {
    "version": 1, "source": "parser",
    "stats": {"pages": null, "words": 37, "characters": 231},
    "contact": {"emails": ["dat.ngo@example.com"], "phones": ["0987654321"], "links": ["https://github.com/ngobadat"]}
  }
}
```

Trạng thái bóc tách: `pending → processing → completed | failed`. Khi `failed`, `parse_error` là thông điệp
tiếng Việt cho ứng viên, ví dụ:
- CV dạng ảnh / PDF scan (không có lớp chữ) — gợi ý xuất lại từ Word/Google Docs (OCR: giai đoạn sau);
- PDF đặt mật khẩu mở file (PDF chỉ hạn chế in/sửa vẫn đọc được);
- file hỏng.

File vẫn được lưu khi bóc tách thất bại; ứng viên có thể `reparse` hoặc tải file khác.

## 5. Quy tắc nghiệp vụ

CV
- CV đầu tiên tự động là **mặc định**; mỗi ứng viên tối đa 1 CV mặc định (ràng buộc `uq_cvs_default`).
  Đổi mặc định bằng `set-default` hoặc `is_default=true` khi upload. Xóa CV mặc định → CV mới nhất còn lại thành mặc định.
- Tối đa `CANDIDATE_MAX_CVS` (mặc định 10) CV chưa xóa → `cv_limit_reached`.
- Cùng một file (SHA-256) không upload hai lần trong phạm vi một ứng viên → 409 `duplicate_cv`.
- `title` bỏ trống → lấy theo tên file. Tên lưu trữ trên đĩa là UUID, không dùng tên file gốc.
- Xóa CV là **xóa mềm**. CV đã dùng để ứng tuyển **giữ file** (NTD vẫn xem được đúng bản đã nhận);
  CV chưa dùng thì **xóa file vật lý** sau khi commit.
- Các thao tác CV của cùng một ứng viên được khóa tuần tự (`select_for_update` trên hồ sơ ứng viên).
- Upload bị giới hạn 30 lần/giờ/người (`cv_upload` throttle) vì mỗi lần tốn CPU bóc tách.

Ứng tuyển
- `cv_id` bỏ trống → dùng CV mặc định; chưa có CV → 400 (`errors.cv_id`). CV của người khác / đã xóa → "CV không tồn tại".
- Tin nháp hoặc của công ty đã xóa → "Tin tuyển dụng không tồn tại"; tin đã đóng / hết hạn / tạm dừng → `job_not_accepting`.
- Không nộp trùng (kể cả sau khi đã rút) → 409 `duplicate_application`.
- CV chưa bóc tách xong vẫn được nộp (UC-08).
- Rút hồ sơ khi đang `applied / screening / interview / offer`; `hired / rejected / withdrawn` → 409
  `invalid_status_transition`. Lý do rút ghi vào lịch sử, NTD thấy được; phát `application_status_changed`.

Yêu thích
- Chỉ yêu thích được tin đang hiển thị công khai (không phải bản nháp, chưa xóa, công ty chưa xóa); tin đã đóng /
  hết hạn vẫn thêm được và vẫn nằm trong danh sách (kèm `status` để frontend hiển thị).
- Tin / công ty bị xóa sau đó tự ẩn khỏi danh sách và khỏi `ids`.
- Thêm lặp lại trả 200, bỏ khi chưa yêu thích trả 204: bấm nhiều lần hoặc mở nhiều tab không gây lỗi.
- Danh sách yêu thích là riêng tư của từng ứng viên; nhà tuyển dụng không xem được.

## 6. Mã lỗi mới

| code | HTTP | Ý nghĩa |
|---|---|---|
| `validation_error` | 400 | Sai dữ liệu / file không hợp lệ (xem `errors`) |
| `cv_limit_reached` | 400 | Đã đủ số CV tối đa |
| `duplicate_cv` | 409 | File đã được tải lên trước đó |
| `invalid_parse_status` | 409 | Chỉ `reparse` CV đang `pending`/`failed` |
| `job_not_accepting` | 400 | Tin không còn nhận hồ sơ |
| `duplicate_application` | 409 | Đã ứng tuyển tin này |
| `invalid_status_transition` | 409 | Không thể rút hồ sơ ở trạng thái hiện tại |
| `throttled` | 429 | Upload quá nhiều trong 1 giờ |

## 7. Điểm mở rộng cho AI (giai đoạn sau)

- `apps.cvs.signals.cv_parsed(cv)` — phát sau commit khi đã có `raw_text`/`parsed_data`: chạy CV analysis,
  CV suggestion, sinh embedding, index ChromaDB, tính lại gợi ý việc làm.
- `cv_deleted(cv)` — gỡ CV khỏi vector store. `cv_uploaded(cv)` — thông báo, thống kê.
- `application_submitted` / `application_status_changed` (giai đoạn 1) — giờ được phát cả từ API ứng viên.
- `parsed_data` có `version` và `source`; module AI ghi thêm cấu trúc (học vấn, kinh nghiệm, kỹ năng...) vào cùng JSON.
- `file_hash` dùng làm khóa cache kết quả AI (cùng file → không gọi LLM lại).
- Chuyển sang Celery: chỉ sửa `cvs/tasks.py` (`@shared_task` + `.delay()`), retry 3 lần theo UC-03.

## 8. Chạy và kiểm thử

```bash
pip install -r requirements.txt        # thêm pypdf
python manage.py migrate               # cvs.0002_cv_parse_fields
python manage.py seed_demo --reset     # ứng viên demo giờ đăng nhập được: candidate@demo.com / 123456
python manage.py parse_cvs             # bóc tách CV có từ trước (đang pending/failed); --all để làm lại tất cả
pytest                                 # 180 test (100 của giai đoạn 1 + 80 mới)
```

Test mới: `apps/candidates/tests/test_candidate_account.py`, `apps/cvs/tests/test_candidate_cvs.py`,
`apps/applications/tests/test_candidate_applications.py` (gồm 1 test luồng đầy đủ đăng ký → tải CV → ứng tuyển).

Cấu hình mới (`config/settings/base.py`, `.env.example`): `CV_MAX_SIZE` (5 MB), `CANDIDATE_MAX_CVS` (10),
throttle `cv_upload` (30/giờ). Ở production nên đặt giới hạn body ở reverse proxy (vd. nginx
`client_max_body_size 6m`) để file quá lớn bị chặn trước khi tới Django.
