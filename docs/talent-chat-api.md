# API Ứng viên phù hợp, Kết bạn và Tin nhắn

Mở rộng cho nhà tuyển dụng (NTD) và ứng viên, cùng khuôn với giai đoạn 1-2:
`urls → views (mỏng) → serializers (validate) → services (ghi) / selectors (đọc) → models`.

Luồng nghiệp vụ:

1. NTD mở **Ứng viên phù hợp** của một tin → hệ thống so khớp CV mặc định của các ứng viên với tin, xếp theo điểm.
2. NTD xem CV, bấm **Kết bạn** (kèm lời nhắn) → ứng viên nhận lời mời ở trang **Kết nối**.
3. Ứng viên **chấp nhận** → hai bên là bạn bè; hội thoại được tạo, lời nhắn kèm lời mời là tin nhắn đầu tiên.
4. Hai bên **nhắn tin** trực tiếp ở trang **Tin nhắn**.

Swagger: `http://localhost:8000/api/docs/` — nhóm **Employer - Ứng viên phù hợp**, **Kết bạn**, **Tin nhắn**.

---

## 1. Quyền riêng tư

NTD chỉ thấy (gợi ý, xem CV, mời kết bạn) ứng viên **được phép tìm thấy** với công ty của họ
(`candidates.selectors.discoverable_candidates`):

- ứng viên bật **"Cho phép nhà tuyển dụng tìm thấy hồ sơ"** (`is_public`, trang Hồ sơ cá nhân), hoặc
- ứng viên đã ứng tuyển vào một tin của công ty.

Ứng viên khác trả về 404 (không lộ sự tồn tại). Danh sách gợi ý không gồm email / số điện thoại; NTD chỉ xem
**CV mặc định** của ứng viên. Tài khoản bị khóa không xuất hiện.

## 2. Chấm điểm phù hợp (`apps/talents/matching.py`)

Bằng quy tắc, không dùng LLM; điểm 0-100 = tổng 4 tiêu chí:

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

### Ứng viên phù hợp (chỉ NTD)

| Method | Đường dẫn | Mô tả |
|---|---|---|
| GET | `employer/jobs/{job_id}/suggested-candidates/` | Ứng viên phù hợp, điểm cao trước. `?q=` (tên, tiêu đề hồ sơ), `?min_score=0-100`, `?hide_applied=true`, phân trang |
| GET | `employer/talents/{candidate_id}/cv/` | Xem CV mặc định của ứng viên (`?download=1` để tải về) |

Một phần tử:

```json
{
  "candidate": {"id": "…", "user_id": "…", "full_name": "Nguyễn Văn An", "headline": "Nhân viên kinh doanh",
                "summary": "…", "years_of_experience": 1.5, "current_level": "staff",
                "location": {"id": 1, "name": "Hà Nội", "slug": "ha-noi"}, "desired_position": "…", "is_open_to_work": true},
  "cv": {"id": "…", "title": "CV Nhân viên kinh doanh", "original_filename": "…pdf", "mime_type": "application/pdf",
         "file_size": 1586, "parse_status": "completed", "updated_at": "…"},
  "score": 100,
  "breakdown": {"skills": 60, "experience": 20, "level": 10, "location": 10},
  "matched_skills": ["Bán hàng", "Đàm phán", "Chăm sóc khách hàng", "Tin học văn phòng"],
  "missing_skills": [],
  "reasons": ["Đáp ứng 4/4 kỹ năng yêu cầu", "1,5 năm kinh nghiệm (yêu cầu từ 1 năm)", "Đúng cấp bậc Nhân viên",
              "Cùng địa điểm Hà Nội"],
  "application_id": "…",
  "connection": {"id": "…", "status": "accepted", "direction": "sent"}
}
```

`application_id`: hồ sơ ứng viên đã nộp vào chính tin này (null nếu chưa). `connection`: null nếu chưa mời.

### Kết bạn (ứng viên và NTD)

| Method | Đường dẫn | Mô tả |
|---|---|---|
| GET | `connections/` | Bạn bè (kết bạn gần nhất trước), `?q=` tìm theo tên |
| GET | `connections/requests/?box=received` | Lời mời đang chờ mình phản hồi (mặc định) |
| GET | `connections/requests/?box=sent` | Lời mời mình đã gửi: đang chờ / bị từ chối |
| POST | `connections/` | **Chỉ NTD**: gửi lời mời `{user_id, job_id?, message?}` → 201 |
| POST | `connections/{id}/accept/` | Người nhận chấp nhận |
| POST | `connections/{id}/decline/` | Người nhận từ chối |
| DELETE | `connections/{id}/` | Hủy kết bạn (một trong hai bên) / người gửi hủy lời mời đang chờ → 204 |

