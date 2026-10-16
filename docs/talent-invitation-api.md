# API Tìm ứng viên và Thư mời ứng tuyển

Mở rộng cho nhà tuyển dụng (NTD) và ứng viên, cùng khuôn với giai đoạn 1-2:
`urls → views (mỏng) → serializers (validate) → services (ghi) / selectors (đọc) → models`.

Luồng nghiệp vụ:

1. Ứng viên bật **Công khai CV** (trang CV của tôi) → mọi NTD tìm thấy hồ sơ và xem được **CV chính** (CV mặc định).
   Muốn công khai CV khác thì đặt CV đó làm CV chính.
2. NTD mở **Tìm ứng viên** (mọi CV công khai) hoặc **Ứng viên phù hợp** với một tin (chấm điểm) → xem CV →
   **Gửi thư mời** ứng tuyển vào một tin đang tuyển của công ty.
3. Ứng viên nhận thư ở trang **Thư mời** (menu có huy hiệu số thư chưa xem) → **Ứng tuyển ngay** (luồng nộp hồ sơ
   thường) hoặc **Từ chối**.
4. Nộp hồ sơ vào tin được mời thì thư tự chuyển **Đã ứng tuyển**. NTD theo dõi ở **Thư mời đã gửi**:
   Chưa xem / Đã xem / Đã ứng tuyển / Đã từ chối.

Thư mời thay cho chức năng kết bạn và nhắn tin trước đây: app `connections`, `messaging` đã được gỡ, migration
`invitations.0002_drop_connections_messaging` xóa các bảng `connections`, `conversations`, `messages`.

Swagger: `http://localhost:8000/api/docs/` — nhóm **Employer - Tìm ứng viên**, **Employer - Thư mời ứng tuyển**,
**Candidate - Thư mời ứng tuyển**.

---

## 1. Quyền riêng tư

- **Tìm ứng viên**: chỉ ứng viên bật công khai CV (`candidate_profiles.is_public`,
  `candidates.selectors.public_candidates`).
- **Ứng viên phù hợp**, **xem CV**, **gửi thư mời**: ứng viên công khai CV hoặc đã ứng tuyển vào một tin của công ty
  (`candidates.selectors.discoverable_candidates`).
- Ứng viên khác trả về 404 (không lộ sự tồn tại). Danh sách không gồm email / số điện thoại; NTD chỉ xem **CV chính**
  của ứng viên. Tài khoản bị khóa không xuất hiện.

Ứng viên bật / tắt công khai CV: `PATCH candidate/profile/` với `{"is_public": true | false}`.

## 2. Chấm điểm phù hợp (`apps/talents/matching.py`)

Chỉ dùng cho **Ứng viên phù hợp** với một tin. Bằng quy tắc, không dùng LLM; điểm 0-100 = tổng 4 tiêu chí:

| Tiêu chí | Tối đa | Cách tính |
|---|---|---|
| Kỹ năng | 60 | Tỉ lệ trọng số kỹ năng của tin có trong CV + hồ sơ. Trọng số = `weight` (1-5) × 2 nếu bắt buộc. |
| Kinh nghiệm | 20 | `years_of_experience / min_years_experience` (tối đa 1); tin không yêu cầu → đủ điểm. |
| Cấp bậc | 10 | Đúng cấp bậc → 10; lệch 1 bậc → 6; lệch nhiều hơn → 0. |
| Địa điểm | 10 | Cùng tỉnh/thành hoặc tin làm từ xa → 10; khác tỉnh → 0. |

Hồ sơ chưa khai thông tin của tiêu chí → được nửa số điểm. Chỉ hiện ứng viên khớp **ít nhất một kỹ năng**.

