# 🤖 Nền Tảng Hỗ Trợ Tuyển Dụng Thông Minh (ATS) Ứng Dụng AI

## 📌 Giới thiệu

Dự án xây dựng một hệ thống web kết nối tuyển dụng, tích hợp tính năng ATS (Applicant Tracking System) và AI để tối ưu hóa quy trình:
- **Dành cho ứng viên:** Ứng dụng kỹ thuật bóc tách dữ liệu (NLP) để đọc file CV, tích hợp AI để phân tích, chấm điểm CV, gợi ý chỉnh sửa và đề xuất việc làm phù hợp.
- **Dành cho nhà tuyển dụng:** Hỗ trợ đăng tin, quản lý quy trình. AI tự động sàng lọc, chấm điểm và xếp hạng (ranking) CV dựa trên độ khớp với JD.
- **Thuật toán cốt lõi:** Áp dụng Machine Learning và LLM để xây dựng hệ thống gợi ý và so khớp (matching) ngữ nghĩa.

---

## 🧑‍💻 Technology Stack

**🔹 Backend**
- Python (Django)
- REST API

**🔹 Cơ sở dữ liệu**
- PostgreSQL (Lưu trữ dữ liệu hệ thống quan hệ)
- ChromaDB (Cơ sở dữ liệu Vector lưu trữ embeddings)

**🔹 AI / Học máy (ML)**
- Gemini / OpenAI API
- Spacy (Xử lý ngôn ngữ tự nhiên)

**🔹 Công cụ hỗ trợ**
- Git: quản lý phiên bản, làm việc nhóm, tránh xung đột code
- Postman: kiểm thử API nhanh chóng
- Docker: đồng bộ môi trường phát triển và triển khai
- Visual Studio Code / PyCharm: môi trường lập trình

---

## ⚙️ Cài đặt môi trường Backend

Yêu cầu: Python 3.12, PostgreSQL ≥ 13 (hoặc SQLite để chạy nhanh).

**1. Clone project và tạo môi trường ảo**
```bash
git clone <repo-url>
cd DO-AN-TOT-NGHIEP-PTIT-BE/backend
py -3.12 -m venv venv
venv\Scripts\activate   # Windows
pip install -r requirements.txt
```

**2. Cấu hình database PostgreSQL**
```sql
CREATE DATABASE ats_db;
```

**3. Cấu hình biến môi trường**: sao chép `backend/.env.example` thành `backend/.env` rồi điền mật khẩu DB
```env
DB_ENGINE=postgresql        # hoặc sqlite (không cần cài PostgreSQL)
DB_NAME=ats_db
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
```

**4. Chạy project**
```bash
python manage.py migrate
python manage.py seed_demo         # dữ liệu demo: recruiter@demo.com / 123456
python manage.py createsuperuser   # tài khoản trang quản trị /admin/
python manage.py runserver
```
- API: `http://localhost:8000/api/v1/` — tài liệu Swagger: `http://localhost:8000/api/docs/`
- Chạy test: `pytest`

Giai đoạn 1 (đã triển khai): API dành cho **Nhà tuyển dụng** — xem [docs/employer-api.md](docs/employer-api.md) (giả định, kiến trúc, API, quy tắc nghiệp vụ, điểm mở rộng cho AI).

---

## 📂 Cấu trúc thư mục
```text
DO-AN-TOT-NGHIEP-PTIT-BE/
├── backend/
│   ├── config/          # Django project: settings (base/dev/prod/test), urls, celery
│   ├── common/          # Thành phần dùng chung: base model, permission, pagination, exception
│   └── apps/
│       ├── accounts/    # Authentication (JWT, custom User, role)
│       ├── catalog/     # Danh mục dùng chung: tỉnh/thành, ngành nghề, kỹ năng
│       ├── candidates/  # Hồ sơ ứng viên
│       ├── employers/   # Công ty & nhà tuyển dụng
│       ├── cvs/         # Upload, parse CV
│       ├── jobs/        # Tin tuyển dụng
│       ├── applications/# Ứng tuyển, pipeline ATS
│       └── ai/          # LLM, prompts, vector store, 4 chức năng AI
├── database/
├── docs/
├── docker-compose.yml
└── README.md
```

Chi tiết trách nhiệm từng thư mục/file: [docs/backend-structure.md](docs/backend-structure.md)

---

## 👥 Thành viên nhóm
- Thành viên 1: Doãn Đức Nghĩa
- Thành viên 2: Ngô Bá Đạt
- Thành viên 3: Lê Minh Ngọc

---

## 🚀 Hướng phát triển
- Tích hợp Chatbot AI hỗ trợ phỏng vấn sơ loại
- Tối ưu hóa tốc độ truy vấn trên hệ thống ChromaDB
- Mở rộng phân tích đa ngôn ngữ (Tiếng Anh, Tiếng Nhật)