Một phần tử (nhìn từ người đang đăng nhập):

```json
{"id": "…", "status": "pending", "direction": "received",
 "user": {"id": "…", "full_name": "Trần Thị Bình", "role": "employer", "headline": "Trưởng phòng Nhân sự",
          "candidate_id": null, "company": {"id": "…", "name": "Công ty CP Bán lẻ Sao Việt", "logo_url": null}},
 "message": "Chào Cúc, …", "job": {"id": "…", "title": "Kế toán tổng hợp"},
 "created_at": "…", "responded_at": null}
```

### Tin nhắn (ứng viên và NTD)

| Method | Đường dẫn | Mô tả |
|---|---|---|
| GET | `conversations/` | Hội thoại của tôi (tin gần nhất trước), kèm `unread_count`, `last_message`, `can_send` |
| POST | `conversations/` | Mở hội thoại với một bạn bè `{user_id}` → 201 (đã có → 200) |
| GET | `conversations/{id}/` | Chi tiết hội thoại |
| GET | `conversations/{id}/messages/` | 50 tin mới nhất; `?before=<id>` 50 tin cũ hơn; `?after=<id>` tin mới hơn (hỏi định kỳ) → `{results, has_more}` |
| POST | `conversations/{id}/messages/` | Gửi tin `{body}` (≤ 2000 ký tự) → 201 |
| POST | `conversations/{id}/read/` | Đánh dấu đã đọc mọi tin mình nhận → 204 |
| GET | `conversations/summary/` | `{unread_messages, unread_conversations, pending_requests}` cho huy hiệu trên menu |

Frontend hỏi định kỳ: khung chat 3 giây (`?after=`), danh sách hội thoại 10 giây, huy hiệu menu 20 giây (bỏ qua
khi tab ẩn). Có thể thay bằng WebSocket (Django Channels) sau — event `messaging.signals.message_sent` đã có sẵn.

## 4. Quy tắc nghiệp vụ

Kết bạn
- Chỉ NTD (recruiter đang hoạt động) gửi lời mời, và chỉ tới ứng viên được phép tìm thấy (mục 1); `job_id` phải
  là tin của công ty NTD.
- Mỗi cặp tài khoản một lời mời: đang chờ → 409 `request_pending`; đã là bạn → 409 `already_connected`.
- Bị từ chối: sau **7 ngày** mới mời lại được (409 `request_declined_recently`); gửi lại dùng lại bản ghi cũ.
- Chỉ người nhận chấp nhận / từ chối (người khác: 403 hoặc 404). Lời mời bị từ chối được giữ để tính thời gian chờ.

Tin nhắn
- Chỉ nhắn được với bạn bè (403 `not_connected`). Hủy kết bạn: vẫn xem tin nhắn cũ, `can_send=false`.
- Mỗi cặp tài khoản một hội thoại (`user_a < user_b`, ràng buộc `uq_conversations_pair`).
- Hội thoại / tin nhắn của người khác trả về 404. Admin không dùng được kết bạn và tin nhắn.
- Giới hạn tốc độ: gửi tin nhắn 30/phút (`chat_message`), gửi lời mời 60/giờ (`connection_request`).

## 5. Mã lỗi mới

| code | HTTP | Ý nghĩa |
|---|---|---|
| `candidate_not_found` | 404 | Ứng viên không tồn tại hoặc NTD không được phép thấy |
| `job_not_found` | 404 | Tin liên quan không thuộc công ty |
| `request_pending` | 409 | Đã có lời mời đang chờ |
| `already_connected` | 409 | Đã là bạn bè |
| `request_declined_recently` | 409 | Bị từ chối chưa đủ 7 ngày |
| `invalid_connection_action` | 403 / 409 | Không phải người nhận, hoặc lời mời không còn ở trạng thái phù hợp |
| `not_connected` | 403 | Nhắn tin khi chưa / không còn là bạn bè |
| `invalid_recipient` | 400 | Nhắn tin cho chính mình |

## 6. Chạy và kiểm thử

```bash
python manage.py migrate               # connections.0001, messaging.0001
python manage.py seed_demo --reset     # ứng viên demo bật công khai hồ sơ (trừ linh.do@demo.com),
                                       # recruiter@demo.com đã kết bạn + nhắn tin với candidate@demo.com,
                                       # đang chờ cuc.le@demo.com nhận lời mời
pytest                                 # 190 test (27 test mới trong apps/talents, connections, messaging)
```

Bảng mới: `connections`, `conversations`, `messages` (đã cập nhật `database/schema.sql`).