So khớp kỹ năng: dùng tên chuẩn và **tên gọi khác** trong danh mục (`ReactJS` → `React`), bỏ dấu + chữ thường
(CV PDF font chuẩn mất dấu: `Ban hang` vẫn khớp `Bán hàng`), khớp trọn từ (`JavaScript` không tính là `Java`).
Kèm `reasons`: số kỹ năng đáp ứng, kỹ năng bắt buộc còn thiếu, kinh nghiệm, cấp bậc, địa điểm.

Điểm tính khi gọi API (không lưu DB). Khi có module AI có thể thay bằng embedding + LLM rerank mà không đổi API.

## 3. Danh sách API

Tất cả dưới `/api/v1/`, cần `Authorization: Bearer <access>`. Lỗi có dạng chung `{"detail", "code", "errors"?}`.

### Tìm ứng viên (chỉ NTD)

| Method | Đường dẫn | Mô tả |
|---|---|---|
| GET | `employer/talents/` | Ứng viên công khai CV, CV cập nhật gần nhất trước. `?q=` (tên, tiêu đề hồ sơ, vị trí mong muốn, giới thiệu, nội dung CV), `?location_id=`, `?level=`, phân trang |
| GET | `employer/jobs/{job_id}/suggested-candidates/` | Ứng viên phù hợp với tin, điểm cao trước. `?q=` (tên, tiêu đề hồ sơ), `?min_score=0-100`, `?hide_applied=true`, phân trang |
| GET | `employer/talents/{candidate_id}/cv/` | Xem CV chính của ứng viên (`?download=1` để tải về) |

Một phần tử của `employer/talents/`:

```json
{
  "candidate": {"id": "…", "full_name": "Lê Thị Cúc", "headline": "Kế toán tổng hợp", "summary": "…",
                "years_of_experience": 3.0, "current_level": "staff",
                "location": {"id": 1, "name": "Hà Nội", "slug": "ha-noi"}, "desired_position": "…", "is_open_to_work": true},
  "cv": {"id": "…", "title": "CV Kế toán tổng hợp", "original_filename": "…pdf", "mime_type": "application/pdf",
         "file_size": 1586, "parse_status": "completed", "updated_at": "…"},
  "invitation": {"id": "…", "job": {"id": "…", "title": "Kế toán tổng hợp", "status": "published"},
                 "status": "accepted", "read_at": "…", "created_at": "…"}
}
```

`invitation`: thư mời gần nhất công ty đã gửi cho ứng viên (null: chưa mời). Ở `suggested-candidates`, mỗi phần tử có
thêm `score`, `breakdown`, `matched_skills`, `missing_skills`, `reasons`, `application_id` (hồ sơ đã nộp vào chính tin
này) và `invitation` là thư của **chính tin đang xem**.

### Thư mời — nhà tuyển dụng

| Method | Đường dẫn | Mô tả |
|---|---|---|
| POST | `employer/invitations/` | Gửi thư `{candidate_id, job_id, message}` → 201 |
| GET | `employer/invitations/` | Thư công ty đã gửi, mới gửi trước. `?status=pending\|accepted\|declined`, `?job_id=`, `?q=` (tên ứng viên), phân trang |
| DELETE | `employer/invitations/{id}/` | Thu hồi thư đang chờ phản hồi → 204 |

Một phần tử:

```json
{"id": "…", "job": {"id": "…", "title": "Nhân viên lễ tân", "status": "published"},
 "candidate": {"id": "…", "full_name": "Nguyễn Văn An", "headline": "Nhân viên kinh doanh", "current_level": "staff",
               "years_of_experience": 1.5, "location": {"id": 1, "name": "Hà Nội", "slug": "ha-noi"}},
 "sender": {"full_name": "Võ Thị Mai", "position": "Trưởng bộ phận Nhân sự"},
 "message": "Chào An, …", "status": "pending", "read_at": null, "responded_at": null, "application_id": null,
 "created_at": "…"}
```

`status = pending` + `read_at = null`: ứng viên chưa xem; `read_at` có giá trị: đã xem, chưa phản hồi.
`status = accepted`: ứng viên đã nộp hồ sơ, `application_id` là hồ sơ đó.

