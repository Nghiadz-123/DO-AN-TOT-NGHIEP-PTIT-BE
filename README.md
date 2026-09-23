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

**1. Clone project**
```bash
git clone <repo-url>
cd project
```

**2. Tạo môi trường ảo**
```bash
python -m venv venv
```
Kích hoạt:
```bash
venv\Scripts\activate   # Windows
```

**3. Cài thư viện**
```bash
pip install -r requirements.txt
```

**4. Cấu hình database PostgreSQL**
```sql
CREATE DATABASE ats_db;
```

**5. Cấu hình biến môi trường (.env)**
```env
DB_NAME=ats_db
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
OPENAI_API_KEY=your_api_key
```

**6. Chạy project**
```bash
python manage.py migrate
python manage.py runserver
```

---

## 📂 Cấu trúc thư mục
```text
project/
├── frontend/
├── backend/
├── database/
├── docs/
└── README.md
```

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