### Thư mời — ứng viên

| Method | Đường dẫn | Mô tả |
|---|---|---|
| GET | `candidate/invitations/` | Thư tôi nhận được, mới nhất trước. `?status=`, phân trang |
| GET | `candidate/invitations/{id}/` | Chi tiết thư |
| POST | `candidate/invitations/{id}/read/` | Đánh dấu đã xem (chỉ ghi nhận lần đầu) |
| POST | `candidate/invitations/{id}/decline/` | Từ chối thư đang chờ phản hồi |
| GET | `candidate/invitations/summary/` | `{"unread": 1}` — số thư đang chờ mà ứng viên chưa mở (huy hiệu trên menu) |

Phần tử giống phía NTD nhưng không có `candidate`, còn `job` cùng cấu trúc với danh sách việc làm công khai (công ty,
địa điểm, lương, trạng thái...). **Nhận lời mời = nộp hồ sơ** bằng API ứng tuyển sẵn có
`POST candidate/applications/ {job_id, cv_id?}`.

## 4. Quy tắc nghiệp vụ

- Chỉ NTD đang hoạt động gửi thư; `job_id` phải là tin của công ty **đang nhận hồ sơ** (đang tuyển, chưa hết hạn).
- Ứng viên phải được công ty phép thấy (mục 1) và **chưa ứng tuyển** vào tin đó.
- Mỗi ứng viên nhận tối đa **một thư cho mỗi tin** (ràng buộc `uq_invitations_job_candidate`); mời vị trí khác thì
  gửi thư cho tin khác.
- Nội dung thư bắt buộc, tối đa 2000 ký tự.
- Mọi NTD của công ty thấy và thu hồi được thư của công ty; chỉ thu hồi được thư **đang chờ phản hồi** (xóa hẳn, nên
  có thể mời lại).
- Ứng viên chỉ từ chối được thư đang chờ phản hồi. Ứng viên nộp hồ sơ vào tin được mời (kể cả sau khi đã từ chối) thì
  thư chuyển `accepted` và lưu `application_id` (`invitations/receivers.py` nghe `application_submitted`).
- Thư của tin đã xóa (hoặc công ty đã xóa) được ẩn với cả hai bên.
- Giới hạn tốc độ: gửi thư 60/giờ (`invitation`). Chưa gửi email: frontend hỏi `summary` mỗi 60 giây (bỏ qua khi tab ẩn).

## 5. Mã lỗi mới

| code | HTTP | Ý nghĩa |
|---|---|---|
| `candidate_not_found` | 404 | Ứng viên không tồn tại hoặc NTD không được phép thấy |
| `job_not_found` | 404 | Tin không thuộc công ty |
| `job_not_accepting` | 400 | Tin không còn nhận hồ sơ (nháp, tạm dừng, đã đóng, hết hạn) |
| `already_applied` | 409 | Ứng viên đã ứng tuyển vào tin này |
| `already_invited` | 409 | Công ty đã gửi thư mời ứng viên cho tin này |
| `invalid_invitation_action` | 409 | Thu hồi / từ chối thư không còn ở trạng thái chờ phản hồi |

## 6. Chạy và kiểm thử

```bash
python manage.py migrate               # invitations.0001 tạo bảng invitations,
                                       # invitations.0002 xóa bảng kết bạn / tin nhắn cũ (không hoàn tác được)
python manage.py seed_demo --reset     # ứng viên demo bật công khai CV (trừ linh.do@demo.com);
                                       # recruiter@demo.com đã gửi 4 thư (3 đã ứng tuyển, 1 bị từ chối),
                                       # candidate@demo.com có 1 thư mới chưa xem của Khách sạn Biển Xanh
pytest                                 # 209 test (apps/invitations, apps/talents)
```

Bảng mới: `invitations`. Bảng bỏ: `connections`, `conversations`, `messages` (đã cập nhật `database/schema.sql`).
