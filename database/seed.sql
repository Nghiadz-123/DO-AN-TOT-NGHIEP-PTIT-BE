-- ====================================================================================================
-- Smart ATS (CVision) - DỮ LIỆU MẪU
-- Chạy SAU schema.sql trên database CVision:
--   psql -U postgres -d CVision -v ON_ERROR_STOP=1 -f database/seed.sql
-- Mật khẩu mọi tài khoản: 123456. Admin: admin@example.com; NTD: hr@techcorp.vn ...;
--   ứng viên: candidate.python@gmail.com ... (danh sách đầy đủ ở bảng users bên dưới).
-- File CV mẫu: chép thư mục database/seed_cvs vào backend/private_media/seed để xem / tải CV:
--   Copy-Item database\seed_cvs backend\private_media\seed -Recurse      (PowerShell, ở thư mục gốc repo BE)
-- Tỉnh/thành, ngành nghề, kỹ năng tham chiếu theo slug của danh mục trong schema.sql.
-- ====================================================================================================

SET client_encoding = 'UTF8';
BEGIN;

-- ====================================================================================================
-- 1. TÀI KHOẢN
-- ====================================================================================================

-- users (25 dòng)
INSERT INTO "users" ("id", "email", "password", "full_name", "phone", "role", "is_active", "is_staff", "is_superuser", "email_verified_at", "last_login", "created_at", "updated_at", "deleted_at") VALUES
  ('00000000000000000000000000000001'::uuid, 'admin@example.com', 'pbkdf2_sha256$1000000$OpMVxEVugbSimLO9atE2kE$v4xU1aEqPC72WC49zhSgp73ckBi345BqJ7vaAfW2IFU=', 'Quản Trị Viên Hệ Thống', '0900000000', 'admin', TRUE, TRUE, TRUE, now(), NULL, now() - interval '30 days 0 hours', now() - interval '30 days 0 hours', NULL),
  ('00000000000000000000000000000002'::uuid, 'hr@techcorp.vn', 'pbkdf2_sha256$1000000$wQZXAwXk1uD1URVNC32eqi$G0wjdErn+ztRIXnBJgp3FqrnQaIwOZEHUGKva4I7iio=', 'Nguyễn Thị Hồng HR', '0901111111', 'employer', TRUE, FALSE, FALSE, now(), NULL, now() - interval '30 days 0 hours', now() - interval '30 days 0 hours', NULL),
  ('00000000000000000000000000000003'::uuid, 'recruitment@fintechglobal.com', 'pbkdf2_sha256$1000000$eK2S5GmWse3Mj89pcclXv4$8icwMxq2j+wBYit7+QtoOvCkUzacQOCS8sw729DbHLk=', 'Trần Văn Minh HR', '0902222222', 'employer', TRUE, FALSE, FALSE, now(), NULL, now() - interval '30 days 0 hours', now() - interval '30 days 0 hours', NULL),
  ('00000000000000000000000000000004'::uuid, 'careers@aisolutions.io', 'pbkdf2_sha256$1000000$Kdu805EnHJjrIo7daV8dRU$6kYiUqKCnRSjFj45XFevPgWhz6qIjYkx9fNAA5oiAic=', 'Hoàng Thu Trang Talent Lead', '0903333333', 'employer', TRUE, FALSE, FALSE, now(), NULL, now() - interval '30 days 0 hours', now() - interval '30 days 0 hours', NULL),
  ('00000000000000000000000000000005'::uuid, 'jobs@ecomstars.vn', 'pbkdf2_sha256$1000000$gsla2eFgiaSqEW2LXOOOGP$bvBRpXxEXcjcAf2k79oZPBt4h2PrvmxPOJ+yZCBcKa4=', 'Vũ Quốc Anh Head of HR', '0904444444', 'employer', TRUE, FALSE, FALSE, now(), NULL, now() - interval '30 days 0 hours', now() - interval '30 days 0 hours', NULL),
  ('00000000000000000000000000000006'::uuid, 'talent@cloudscale.net', 'pbkdf2_sha256$1000000$4BcYZf2jcQaQAA5fUbp89n$KbyBNyxk9yOUXqyqlMPZkOcbwV0r/n8JsotvUaF4mPA=', 'Đặng Thùy Dung HR Specialist', '0905555555', 'employer', TRUE, FALSE, FALSE, now(), NULL, now() - interval '30 days 0 hours', now() - interval '30 days 0 hours', NULL),
  ('00000000000000000000000000000007'::uuid, 'hiring@cyberdefense.vn', 'pbkdf2_sha256$1000000$c4F8bz9ImmiYS3jX7QLxNl$P9DbdQSi7GO8Kn+gTHirx78tEfKeo/MJn0h+4JCCEL0=', 'Lý Hải Đăng Recruiter', '0906666666', 'employer', TRUE, FALSE, FALSE, now(), NULL, now() - interval '30 days 0 hours', now() - interval '30 days 0 hours', NULL),
  ('00000000000000000000000000000008'::uuid, 'recruiter@logismart.com', 'pbkdf2_sha256$1000000$jZeINXpq43X0nXJSbV9ZG5$lgEiPblF2WLLURX+JDuto8tY7TEdXEy1nNyt7TVfYvc=', 'Phan Thanh Bình HR Lead', '0907777777', 'employer', TRUE, FALSE, FALSE, now(), NULL, now() - interval '30 days 0 hours', now() - interval '30 days 0 hours', NULL),
  ('00000000000000000000000000000009'::uuid, 'contact@edutech.vn', 'pbkdf2_sha256$1000000$fWNuPJ9SjojBqYOBZYBlSl$wiQKHihM6DMbxUnv373IdeJ42TwsvxAIuMK4HV78NIc=', 'Mai Lan Hương People Operations', '0908888888', 'employer', TRUE, FALSE, FALSE, now(), NULL, now() - interval '30 days 0 hours', now() - interval '30 days 0 hours', NULL),
  ('00000000000000000000000000000010'::uuid, 'candidate.python@gmail.com', 'pbkdf2_sha256$1000000$guhD9pJuXw4Bek5EPHkVLh$OrkKWydA59oh7nZdOp05dx0pXA/dkpWzHsb1ChWUoRc=', 'Lê Tuấn Kiệt', '0910000001', 'candidate', TRUE, FALSE, FALSE, now(), NULL, now() - interval '30 days 0 hours', now() - interval '30 days 0 hours', NULL),
  ('00000000000000000000000000000011'::uuid, 'candidate.frontend@gmail.com', 'pbkdf2_sha256$1000000$3Dpsu3zUCW1vEnV8AnQrW4$wHv0fc4FBQ6WCrvf5vGAuZfdwUmf1fCewta3vgH84E8=', 'Trần Bảo Anh', '0910000002', 'candidate', TRUE, FALSE, FALSE, now(), NULL, now() - interval '30 days 0 hours', now() - interval '30 days 0 hours', NULL),
  ('00000000000000000000000000000012'::uuid, 'candidate.java@gmail.com', 'pbkdf2_sha256$1000000$WO6n0gTXkPr1WBEn9sP4Py$oRyUSkKRSPLgyzBp5LkdDJYleUyFB/C6qxsWbBUa6LI=', 'Nguyễn Đăng Khoa', '0910000003', 'candidate', TRUE, FALSE, FALSE, now(), NULL, now() - interval '30 days 0 hours', now() - interval '30 days 0 hours', NULL),
  ('00000000000000000000000000000013'::uuid, 'candidate.devops@gmail.com', 'pbkdf2_sha256$1000000$Eun9UvUmA8TUmfKOUNr1df$SoOk1rs5r/ejrbWMC9N/e8mXP7zYdmHJazT2b3ulCHM=', 'Phạm Hoàng Nam', '0910000004', 'candidate', TRUE, FALSE, FALSE, now(), NULL, now() - interval '30 days 0 hours', now() - interval '30 days 0 hours', NULL),
  ('00000000000000000000000000000014'::uuid, 'candidate.uiux@gmail.com', 'pbkdf2_sha256$1000000$8apez7StVMoaicOf4lPiBb$F9Es2WRaksGU0706N5BrRw7R0qOXAmTuN0ylyZPJbsA=', 'Đinh Thảo Vy', '0910000005', 'candidate', TRUE, FALSE, FALSE, now(), NULL, now() - interval '30 days 0 hours', now() - interval '30 days 0 hours', NULL),
  ('00000000000000000000000000000015'::uuid, 'candidate.ai@gmail.com', 'pbkdf2_sha256$1000000$RgZE9z2nsogdMaACNm1LRZ$3dZIeZ5bFltAaDNAsLmRs1cHyvu8FctZgUnw5u3GJP0=', 'Võ Trọng Nghĩa', '0910000006', 'candidate', TRUE, FALSE, FALSE, now(), NULL, now() - interval '30 days 0 hours', now() - interval '30 days 0 hours', NULL),
  ('00000000000000000000000000000016'::uuid, 'candidate.golang@gmail.com', 'pbkdf2_sha256$1000000$yPBW9blILyNGY0rL4a41yJ$ho1OEdR8uwiLPLk2cKD/ECcRSYdnnkWqrjCXW0oT7Rc=', 'Bùi Đức Huy', '0910000007', 'candidate', TRUE, FALSE, FALSE, now(), NULL, now() - interval '30 days 0 hours', now() - interval '30 days 0 hours', NULL),
  ('00000000000000000000000000000017'::uuid, 'candidate.fullstack@gmail.com', 'pbkdf2_sha256$1000000$BrPPOxSmphCeaELmqY49pK$9q7JyjCL1GQBLV4tHBdjZ44e4G/ryJ3BnnS1dJh4aQ4=', 'Dương Gia Hân', '0910000008', 'candidate', TRUE, FALSE, FALSE, now(), NULL, now() - interval '30 days 0 hours', now() - interval '30 days 0 hours', NULL),
  ('00000000000000000000000000000018'::uuid, 'candidate.fresher1@gmail.com', 'pbkdf2_sha256$1000000$JMBK6kibQvZzkgWdvhRuGo$foV9efKS9tZuJpo8pko+mm5gf/2uxrYammYWYYXHNaQ=', 'Trương Minh Trí', '0910000009', 'candidate', TRUE, FALSE, FALSE, now(), NULL, now() - interval '30 days 0 hours', now() - interval '30 days 0 hours', NULL),
  ('00000000000000000000000000000019'::uuid, 'candidate.fresher2@gmail.com', 'pbkdf2_sha256$1000000$iKsTK05Kv7jpNfT2TxCCiZ$lczoUZ6emHqKHDhvNHj3/7GXGowkDv7ywm3UJIwx7L8=', 'Lâm Khánh Linh', '0910000010', 'candidate', TRUE, FALSE, FALSE, now(), NULL, now() - interval '30 days 0 hours', now() - interval '30 days 0 hours', NULL),
  ('00000000000000000000000000000020'::uuid, 'candidate.intern1@gmail.com', 'pbkdf2_sha256$1000000$agHfvvrQaRXyUNzpaypJjt$e8LKKwvyXBp1NVsHH5+9ZbA8LsdHp6s1Qh9pKwa+oIw=', 'Hà Quang Sáng', '0910000011', 'candidate', TRUE, FALSE, FALSE, now(), NULL, now() - interval '30 days 0 hours', now() - interval '30 days 0 hours', NULL),
  ('00000000000000000000000000000021'::uuid, 'candidate.intern2@gmail.com', 'pbkdf2_sha256$1000000$XwrlLVk859fcRLhLhWq2tw$keXHrHFK+Yl2KkXbMIm+Fv8e/IlJgSUMXhxv0nSdiKc=', 'Chu Ngọc Mai', '0910000012', 'candidate', TRUE, FALSE, FALSE, now(), NULL, now() - interval '30 days 0 hours', now() - interval '30 days 0 hours', NULL),
  ('00000000000000000000000000000022'::uuid, 'candidate.manager@gmail.com', 'pbkdf2_sha256$1000000$tDZTUBACRF0YK1pVCqBHq3$aBPfIs4oenpGSzULo0B96pjoOO67ISq4WzGtkooAjpU=', 'Đoàn Nhật Quang', '0910000013', 'candidate', TRUE, FALSE, FALSE, now(), NULL, now() - interval '30 days 0 hours', now() - interval '30 days 0 hours', NULL),
  ('00000000000000000000000000000023'::uuid, 'candidate.director@gmail.com', 'pbkdf2_sha256$1000000$NzEQywDHlpJx2MUfV0kwbb$j/0k2JGMxRDRQMETc25z0iJq3xm8jWT2pkVTZWTS/jo=', 'Ngô Kiến Huy', '0910000014', 'candidate', TRUE, FALSE, FALSE, now(), NULL, now() - interval '30 days 0 hours', now() - interval '30 days 0 hours', NULL),
  ('00000000000000000000000000000024'::uuid, 'candidate.security@gmail.com', 'pbkdf2_sha256$1000000$69aVTXvnY8Mtp5jggKysDW$fvCzFelQMgOeEpar3ZmFX1833hUazVaihiX1Siw0rOg=', 'Lý Tuấn Kiệt', '0910000015', 'candidate', TRUE, FALSE, FALSE, now(), NULL, now() - interval '30 days 0 hours', now() - interval '30 days 0 hours', NULL),
  ('00000000000000000000000000000025'::uuid, 'candidate.qa@gmail.com', 'pbkdf2_sha256$1000000$NjKO0OK5dVLC087syiMNIY$9SlRqitaF/U5TCq39wyPfn9mDqdjO2J+b8yeXcKBBR0=', 'Tống Ánh Tuyết', '0910000016', 'candidate', TRUE, FALSE, FALSE, now(), NULL, now() - interval '30 days 0 hours', now() - interval '30 days 0 hours', NULL);


-- ====================================================================================================
-- 2. ỨNG VIÊN
-- ====================================================================================================

-- candidate_profiles (16 dòng)
INSERT INTO "candidate_profiles" ("id", "user_id", "headline", "date_of_birth", "gender", "address", "location_id", "summary", "years_of_experience", "current_level", "desired_position", "desired_salary_min", "desired_salary_max", "salary_currency", "desired_job_type", "desired_work_mode", "is_open_to_work", "is_public", "created_at", "updated_at") VALUES
  ('33333333333333333333333333333310'::uuid, '00000000000000000000000000000010'::uuid, 'Backend Engineer | 3 năm kinh nghiệm Python/Django', '1998-05-15'::date, 'male', '123 Cầu Giấy, Hà Nội', (SELECT id FROM locations WHERE slug = 'ha-noi'), 'Lập trình viên Backend có thế mạnh về thiết kế API RESTful, tối ưu cơ sở dữ liệu và microservices.', 3.0, 'staff', 'Senior Python Developer', 22000000, 38000000, 'VND', 'full_time', 'hybrid', TRUE, TRUE, now() - interval '30 days 0 hours', now() - interval '30 days 0 hours'),
  ('33333333333333333333333333333311'::uuid, '00000000000000000000000000000011'::uuid, 'Frontend Developer | ReactJS & TypeScript', '2000-09-20'::date, 'female', '456 Lê Duẩn, Đà Nẵng', (SELECT id FROM locations WHERE slug = 'da-nang'), 'Chuyên xây dựng web app tương tác cao bằng ReactJS, Redux Toolkit, TailwindCSS và Next.js.', 2.5, 'staff', 'Senior Frontend Engineer', 18000000, 30000000, 'VND', 'full_time', 'remote', TRUE, TRUE, now() - interval '30 days 0 hours', now() - interval '30 days 0 hours'),
  ('33333333333333333333333333333312'::uuid, '00000000000000000000000000000012'::uuid, 'Java Enterprise Architect | Spring Boot Specialist', '1993-02-10'::date, 'male', '789 Nguyễn Huệ, Quận 1, TP.HCM', (SELECT id FROM locations WHERE slug = 'ho-chi-minh'), 'Hơn 7 năm kinh nghiệm với hạ tầng tài chính, hệ thống ngân hàng chịu tải lớn bằng Java và Spring Cloud.', 7.0, 'supervisor', 'Software Architect / Tech Lead', 45000000, 70000000, 'VND', 'full_time', 'onsite', TRUE, TRUE, now() - interval '30 days 0 hours', now() - interval '30 days 0 hours'),
  ('33333333333333333333333333333313'::uuid, '00000000000000000000000000000013'::uuid, 'DevOps & Site Reliability Engineer (SRE)', '1996-07-28'::date, 'male', '12 Cách Mạng Tháng 8, Cần Thơ', (SELECT id FROM locations WHERE slug = 'can-tho'), 'Chuyên gia xây dựng pipeline CI/CD, quản trị hạ tầng AWS và cụm Kubernetes đa vùng.', 4.5, 'staff', 'Lead DevOps Engineer', 30000000, 50000000, 'VND', 'full_time', 'remote', TRUE, TRUE, now() - interval '30 days 0 hours', now() - interval '30 days 0 hours'),
  ('33333333333333333333333333333314'::uuid, '00000000000000000000000000000014'::uuid, 'Senior UI/UX Designer | Product Design', '1997-12-05'::date, 'female', '55 Quang Trung, Hải Phòng', (SELECT id FROM locations WHERE slug = 'hai-phong'), 'Kinh nghiệm thiết kế trải nghiệm người dùng các hệ thống SaaS B2B và siêu ứng dụng bán lẻ.', 3.5, 'staff', 'Lead Product Designer', 20000000, 35000000, 'VND', 'full_time', 'hybrid', TRUE, TRUE, now() - interval '30 days 0 hours', now() - interval '30 days 0 hours'),
  ('33333333333333333333333333333315'::uuid, '00000000000000000000000000000015'::uuid, 'AI/ML Engineer | Computer Vision & NLP', '1995-04-18'::date, 'male', '100 Đại Cồ Việt, Hai Bà Trưng, Hà Nội', (SELECT id FROM locations WHERE slug = 'ha-noi'), 'Phát triển mô hình Deep Learning ứng dụng cho nhận diện khuôn mặt và chatbot thông minh.', 4.0, 'staff', 'Senior AI Engineer', 35000000, 60000000, 'VND', 'full_time', 'hybrid', TRUE, TRUE, now() - interval '30 days 0 hours', now() - interval '30 days 0 hours'),
  ('33333333333333333333333333333316'::uuid, '00000000000000000000000000000016'::uuid, 'Golang Backend Developer | High Throughput System', '1997-08-30'::date, 'male', '68 Hoàng Văn Thụ, Bình Dương', (SELECT id FROM locations WHERE slug = 'ho-chi-minh'), 'Xây dựng core giao dịch tốc độ cao bằng Go, gRPC, Kafka và Redis.', 3.0, 'staff', 'Backend Go Engineer', 25000000, 42000000, 'VND', 'full_time', 'remote', TRUE, TRUE, now() - interval '30 days 0 hours', now() - interval '30 days 0 hours'),
  ('33333333333333333333333333333317'::uuid, '00000000000000000000000000000017'::uuid, 'Fullstack JavaScript Developer (Node.js + React)', '1999-03-12'::date, 'female', '200 Võ Thị Sáu, Quận 3, TP.HCM', (SELECT id FROM locations WHERE slug = 'ho-chi-minh'), 'Xây dựng ứng dụng hoàn chỉnh từ giao diện đến server backend phục vụ thương mại điện tử.', 2.5, 'staff', 'Fullstack Engineer', 18000000, 28000000, 'VND', 'full_time', 'hybrid', TRUE, TRUE, now() - interval '30 days 0 hours', now() - interval '30 days 0 hours'),
  ('33333333333333333333333333333318'::uuid, '00000000000000000000000000000018'::uuid, 'Fresher Backend Developer | Java & Spring Boot', '2002-11-20'::date, 'male', '45 Hoàng Diệu, Đà Nẵng', (SELECT id FROM locations WHERE slug = 'da-nang'), 'Tốt nghiệp loại Giỏi ngành CNTT, có dự án thực tế về REST API và cơ sở dữ liệu quan hệ.', 0.5, 'fresher', 'Junior Backend Developer', 9000000, 14000000, 'VND', 'full_time', 'onsite', TRUE, TRUE, now() - interval '30 days 0 hours', now() - interval '30 days 0 hours'),
  ('33333333333333333333333333333319'::uuid, '00000000000000000000000000000019'::uuid, 'Fresher Frontend Developer | VueJS & Nuxt', '2002-06-15'::date, 'female', '32 Hùng Vương, Huế', (SELECT id FROM locations WHERE slug = 'hue'), 'Nắm vững kiến thức HTML/CSS/JavaScript hiện đại, ham học hỏi và tư duy thiết kế giao diện tốt.', 0.5, 'fresher', 'Junior Frontend Developer', 8000000, 13000000, 'VND', 'full_time', 'hybrid', TRUE, TRUE, now() - interval '30 days 0 hours', now() - interval '30 days 0 hours'),
  ('33333333333333333333333333333320'::uuid, '00000000000000000000000000000020'::uuid, 'Intern Python Developer', '2003-01-22'::date, 'male', '88 Trần Phú, Hà Đông, Hà Nội', (SELECT id FROM locations WHERE slug = 'ha-noi'), 'Sinh viên năm cuối tìm kiếm cơ hội thực tập phát triển web và xử lý dữ liệu với Python.', 0.0, 'intern', 'Python Intern', 3000000, 6000000, 'VND', 'internship', 'onsite', TRUE, TRUE, now() - interval '30 days 0 hours', now() - interval '30 days 0 hours'),
  ('33333333333333333333333333333321'::uuid, '00000000000000000000000000000021'::uuid, 'Intern UI/UX Designer', '2003-08-08'::date, 'female', '15 Lê Lợi, TP. Vũng Tàu', (SELECT id FROM locations WHERE slug = 'ho-chi-minh'), 'Yêu thích thiết kế trải nghiệm người dùng, thành thạo công cụ Figma và vẽ vector.', 0.0, 'intern', 'Design Intern', 3000000, 5000000, 'VND', 'internship', 'hybrid', TRUE, TRUE, now() - interval '30 days 0 hours', now() - interval '30 days 0 hours'),
  ('33333333333333333333333333333322'::uuid, '00000000000000000000000000000022'::uuid, 'Engineering Manager | 10+ năm kinh nghiệm quản lý', '1988-10-14'::date, 'male', '50 Nam Kỳ Khởi Nghĩa, Quận 1, TP.HCM', (SELECT id FROM locations WHERE slug = 'ho-chi-minh'), 'Kinh nghiệm dẫn dắt đội ngũ kỹ thuật 40+ kỹ sư, triển khai quy trình Agile/Scrum và chuyển đổi số.', 10.0, 'manager', 'Engineering Manager / Head of Tech', 60000000, 95000000, 'VND', 'full_time', 'hybrid', TRUE, TRUE, now() - interval '30 days 0 hours', now() - interval '30 days 0 hours'),
  ('33333333333333333333333333333323'::uuid, '00000000000000000000000000000023'::uuid, 'Chief Technology Officer (CTO) | Định hướng công nghệ', '1984-05-02'::date, 'male', '12 Xuân Diệu, Tây Hồ, Hà Nội', (SELECT id FROM locations WHERE slug = 'ha-noi'), 'Từng giữ vai trò CTO tại các startup kỳ lân công nghệ, quản trị kiến trúc tổng thể và ngân sách R&D.', 14.0, 'director', 'CTO / VP of Engineering', 100000000, 160000000, 'VND', 'full_time', 'hybrid', FALSE, TRUE, now() - interval '30 days 0 hours', now() - interval '30 days 0 hours'),
  ('33333333333333333333333333333324'::uuid, '00000000000000000000000000000024'::uuid, 'Cybersecurity Specialist | SOC & Pentest', '1996-09-09'::date, 'male', '230 Lê Duẩn, TP. Vinh, Nghệ An', (SELECT id FROM locations WHERE slug = 'nghe-an'), 'Chứng chỉ CEH, OSCP, chuyên đánh giá an ninh mạng và rà soát lỗ hổng hệ thống.', 4.0, 'staff', 'Security Specialist', 28000000, 48000000, 'VND', 'full_time', 'remote', TRUE, TRUE, now() - interval '30 days 0 hours', now() - interval '30 days 0 hours'),
  ('33333333333333333333333333333325'::uuid, '00000000000000000000000000000025'::uuid, 'QA/QC Automation Lead | Cypress & Selenium', '1998-02-28'::date, 'female', '77 Nguyễn Trãi, Thanh Xuân, Hà Nội', (SELECT id FROM locations WHERE slug = 'ha-noi'), 'Xây dựng khung kiểm thử tự động, tích hợp CI/CD để đảm bảo chất lượng phát hành liên tục.', 3.5, 'staff', 'QA Automation Lead', 20000000, 32000000, 'VND', 'full_time', 'hybrid', TRUE, TRUE, now() - interval '30 days 0 hours', now() - interval '30 days 0 hours');


-- ====================================================================================================
-- 3. CÔNG TY VÀ NHÀ TUYỂN DỤNG
-- ====================================================================================================

-- companies (8 dòng)
INSERT INTO "companies" ("id", "name", "slug", "tax_code", "logo", "website", "email", "phone", "address", "location_id", "industry_id", "company_size", "founded_year", "description", "verification_status", "verified_at", "verified_by_id", "created_by_id", "created_at", "updated_at", "deleted_at") VALUES
  ('11111111111111111111111111111101'::uuid, 'Công ty Cổ phần Công nghệ TechCorp Vietnam', 'techcorp-vietnam', '0101234567', '', 'https://techcorp.vn', 'contact@techcorp.vn', '02439998888', 'Tầng 5, Tòa nhà A, Cầu Giấy, Hà Nội', (SELECT id FROM locations WHERE slug = 'ha-noi'), (SELECT id FROM industries WHERE slug = 'cong-nghe-thong-tin'), '51-200', 2018, 'Doanh nghiệp tiên phong cung cấp giải pháp Cloud và phát triển phần mềm theo yêu cầu.', 'verified', now(), '00000000000000000000000000000001'::uuid, '00000000000000000000000000000002'::uuid, now() - interval '60 days 0 hours', now() - interval '60 days 0 hours', NULL),
  ('11111111111111111111111111111102'::uuid, 'Tập đoàn Giải pháp Tài chính FinTech Global', 'fintech-global', '0309876543', '', 'https://fintechglobal.com', 'hr@fintechglobal.com', '02837776666', 'Tầng 12, Tòa nhà Bitexco, Quận 1, TP.HCM', (SELECT id FROM locations WHERE slug = 'ho-chi-minh'), (SELECT id FROM industries WHERE slug = 'tai-chinh-ngan-hang'), '201-500', 2015, 'Cung cấp hạ tầng thanh toán số và ngân hàng mở cho các định chế tài chính quốc tế.', 'verified', now(), '00000000000000000000000000000001'::uuid, '00000000000000000000000000000003'::uuid, now() - interval '60 days 0 hours', now() - interval '60 days 0 hours', NULL),
  ('11111111111111111111111111111103'::uuid, 'Công ty TNHH Giải pháp Trí tuệ Nhân tạo AI Solutions Corp', 'ai-solutions-corp', '0109998877', '', 'https://aisolutions.io', 'info@aisolutions.io', '02431112222', 'Tầng 8, Tòa Keangnam, Nam Từ Liêm, Hà Nội', (SELECT id FROM locations WHERE slug = 'ha-noi'), (SELECT id FROM industries WHERE slug = 'cong-nghe-thong-tin'), '11-50', 2021, 'R&D các sản phẩm thị giác máy tính và xử lý ngôn ngữ tự nhiên ứng dụng trong doanh nghiệp.', 'verified', now(), '00000000000000000000000000000001'::uuid, '00000000000000000000000000000004'::uuid, now() - interval '60 days 0 hours', now() - interval '60 days 0 hours', NULL),
  ('11111111111111111111111111111104'::uuid, 'Sàn Thương mại Điện tử E-Commerce Stars', 'e-commerce-stars', '0301112233', '', 'https://ecomstars.vn', 'recruitment@ecomstars.vn', '02834445555', 'Tầng 3, Tòa nhà D, Quận 3, TP.HCM', (SELECT id FROM locations WHERE slug = 'ho-chi-minh'), (SELECT id FROM industries WHERE slug = 'thuong-mai-dien-tu'), '501-1000', 2017, 'Nền tảng mua sắm trực tuyến với chuỗi logistics hiện đại và độ phủ sóng toàn quốc.', 'verified', now(), '00000000000000000000000000000001'::uuid, '00000000000000000000000000000005'::uuid, now() - interval '60 days 0 hours', now() - interval '60 days 0 hours', NULL),
  ('11111111111111111111111111111105'::uuid, 'Công ty Hạ tầng Đám mây CloudScale Networks', 'cloudscale-networks', '0405556677', '', 'https://cloudscale.net', 'career@cloudscale.net', '02363888999', 'Khu Công viên Phần mềm Đà Nẵng, Hải Châu, Đà Nẵng', (SELECT id FROM locations WHERE slug = 'da-nang'), (SELECT id FROM industries WHERE slug = 'cong-nghe-thong-tin'), '51-200', 2019, 'Cung cấp hạ tầng ảo hóa bare-metal, cụm máy chủ Kubernetes và dịch vụ an toàn mạng.', 'verified', now(), '00000000000000000000000000000001'::uuid, '00000000000000000000000000000006'::uuid, now() - interval '60 days 0 hours', now() - interval '60 days 0 hours', NULL),
  ('11111111111111111111111111111106'::uuid, 'Công ty An toàn Thông tin CyberDefense Vietnam', 'cyberdefense-vietnam', '0106667788', '', 'https://cyberdefense.vn', 'security@cyberdefense.vn', '02437778899', 'Tòa CMC Tower, Cầu Giấy, Hà Nội', (SELECT id FROM locations WHERE slug = 'ha-noi'), (SELECT id FROM industries WHERE slug = 'cong-nghe-thong-tin'), '11-50', 2020, 'Đơn vị kiểm định an ninh ứng dụng và phản ứng sự cố không gian mạng chuyên nghiệp.', 'verified', now(), '00000000000000000000000000000001'::uuid, '00000000000000000000000000000007'::uuid, now() - interval '60 days 0 hours', now() - interval '60 days 0 hours', NULL),
  ('11111111111111111111111111111107'::uuid, 'LogiSmart Vận tải Thông minh', 'logismart-van-tai', '0308889900', '', 'https://logismart.com', 'jobs@logismart.com', '02839991122', 'Khu Công nghệ cao Quận 9, TP. Thủ Đức, TP.HCM', (SELECT id FROM locations WHERE slug = 'ho-chi-minh'), (SELECT id FROM industries WHERE slug = 'logistics-van-tai'), '201-500', 2016, 'Giải pháp số hóa chuỗi cung ứng và điều phối vận tải chặng cuối tự động bằng IoT.', 'verified', now(), '00000000000000000000000000000001'::uuid, '00000000000000000000000000000008'::uuid, now() - interval '60 days 0 hours', now() - interval '60 days 0 hours', NULL),
  ('11111111111111111111111111111108'::uuid, 'Công ty Giáo dục Số EduTech Future', 'edutech-future', '0103334455', '', 'https://edutech.vn', 'hello@edutech.vn', '02435556677', 'Tầng 4, Tòa Hapulico, Thanh Xuân, Hà Nội', (SELECT id FROM locations WHERE slug = 'ha-noi'), (SELECT id FROM industries WHERE slug = 'giao-duc-dao-tao'), '51-200', 2022, 'Hệ thống học trực tuyến cá nhân hóa với trợ lý gia sư trí tuệ nhân tạo.', 'verified', now(), '00000000000000000000000000000001'::uuid, '00000000000000000000000000000009'::uuid, now() - interval '60 days 0 hours', now() - interval '60 days 0 hours', NULL);

-- recruiters (8 dòng)
INSERT INTO "recruiters" ("id", "user_id", "company_id", "position", "company_role", "status", "joined_at", "created_at", "updated_at") VALUES
  ('22222222222222222222222222222201'::uuid, '00000000000000000000000000000002'::uuid, '11111111111111111111111111111101'::uuid, 'HR Director', 'owner', 'active', now() - interval '60 days 0 hours', now() - interval '60 days 0 hours', now() - interval '60 days 0 hours'),
  ('22222222222222222222222222222202'::uuid, '00000000000000000000000000000003'::uuid, '11111111111111111111111111111102'::uuid, 'Head of Talent Acquisition', 'owner', 'active', now() - interval '60 days 0 hours', now() - interval '60 days 0 hours', now() - interval '60 days 0 hours'),
  ('22222222222222222222222222222203'::uuid, '00000000000000000000000000000004'::uuid, '11111111111111111111111111111103'::uuid, 'Talent Partner', 'owner', 'active', now() - interval '60 days 0 hours', now() - interval '60 days 0 hours', now() - interval '60 days 0 hours'),
  ('22222222222222222222222222222204'::uuid, '00000000000000000000000000000005'::uuid, '11111111111111111111111111111104'::uuid, 'Senior Recruiter', 'owner', 'active', now() - interval '60 days 0 hours', now() - interval '60 days 0 hours', now() - interval '60 days 0 hours'),
  ('22222222222222222222222222222205'::uuid, '00000000000000000000000000000006'::uuid, '11111111111111111111111111111105'::uuid, 'HR Lead', 'owner', 'active', now() - interval '60 days 0 hours', now() - interval '60 days 0 hours', now() - interval '60 days 0 hours'),
  ('22222222222222222222222222222206'::uuid, '00000000000000000000000000000007'::uuid, '11111111111111111111111111111106'::uuid, 'Recruitment Specialist', 'owner', 'active', now() - interval '60 days 0 hours', now() - interval '60 days 0 hours', now() - interval '60 days 0 hours'),
  ('22222222222222222222222222222207'::uuid, '00000000000000000000000000000008'::uuid, '11111111111111111111111111111107'::uuid, 'HR Manager', 'owner', 'active', now() - interval '60 days 0 hours', now() - interval '60 days 0 hours', now() - interval '60 days 0 hours'),
  ('22222222222222222222222222222208'::uuid, '00000000000000000000000000000009'::uuid, '11111111111111111111111111111108'::uuid, 'People Lead', 'owner', 'active', now() - interval '60 days 0 hours', now() - interval '60 days 0 hours', now() - interval '60 days 0 hours');


-- ====================================================================================================
-- 4. CV
-- ====================================================================================================

-- cvs (16 dòng)
INSERT INTO "cvs" ("id", "candidate_id", "title", "file", "original_filename", "mime_type", "file_size", "file_hash", "language", "is_default", "parse_status", "parse_error", "raw_text", "parsed_data", "parsed_at", "created_at", "updated_at", "deleted_at") VALUES
  ('44444444444444444444444444444410'::uuid, '33333333333333333333333333333310'::uuid, 'CV Lê Tuấn Kiệt - Python Engineer', 'seed/seed_cv_01.pdf', 'CV_LeTuanKiet_Python.pdf', 'application/pdf', 1339, '6083c64921154eec90d7770729fc017abaf545f4056107715ae603fc3e675886', 'vi', TRUE, 'completed', '', 'Lê Tuấn Kiệt
Backend Engineer | 3 năm kinh nghiệm Python/Django
candidate.python@gmail.com | 0910000001

GIỚI THIỆU
Lập trình viên Backend có thế mạnh về thiết kế API RESTful, tối ưu cơ sở dữ liệu và microservices.

KỸ NĂNG
Python, PostgreSQL, Docker, Redis

KINH NGHIỆM
Nội dung chi tiết CV Backend Developer...', '{"version": 1, "source": "parser", "stats": {"pages": 1, "words": 51, "characters": 312}, "contact": {"emails": ["candidate.python@gmail.com"], "phones": ["0910000001"], "links": []}, "skills": ["Python", "PostgreSQL", "Docker", "Redis"]}'::jsonb, now() - interval '25 days 0 hours', now() - interval '25 days 0 hours', now() - interval '25 days 0 hours', NULL),
  ('44444444444444444444444444444411'::uuid, '33333333333333333333333333333311'::uuid, 'CV Trần Bảo Anh - Frontend React', 'seed/seed_cv_02.pdf', 'CV_TranBaoAnh_Frontend.pdf', 'application/pdf', 1320, '28d95a64fa6690eea80ebb8af671557391bad87155c2097c8a377461e1dfefce', 'vi', TRUE, 'completed', '', 'Trần Bảo Anh
Frontend Developer | ReactJS & TypeScript
candidate.frontend@gmail.com | 0910000002

GIỚI THIỆU
Chuyên xây dựng web app tương tác cao bằng ReactJS, Redux Toolkit, TailwindCSS và Next.js.

KỸ NĂNG
ReactJS, TypeScript, Next.js

KINH NGHIỆM
Kinh nghiệm phát triển ReactJS, Next.js...', '{"version": 1, "source": "parser", "stats": {"pages": 1, "words": 42, "characters": 293}, "contact": {"emails": ["candidate.frontend@gmail.com"], "phones": ["0910000002"], "links": []}, "skills": ["ReactJS", "TypeScript", "Next.js"]}'::jsonb, now() - interval '25 days 0 hours', now() - interval '25 days 0 hours', now() - interval '25 days 0 hours', NULL),
  ('44444444444444444444444444444412'::uuid, '33333333333333333333333333333312'::uuid, 'CV Nguyễn Đăng Khoa - Java Architect', 'seed/seed_cv_03.pdf', 'CV_NguyenDangKhoa_Java.pdf', 'application/pdf', 1420, '5c5351e8c055bad53ee5d46f0c08b27031f728732e476fa34a6045bd8759df0c', 'en', TRUE, 'completed', '', 'Nguyễn Đăng Khoa
Java Enterprise Architect | Spring Boot Specialist
candidate.java@gmail.com | 0910000003

GIỚI THIỆU
Hơn 7 năm kinh nghiệm với hạ tầng tài chính, hệ thống ngân hàng chịu tải lớn bằng Java và Spring Cloud.

KỸ NĂNG
Java, Spring Boot, PostgreSQL, Microservices

KINH NGHIỆM
Full profile Java Solution Architect with 7 years experience...', '{"version": 1, "source": "parser", "stats": {"pages": 1, "words": 55, "characters": 352}, "contact": {"emails": ["candidate.java@gmail.com"], "phones": ["0910000003"], "links": []}, "skills": ["Java", "Spring Boot", "PostgreSQL", "Microservices"]}'::jsonb, now() - interval '25 days 0 hours', now() - interval '25 days 0 hours', now() - interval '25 days 0 hours', NULL),
  ('44444444444444444444444444444413'::uuid, '33333333333333333333333333333313'::uuid, 'CV Phạm Hoàng Nam - DevOps SRE', 'seed/seed_cv_04.pdf', 'CV_PhamHoangNam_DevOps.pdf', 'application/pdf', 1343, '20758631ad154f8434b5017bec0c132d29ea2b6bee9e02b98346d02b60fe6202', 'vi', TRUE, 'completed', '', 'Phạm Hoàng Nam
DevOps & Site Reliability Engineer (SRE)
candidate.devops@gmail.com | 0910000004

GIỚI THIỆU
Chuyên gia xây dựng pipeline CI/CD, quản trị hạ tầng AWS và cụm Kubernetes đa vùng.

KỸ NĂNG
Docker, Kubernetes, AWS Cloud, CI/CD

KINH NGHIỆM
Kinh nghiệm triển khai Kubernetes, AWS và Terraform...', '{"version": 1, "source": "parser", "stats": {"pages": 1, "words": 47, "characters": 305}, "contact": {"emails": ["candidate.devops@gmail.com"], "phones": ["0910000004"], "links": []}, "skills": ["Docker", "Kubernetes", "AWS Cloud", "CI/CD"]}'::jsonb, now() - interval '25 days 0 hours', now() - interval '25 days 0 hours', now() - interval '25 days 0 hours', NULL),
  ('44444444444444444444444444444414'::uuid, '33333333333333333333333333333314'::uuid, 'CV Đinh Thảo Vy - UI UX Product', 'seed/seed_cv_05.pdf', 'CV_DinhThaoVy_UIUX.pdf', 'application/pdf', 1329, '615384c891291d5d874aeda4f7e664e4fc799a7a6e6420b96ea386939ed14dc0', 'vi', TRUE, 'completed', '', 'Đinh Thảo Vy
Senior UI/UX Designer | Product Design
candidate.uiux@gmail.com | 0910000005

GIỚI THIỆU
Kinh nghiệm thiết kế trải nghiệm người dùng các hệ thống SaaS B2B và siêu ứng dụng bán lẻ.

KỸ NĂNG
Figma, UI/UX, User Research

KINH NGHIỆM
Hồ sơ năng lực thiết kế giao diện sản phẩm số Figma...', '{"version": 1, "source": "parser", "stats": {"pages": 1, "words": 53, "characters": 297}, "contact": {"emails": ["candidate.uiux@gmail.com"], "phones": ["0910000005"], "links": []}, "skills": ["Figma", "UI/UX", "User Research"]}'::jsonb, now() - interval '25 days 0 hours', now() - interval '25 days 0 hours', now() - interval '25 days 0 hours', NULL),
  ('44444444444444444444444444444415'::uuid, '33333333333333333333333333333315'::uuid, 'CV Võ Trọng Nghĩa - AI Engineer', 'seed/seed_cv_06.pdf', 'CV_VoTrongNghia_AI.pdf', 'application/pdf', 1364, 'bc7595a9b21174560be2ec3a9bf04d15f76b5f3f40ed61dcd0d4dc51a6566deb', 'en', TRUE, 'completed', '', 'Võ Trọng Nghĩa
AI/ML Engineer | Computer Vision & NLP
candidate.ai@gmail.com | 0910000006

GIỚI THIỆU
Phát triển mô hình Deep Learning ứng dụng cho nhận diện khuôn mặt và chatbot thông minh.

KỸ NĂNG
Python, TensorFlow, PyTorch, Computer Vision

KINH NGHIỆM
Applied AI Researcher with TensorFlow and PyTorch expertise...', '{"version": 1, "source": "parser", "stats": {"pages": 1, "words": 49, "characters": 320}, "contact": {"emails": ["candidate.ai@gmail.com"], "phones": ["0910000006"], "links": []}, "skills": ["Python", "TensorFlow", "PyTorch", "Computer Vision"]}'::jsonb, now() - interval '25 days 0 hours', now() - interval '25 days 0 hours', now() - interval '25 days 0 hours', NULL),
  ('44444444444444444444444444444416'::uuid, '33333333333333333333333333333316'::uuid, 'CV Bùi Đức Huy - Golang Backend', 'seed/seed_cv_07.pdf', 'CV_BuiDucHuy_Golang.pdf', 'application/pdf', 1319, '2dd7ed03e390e068d07265c2f826839deee2becae48111cf2f276d6ad488a44d', 'vi', TRUE, 'completed', '', 'Bùi Đức Huy
Golang Backend Developer | High Throughput System
candidate.golang@gmail.com | 0910000007

GIỚI THIỆU
Xây dựng core giao dịch tốc độ cao bằng Go, gRPC, Kafka và Redis.

KỸ NĂNG
Go (Golang), PostgreSQL, Redis, Kafka

KINH NGHIỆM
Chuyên gia Golang hệ thống chịu tải cao...', '{"version": 1, "source": "parser", "stats": {"pages": 1, "words": 46, "characters": 282}, "contact": {"emails": ["candidate.golang@gmail.com"], "phones": ["0910000007"], "links": []}, "skills": ["Go (Golang)", "PostgreSQL", "Redis", "Kafka"]}'::jsonb, now() - interval '25 days 0 hours', now() - interval '25 days 0 hours', now() - interval '25 days 0 hours', NULL),
  ('44444444444444444444444444444417'::uuid, '33333333333333333333333333333317'::uuid, 'CV Dương Gia Hân - Fullstack JS', 'seed/seed_cv_08.pdf', 'CV_DuongGiaHan_Fullstack.pdf', 'application/pdf', 1350, 'e50f49b6f7efc7cc7d7234b625952efabd9d12c0eefb2b55852d6e3cc0fe696b', 'vi', TRUE, 'completed', '', 'Dương Gia Hân
Fullstack JavaScript Developer (Node.js + React)
candidate.fullstack@gmail.com | 0910000008

GIỚI THIỆU
Xây dựng ứng dụng hoàn chỉnh từ giao diện đến server backend phục vụ thương mại điện tử.

KỸ NĂNG
Node.js, ReactJS, MongoDB

KINH NGHIỆM
Fullstack Developer with Node.js, Express and ReactJS...', '{"version": 1, "source": "parser", "stats": {"pages": 1, "words": 46, "characters": 311}, "contact": {"emails": ["candidate.fullstack@gmail.com"], "phones": ["0910000008"], "links": []}, "skills": ["Node.js", "ReactJS", "MongoDB"]}'::jsonb, now() - interval '25 days 0 hours', now() - interval '25 days 0 hours', now() - interval '25 days 0 hours', NULL),
  ('44444444444444444444444444444418'::uuid, '33333333333333333333333333333318'::uuid, 'CV Trương Minh Trí - Fresher Java', 'seed/seed_cv_09.pdf', 'CV_TruongMinhTri_Java.pdf', 'application/pdf', 1310, '5f155004ad59c464904bcc7b41b5476005474783151e70901f3f2c618e37251c', 'vi', TRUE, 'completed', '', 'Trương Minh Trí
Fresher Backend Developer | Java & Spring Boot
candidate.fresher1@gmail.com | 0910000009

GIỚI THIỆU
Tốt nghiệp loại Giỏi ngành CNTT, có dự án thực tế về REST API và cơ sở dữ liệu quan hệ.

KỸ NĂNG
Java, Spring Boot

KINH NGHIỆM
Hồ sơ Fresher tốt nghiệp xuất sắc...', '{"version": 1, "source": "parser", "stats": {"pages": 1, "words": 51, "characters": 281}, "contact": {"emails": ["candidate.fresher1@gmail.com"], "phones": ["0910000009"], "links": []}, "skills": ["Java", "Spring Boot"]}'::jsonb, now() - interval '25 days 0 hours', now() - interval '25 days 0 hours', now() - interval '25 days 0 hours', NULL),
  ('44444444444444444444444444444419'::uuid, '33333333333333333333333333333319'::uuid, 'CV Lâm Khánh Linh - Fresher Vue', 'seed/seed_cv_10.pdf', 'CV_LamKhanhLinh_Vue.pdf', 'application/pdf', 1302, 'd695740a481ab86143b4fc453de35b91926618da9f7f129fbd70d5e89b97c17a', 'vi', TRUE, 'completed', '', 'Lâm Khánh Linh
Fresher Frontend Developer | VueJS & Nuxt
candidate.fresher2@gmail.com | 0910000010

GIỚI THIỆU
Nắm vững kiến thức HTML/CSS/JavaScript hiện đại, ham học hỏi và tư duy thiết kế giao diện tốt.

KỸ NĂNG
VueJS, JavaScript

KINH NGHIỆM
Hồ sơ Fresher Frontend VueJS...', '{"version": 1, "source": "parser", "stats": {"pages": 1, "words": 44, "characters": 277}, "contact": {"emails": ["candidate.fresher2@gmail.com"], "phones": ["0910000010"], "links": []}, "skills": ["VueJS", "JavaScript"]}'::jsonb, now() - interval '25 days 0 hours', now() - interval '25 days 0 hours', now() - interval '25 days 0 hours', NULL),
  ('44444444444444444444444444444420'::uuid, '33333333333333333333333333333320'::uuid, 'CV Hà Quang Sáng - Python Intern', 'seed/seed_cv_11.pdf', 'CV_HaQuangSang_Intern.pdf', 'application/pdf', 1283, '24c173f1c44d20b4df200bc4cf54945b57e12244154e4699a386ed4c2a7366e7', 'vi', TRUE, 'completed', '', 'Hà Quang Sáng
Intern Python Developer
candidate.intern1@gmail.com | 0910000011

GIỚI THIỆU
Sinh viên năm cuối tìm kiếm cơ hội thực tập phát triển web và xử lý dữ liệu với Python.

KỸ NĂNG
Python

KINH NGHIỆM
Sinh viên năm cuối ứng tuyển thực tập...', '{"version": 1, "source": "parser", "stats": {"pages": 1, "words": 44, "characters": 248}, "contact": {"emails": ["candidate.intern1@gmail.com"], "phones": ["0910000011"], "links": []}, "skills": ["Python"]}'::jsonb, now() - interval '25 days 0 hours', now() - interval '25 days 0 hours', now() - interval '25 days 0 hours', NULL),
  ('44444444444444444444444444444421'::uuid, '33333333333333333333333333333321'::uuid, 'CV Chu Ngọc Mai - UI Design Intern', 'seed/seed_cv_12.pdf', 'CV_ChuNgocMai_Intern.pdf', 'application/pdf', 1265, 'd3574091f6331e798e40d0aa8e2e02e338c5b819fd6b5cbdaea3ec773c2c2421', 'vi', TRUE, 'completed', '', 'Chu Ngọc Mai
Intern UI/UX Designer
candidate.intern2@gmail.com | 0910000012

GIỚI THIỆU
Yêu thích thiết kế trải nghiệm người dùng, thành thạo công cụ Figma và vẽ vector.

KỸ NĂNG
Figma

KINH NGHIỆM
Portfolio thiết kế giao diện Figma...', '{"version": 1, "source": "parser", "stats": {"pages": 1, "words": 38, "characters": 235}, "contact": {"emails": ["candidate.intern2@gmail.com"], "phones": ["0910000012"], "links": []}, "skills": ["Figma"]}'::jsonb, now() - interval '25 days 0 hours', now() - interval '25 days 0 hours', now() - interval '25 days 0 hours', NULL),
  ('44444444444444444444444444444422'::uuid, '33333333333333333333333333333322'::uuid, 'CV Đoàn Nhật Quang - Tech Manager', 'seed/seed_cv_13.pdf', 'CV_DoanNhatQuang_Manager.pdf', 'application/pdf', 1403, 'ca86a1ade48751c2e4fd99b4ba8cb1323ee4b82fa284fa610b4d87536446781b', 'en', TRUE, 'completed', '', 'Đoàn Nhật Quang
Engineering Manager | 10+ năm kinh nghiệm quản lý
candidate.manager@gmail.com | 0910000013

GIỚI THIỆU
Kinh nghiệm dẫn dắt đội ngũ kỹ thuật 40+ kỹ sư, triển khai quy trình Agile/Scrum và chuyển đổi số.

KỸ NĂNG
Engineering Management, Agile, Architecture

KINH NGHIỆM
Executive Profile with 10 years experience...', '{"version": 1, "source": "parser", "stats": {"pages": 1, "words": 51, "characters": 329}, "contact": {"emails": ["candidate.manager@gmail.com"], "phones": ["0910000013"], "links": []}, "skills": ["Engineering Management", "Agile", "Architecture"]}'::jsonb, now() - interval '25 days 0 hours', now() - interval '25 days 0 hours', now() - interval '25 days 0 hours', NULL),
  ('44444444444444444444444444444423'::uuid, '33333333333333333333333333333323'::uuid, 'CV Ngô Kiến Huy - Chief Technology Officer', 'seed/seed_cv_14.pdf', 'CV_NgoKienHuy_CTO.pdf', 'application/pdf', 1355, 'fcd94108951454cef18eaa612e8d31410ca41626347188b7b50e5d7ebabcc17e', 'en', TRUE, 'completed', '', 'Ngô Kiến Huy
Chief Technology Officer (CTO) | Định hướng công nghệ
candidate.director@gmail.com | 0910000014

GIỚI THIỆU
Từng giữ vai trò CTO tại các startup kỳ lân công nghệ, quản trị kiến trúc tổng thể và ngân sách R&D.

KỸ NĂNG
Strategic Leadership, Scale-up

KINH NGHIỆM
CTO Profile with successful track record...', '{"version": 1, "source": "parser", "stats": {"pages": 1, "words": 52, "characters": 318}, "contact": {"emails": ["candidate.director@gmail.com"], "phones": ["0910000014"], "links": []}, "skills": ["Strategic Leadership", "Scale-up"]}'::jsonb, now() - interval '25 days 0 hours', now() - interval '25 days 0 hours', now() - interval '25 days 0 hours', NULL),
  ('44444444444444444444444444444424'::uuid, '33333333333333333333333333333324'::uuid, 'CV Lý Tuấn Kiệt - Cybersecurity', 'seed/seed_cv_15.pdf', 'CV_LyTuanKiet_Security.pdf', 'application/pdf', 1309, '27fdb35bdc777b82d73115a6fea6e0ec61ed33afaf4aa77a013c6cb58477b120', 'vi', TRUE, 'completed', '', 'Lý Tuấn Kiệt
Cybersecurity Specialist | SOC & Pentest
candidate.security@gmail.com | 0910000015

GIỚI THIỆU
Chứng chỉ CEH, OSCP, chuyên đánh giá an ninh mạng và rà soát lỗ hổng hệ thống.

KỸ NĂNG
Security, Linux, SOC

KINH NGHIỆM
Chuyên môn Pentest và An toàn thông tin...', '{"version": 1, "source": "parser", "stats": {"pages": 1, "words": 46, "characters": 272}, "contact": {"emails": ["candidate.security@gmail.com"], "phones": ["0910000015"], "links": []}, "skills": ["Security", "Linux", "SOC"]}'::jsonb, now() - interval '25 days 0 hours', now() - interval '25 days 0 hours', now() - interval '25 days 0 hours', NULL),
  ('44444444444444444444444444444425'::uuid, '33333333333333333333333333333325'::uuid, 'CV Tống Ánh Tuyết - QA Automation', 'seed/seed_cv_16.pdf', 'CV_TongAnhTuyet_QA.pdf', 'application/pdf', 1337, '2697a6c323df0813f432022d19893a627bb3606548fe9b793aa605bcaff6231c', 'vi', TRUE, 'completed', '', 'Tống Ánh Tuyết
QA/QC Automation Lead | Cypress & Selenium
candidate.qa@gmail.com | 0910000016

GIỚI THIỆU
Xây dựng khung kiểm thử tự động, tích hợp CI/CD để đảm bảo chất lượng phát hành liên tục.

KỸ NĂNG
QA Automation, Python, CI/CD

KINH NGHIỆM
Chuyên gia kiểm thử tự động Cypress & Selenium...', '{"version": 1, "source": "parser", "stats": {"pages": 1, "words": 51, "characters": 296}, "contact": {"emails": ["candidate.qa@gmail.com"], "phones": ["0910000016"], "links": []}, "skills": ["QA Automation", "Python", "CI/CD"]}'::jsonb, now() - interval '25 days 0 hours', now() - interval '25 days 0 hours', now() - interval '25 days 0 hours', NULL);


-- ====================================================================================================
-- 5. TIN TUYỂN DỤNG
-- ====================================================================================================

-- jobs (16 dòng)
INSERT INTO "jobs" ("id", "company_id", "created_by_id", "title", "slug", "description", "requirements", "benefits", "job_type", "work_mode", "level", "min_years_experience", "salary_min", "salary_max", "salary_currency", "is_salary_negotiable", "headcount", "location_id", "address", "industry_id", "deadline", "status", "published_at", "closed_at", "view_count", "application_count", "created_at", "updated_at", "deleted_at") VALUES
  ('55555555555555555555555555555501'::uuid, '11111111111111111111111111111101'::uuid, '00000000000000000000000000000002'::uuid, 'Senior Python Backend Engineer', 'senior-python-backend-engineer', 'Phát triển kiến trúc backend microservices cho nền tảng điện toán đám mây.', 'Tối thiểu 3 năm kinh nghiệm Python, Django, PostgreSQL, Docker.', 'Lương thưởng cạnh tranh, BHXH đầy đủ, chế độ làm việc hybrid.', 'full_time', 'hybrid', 'staff', 3.0, 25000000, 40000000, 'VND', FALSE, 2, (SELECT id FROM locations WHERE slug = 'ha-noi'), 'Tầng 5, Tòa nhà A, Cầu Giấy, Hà Nội', (SELECT id FROM industries WHERE slug = 'cong-nghe-thong-tin'), '2026-12-31'::date, 'published', now() - interval '1 days 0 hours', NULL, 340, 0, now() - interval '1 days 2 hours', now() - interval '1 days 0 hours', NULL),
  ('55555555555555555555555555555502'::uuid, '11111111111111111111111111111102'::uuid, '00000000000000000000000000000003'::uuid, 'Lead Java Architect (Fintech)', 'lead-java-architect-fintech', 'Chịu trách nhiệm kiến trúc hệ thống thanh toán cốt lõi xử lý triệu giao dịch/ngày.', 'Tối thiểu 6 năm kinh nghiệm Java/Spring Boot, Kafka, kiến trúc ngân hàng.', 'Gói phúc lợi cao cấp, thưởng KPI quý, hỗ trợ thiết bị làm việc.', 'full_time', 'onsite', 'supervisor', 6.0, 50000000, 80000000, 'VND', FALSE, 1, (SELECT id FROM locations WHERE slug = 'ho-chi-minh'), 'Tầng 12, Tòa nhà Bitexco, Quận 1, TP.HCM', (SELECT id FROM industries WHERE slug = 'tai-chinh-ngan-hang'), '2026-12-31'::date, 'published', now() - interval '2 days 0 hours', NULL, 410, 0, now() - interval '2 days 2 hours', now() - interval '2 days 0 hours', NULL),
  ('55555555555555555555555555555503'::uuid, '11111111111111111111111111111103'::uuid, '00000000000000000000000000000004'::uuid, 'Senior AI / Machine Learning Engineer', 'senior-ai-machine-learning-engineer', 'Xây dựng và tối ưu mô hình học sâu (Deep Learning) phục vụ giải pháp nhận dạng thông minh.', 'Thành thạo Python, PyTorch/TensorFlow, kinh nghiệm triển khai production model.', 'Môi trường R&D chuyên nghiệp, tài trợ tham gia các hội nghị khoa học quốc tế.', 'full_time', 'hybrid', 'staff', 3.0, 35000000, 55000000, 'VND', FALSE, 2, (SELECT id FROM locations WHERE slug = 'ha-noi'), 'Tầng 8, Tòa Keangnam, Nam Từ Liêm, Hà Nội', (SELECT id FROM industries WHERE slug = 'cong-nghe-thong-tin'), '2026-12-31'::date, 'published', now() - interval '3 days 0 hours', NULL, 290, 0, now() - interval '3 days 2 hours', now() - interval '3 days 0 hours', NULL),
  ('55555555555555555555555555555504'::uuid, '11111111111111111111111111111104'::uuid, '00000000000000000000000000000005'::uuid, 'Frontend React Developer (E-Commerce)', 'frontend-react-developer-ecom', 'Xây dựng giao diện sàn thương mại điện tử mượt mà trên desktop và mobile web.', 'Thành thạo ReactJS, TypeScript, Next.js, tư duy tối ưu hiệu năng web Core Web Vitals.', 'Thưởng doanh số cuối năm, giảm giá nội bộ khi mua sắm trên sàn.', 'full_time', 'remote', 'staff', 2.0, 20000000, 32000000, 'VND', FALSE, 3, (SELECT id FROM locations WHERE slug = 'ho-chi-minh'), 'Tầng 3, Tòa nhà D, Quận 3, TP.HCM', (SELECT id FROM industries WHERE slug = 'thuong-mai-dien-tu'), '2026-12-31'::date, 'published', now() - interval '4 days 0 hours', NULL, 520, 0, now() - interval '4 days 2 hours', now() - interval '4 days 0 hours', NULL),
  ('55555555555555555555555555555505'::uuid, '11111111111111111111111111111105'::uuid, '00000000000000000000000000000006'::uuid, 'Cloud DevOps & SRE Engineer', 'cloud-devops-sre-engineer', 'Xây dựng hạ tầng Cloud tự động hóa và duy trì độ sẵn sàng 99.99% cho khách hàng.', 'Kinh nghiệm sâu với Kubernetes, Terraform, AWS và giám sát hệ thống bằng Prometheus/Grafana.', 'Thưởng chứng chỉ công nghệ AWS/CKA, làm việc từ xa 100%.', 'full_time', 'remote', 'staff', 3.0, 28000000, 48000000, 'VND', FALSE, 2, (SELECT id FROM locations WHERE slug = 'da-nang'), 'Công viên Phần mềm Đà Nẵng, Hải Châu, Đà Nẵng', (SELECT id FROM industries WHERE slug = 'cong-nghe-thong-tin'), '2026-12-31'::date, 'published', now() - interval '5 days 0 hours', NULL, 215, 0, now() - interval '5 days 2 hours', now() - interval '5 days 0 hours', NULL),
  ('55555555555555555555555555555506'::uuid, '11111111111111111111111111111106'::uuid, '00000000000000000000000000000007'::uuid, 'Chuyên viên An toàn Thông tin (Pentester)', 'chuyen-vien-an-toan-thong-tin-pentest', 'Thực hiện kiểm thử xâm nhập (Penetration Testing) ứng dụng web và hệ thống máy chủ.', 'Kinh nghiệm đánh giá lỗ hổng bảo mật, sử dụng thành thạo Burp Suite, Nmap, Metasploit.', 'Phụ cấp dự án pentest đặc thù, đào tạo các chứng chỉ bảo mật cao cấp.', 'full_time', 'onsite', 'staff', 2.0, 22000000, 38000000, 'VND', FALSE, 2, (SELECT id FROM locations WHERE slug = 'ha-noi'), 'Tòa CMC Tower, Cầu Giấy, Hà Nội', (SELECT id FROM industries WHERE slug = 'cong-nghe-thong-tin'), '2026-12-31'::date, 'published', now() - interval '6 days 0 hours', NULL, 160, 0, now() - interval '6 days 2 hours', now() - interval '6 days 0 hours', NULL),
  ('55555555555555555555555555555507'::uuid, '11111111111111111111111111111107'::uuid, '00000000000000000000000000000008'::uuid, 'Golang Backend Developer (Logistics Platform)', 'golang-backend-developer-logistics', 'Phát triển backend định tuyến vận chuyển tức thì cho hệ thống điều phối thông minh.', 'Tối thiểu 2 năm Go/Golang, hiểu biết về Message Queue (Kafka/RabbitMQ) và gRPC.', 'Môi trường làm việc trẻ trung, du lịch hàng năm, phụ cấp cơm trưa.', 'full_time', 'hybrid', 'staff', 2.0, 22000000, 36000000, 'VND', FALSE, 2, (SELECT id FROM locations WHERE slug = 'ho-chi-minh'), 'Khu Công nghệ cao Quận 9, TP. Thủ Đức, TP.HCM', (SELECT id FROM industries WHERE slug = 'logistics-van-tai'), '2026-12-31'::date, 'published', now() - interval '7 days 0 hours', NULL, 185, 0, now() - interval '7 days 2 hours', now() - interval '7 days 0 hours', NULL),
  ('55555555555555555555555555555508'::uuid, '11111111111111111111111111111108'::uuid, '00000000000000000000000000000009'::uuid, 'Senior UI/UX Product Designer', 'senior-ui-ux-product-designer', 'Chịu trách nhiệm thiết kế trải nghiệm người dùng cho ứng dụng học tập trực tuyến EdTech.', 'Thành thạo Figma, xây dựng Design System, kinh nghiệm phỏng vấn người dùng.', 'Môi trường giáo dục nhân văn, thời gian làm việc linh hoạt, thưởng hiệu quả.', 'full_time', 'hybrid', 'staff', 3.0, 20000000, 35000000, 'VND', FALSE, 1, (SELECT id FROM locations WHERE slug = 'ha-noi'), 'Tầng 4, Tòa Hapulico, Thanh Xuân, Hà Nội', (SELECT id FROM industries WHERE slug = 'giao-duc-dao-tao'), '2026-12-31'::date, 'published', now() - interval '8 days 0 hours', NULL, 230, 0, now() - interval '8 days 2 hours', now() - interval '8 days 0 hours', NULL),
  ('55555555555555555555555555555509'::uuid, '11111111111111111111111111111101'::uuid, '00000000000000000000000000000002'::uuid, 'Fresher Java Backend Developer', 'fresher-java-backend-developer', 'Tham gia dự án đào tạo và làm việc thực tế với Java Spring Boot cho thị trường nước ngoài.', 'Nắm chắc kiến thức OOP, SQL, Java Core. Ưu tiên có điểm GPA khá/giỏi.', 'Được mentor kèm 1:1, lộ trình thăng tiến rõ ràng lên Junior sau 6 tháng.', 'full_time', 'onsite', 'fresher', 0.0, 8000000, 13000000, 'VND', FALSE, 5, (SELECT id FROM locations WHERE slug = 'ha-noi'), 'Tầng 5, Tòa nhà A, Cầu Giấy, Hà Nội', (SELECT id FROM industries WHERE slug = 'cong-nghe-thong-tin'), '2026-12-31'::date, 'published', now() - interval '9 days 0 hours', NULL, 450, 0, now() - interval '9 days 2 hours', now() - interval '9 days 0 hours', NULL),
  ('55555555555555555555555555555510'::uuid, '11111111111111111111111111111104'::uuid, '00000000000000000000000000000005'::uuid, 'Fresher Frontend Developer (VueJS)', 'fresher-frontend-developer-vue', 'Phát triển các module giao diện quản trị Admin portal phục vụ người bán hàng.', 'Hiểu biết căn bản về VueJS, HTML5, CSS3, JavaScript ES6.', 'Trợ cấp ăn trưa, đào tạo bài bản từ các Senior Frontend Kỹ sư.', 'full_time', 'hybrid', 'fresher', 0.0, 9000000, 14000000, 'VND', FALSE, 4, (SELECT id FROM locations WHERE slug = 'ho-chi-minh'), 'Tầng 3, Tòa nhà D, Quận 3, TP.HCM', (SELECT id FROM industries WHERE slug = 'thuong-mai-dien-tu'), '2026-12-31'::date, 'published', now() - interval '10 days 0 hours', NULL, 310, 0, now() - interval '10 days 2 hours', now() - interval '10 days 0 hours', NULL),
  ('55555555555555555555555555555511'::uuid, '11111111111111111111111111111103'::uuid, '00000000000000000000000000000004'::uuid, 'Thực tập sinh Python / AI Intern', 'thuc-tap-sinh-python-ai-intern', 'Hỗ trợ thu thập, gán nhãn dữ liệu và thử nghiệm các mô hình AI mã nguồn mở.', 'Sinh viên năm 3, 4 chuyên ngành CNTT, Toán - Tin, biết lập trình Python cơ bản.', 'Hỗ trợ dấu thực tập tốt nghiệp, phụ cấp thực tập cạnh tranh, cơ hội lên chính thức.', 'internship', 'onsite', 'intern', 0.0, 3500000, 6000000, 'VND', FALSE, 4, (SELECT id FROM locations WHERE slug = 'ha-noi'), 'Tầng 8, Tòa Keangnam, Nam Từ Liêm, Hà Nội', (SELECT id FROM industries WHERE slug = 'cong-nghe-thong-tin'), '2026-12-31'::date, 'published', now() - interval '11 days 0 hours', NULL, 380, 0, now() - interval '11 days 2 hours', now() - interval '11 days 0 hours', NULL),
  ('55555555555555555555555555555512'::uuid, '11111111111111111111111111111108'::uuid, '00000000000000000000000000000009'::uuid, 'Thực tập sinh Thiết kế UI/UX', 'thuc-tap-sinh-thiet-ke-ui-ux', 'Hỗ trợ đội ngũ Product tạo wireframe, icon và chuẩn bị hình ảnh minh họa cho app.', 'Có sản phẩm thiết kế mẫu cá nhân bằng Figma, tư duy thẩm mỹ hiện đại.', 'Được hướng dẫn bởi Lead Designer, nhận trợ cấp thực tập hàng tháng.', 'internship', 'hybrid', 'intern', 0.0, 3000000, 5000000, 'VND', FALSE, 2, (SELECT id FROM locations WHERE slug = 'ha-noi'), 'Tầng 4, Tòa Hapulico, Thanh Xuân, Hà Nội', (SELECT id FROM industries WHERE slug = 'giao-duc-dao-tao'), '2026-12-31'::date, 'published', now() - interval '12 days 0 hours', NULL, 210, 0, now() - interval '12 days 2 hours', now() - interval '12 days 0 hours', NULL),
  ('55555555555555555555555555555513'::uuid, '11111111111111111111111111111102'::uuid, '00000000000000000000000000000003'::uuid, 'Engineering Manager (Head of Core Banking)', 'engineering-manager-head-of-core', 'Quản lý 3 đội kỹ thuật (Backend, Frontend, DevOps) phát triển hệ thống lõi ngân hàng.', '10+ năm kinh nghiệm kỹ thuật, ít nhất 3 năm ở vị trí Manager, khả năng lãnh đạo xuất sắc.', 'Lương cạnh tranh top thị trường, thưởng cổ phiếu ESOP, gói bảo hiểm toàn diện cho gia đình.', 'full_time', 'hybrid', 'manager', 8.0, 70000000, 110000000, 'VND', FALSE, 1, (SELECT id FROM locations WHERE slug = 'ho-chi-minh'), 'Tầng 12, Tòa nhà Bitexco, Quận 1, TP.HCM', (SELECT id FROM industries WHERE slug = 'tai-chinh-ngan-hang'), '2026-12-31'::date, 'published', now() - interval '13 days 0 hours', NULL, 280, 0, now() - interval '13 days 2 hours', now() - interval '13 days 0 hours', NULL),
  ('55555555555555555555555555555514'::uuid, '11111111111111111111111111111105'::uuid, '00000000000000000000000000000006'::uuid, 'Giám đốc Công nghệ (CTO)', 'giam-doc-cong-nghe-cto-cloudscale', 'Định hướng toàn bộ lộ trình phát triển hạ tầng mạng viễn thông đám mây của doanh nghiệp.', 'Từng giữ vị trí Tech Director/CTO tại các công ty công nghệ lớn, có tầm nhìn chiến lược sâu rộng.', 'Thu nhập thỏa thuận xứng tầm, cổ phần sở hữu tại công ty.', 'full_time', 'hybrid', 'director', 12.0, 110000000, 180000000, 'VND', TRUE, 1, (SELECT id FROM locations WHERE slug = 'da-nang'), 'Công viên Phần mềm Đà Nẵng, Hải Châu, Đà Nẵng', (SELECT id FROM industries WHERE slug = 'cong-nghe-thong-tin'), '2026-12-31'::date, 'published', now() - interval '14 days 0 hours', NULL, 390, 0, now() - interval '14 days 2 hours', now() - interval '14 days 0 hours', NULL),
  ('55555555555555555555555555555515'::uuid, '11111111111111111111111111111107'::uuid, '00000000000000000000000000000008'::uuid, 'Senior QA Automation Engineer', 'senior-qa-automation-engineer', 'Xây dựng framework kiểm thử tự động cho hệ thống tracking xe tải và kho bãi.', 'Tối thiểu 3 năm kinh nghiệm Automation Test (Selenium/Cypress), lập trình Python hoặc Java.', 'Thưởng dự án định kỳ, môi trường ổn định, cơ hội học hỏi hệ thống IoT.', 'full_time', 'hybrid', 'staff', 3.0, 20000000, 32000000, 'VND', FALSE, 2, (SELECT id FROM locations WHERE slug = 'ho-chi-minh'), 'Khu Công nghệ cao Quận 9, TP. Thủ Đức, TP.HCM', (SELECT id FROM industries WHERE slug = 'logistics-van-tai'), '2026-12-31'::date, 'published', now() - interval '15 days 0 hours', NULL, 145, 0, now() - interval '15 days 2 hours', now() - interval '15 days 0 hours', NULL),
  ('55555555555555555555555555555516'::uuid, '11111111111111111111111111111104'::uuid, '00000000000000000000000000000005'::uuid, 'Fullstack Web Engineer (NodeJS + React)', 'fullstack-web-engineer-ecom', 'Tham gia phát triển hệ thống live-streaming bán hàng trực tiếp trên sàn.', 'Kinh nghiệm với NodeJS, WebSocket, ReactJS và kiến trúc chịu tải phân tán.', 'Thưởng doanh thu stream, môi trường trẻ trung, cởi mở.', 'full_time', 'hybrid', 'staff', 2.5, 22000000, 35000000, 'VND', FALSE, 2, (SELECT id FROM locations WHERE slug = 'ho-chi-minh'), 'Tầng 3, Tòa nhà D, Quận 3, TP.HCM', (SELECT id FROM industries WHERE slug = 'thuong-mai-dien-tu'), '2026-12-31'::date, 'published', now() - interval '16 days 0 hours', NULL, 270, 0, now() - interval '16 days 2 hours', now() - interval '16 days 0 hours', NULL);

-- job_skills (32 dòng)
INSERT INTO "job_skills" ("job_id", "skill_id", "is_required", "min_years", "weight") VALUES
  ('55555555555555555555555555555501'::uuid, (SELECT id FROM skills WHERE slug = 'python'), TRUE, 3.0, 5),
  ('55555555555555555555555555555501'::uuid, (SELECT id FROM skills WHERE slug = 'postgresql'), TRUE, 2.0, 4),
  ('55555555555555555555555555555501'::uuid, (SELECT id FROM skills WHERE slug = 'docker'), FALSE, 1.0, 3),
  ('55555555555555555555555555555502'::uuid, (SELECT id FROM skills WHERE slug = 'java'), TRUE, 6.0, 5),
  ('55555555555555555555555555555502'::uuid, (SELECT id FROM skills WHERE slug = 'spring-boot'), TRUE, 5.0, 5),
  ('55555555555555555555555555555502'::uuid, (SELECT id FROM skills WHERE slug = 'postgresql'), TRUE, 4.0, 4),
  ('55555555555555555555555555555503'::uuid, (SELECT id FROM skills WHERE slug = 'python'), TRUE, 3.0, 5),
  ('55555555555555555555555555555503'::uuid, (SELECT id FROM skills WHERE slug = 'pytorch'), TRUE, 2.0, 5),
  ('55555555555555555555555555555503'::uuid, (SELECT id FROM skills WHERE slug = 'tensorflow'), FALSE, 2.0, 3),
  ('55555555555555555555555555555504'::uuid, (SELECT id FROM skills WHERE slug = 'react'), TRUE, 2.0, 5),
  ('55555555555555555555555555555504'::uuid, (SELECT id FROM skills WHERE slug = 'typescript'), TRUE, 2.0, 4),
  ('55555555555555555555555555555504'::uuid, (SELECT id FROM skills WHERE slug = 'next-dot-js'), FALSE, 1.0, 3),
  ('55555555555555555555555555555505'::uuid, (SELECT id FROM skills WHERE slug = 'docker'), TRUE, 3.0, 5),
  ('55555555555555555555555555555505'::uuid, (SELECT id FROM skills WHERE slug = 'kubernetes'), TRUE, 3.0, 5),
  ('55555555555555555555555555555505'::uuid, (SELECT id FROM skills WHERE slug = 'aws'), TRUE, 2.0, 4),
  ('55555555555555555555555555555506'::uuid, (SELECT id FROM skills WHERE slug = 'linux'), TRUE, 2.0, 5),
  ('55555555555555555555555555555506'::uuid, (SELECT id FROM skills WHERE slug = 'spring-boot'), FALSE, 1.0, 3),
  ('55555555555555555555555555555507'::uuid, (SELECT id FROM skills WHERE slug = 'go'), TRUE, 2.0, 5),
  ('55555555555555555555555555555507'::uuid, (SELECT id FROM skills WHERE slug = 'redis'), TRUE, 2.0, 4),
  ('55555555555555555555555555555508'::uuid, (SELECT id FROM skills WHERE slug = 'figma'), TRUE, 3.0, 5),
  ('55555555555555555555555555555509'::uuid, (SELECT id FROM skills WHERE slug = 'java'), TRUE, 0.0, 5),
  ('55555555555555555555555555555509'::uuid, (SELECT id FROM skills WHERE slug = 'spring-boot'), FALSE, 0.0, 3),
  ('55555555555555555555555555555510'::uuid, (SELECT id FROM skills WHERE slug = 'vue-dot-js'), TRUE, 0.0, 5),
  ('55555555555555555555555555555511'::uuid, (SELECT id FROM skills WHERE slug = 'python'), TRUE, 0.0, 5),
  ('55555555555555555555555555555512'::uuid, (SELECT id FROM skills WHERE slug = 'figma'), TRUE, 0.0, 5),
  ('55555555555555555555555555555513'::uuid, (SELECT id FROM skills WHERE slug = 'giao-tiep'), TRUE, 8.0, 5),
  ('55555555555555555555555555555513'::uuid, (SELECT id FROM skills WHERE slug = 'lam-viec-nhom'), TRUE, 8.0, 5),
  ('55555555555555555555555555555514'::uuid, (SELECT id FROM skills WHERE slug = 'giai-quyet-van-de'), TRUE, 12.0, 5),
  ('55555555555555555555555555555515'::uuid, (SELECT id FROM skills WHERE slug = 'python'), TRUE, 2.0, 4),
  ('55555555555555555555555555555515'::uuid, (SELECT id FROM skills WHERE slug = 'cicd'), TRUE, 2.0, 4),
  ('55555555555555555555555555555516'::uuid, (SELECT id FROM skills WHERE slug = 'node-dot-js'), TRUE, 2.5, 5),
  ('55555555555555555555555555555516'::uuid, (SELECT id FROM skills WHERE slug = 'react'), TRUE, 2.0, 4);


-- ====================================================================================================
-- 6. YÊU THÍCH
-- ====================================================================================================

-- favorite_jobs (12 dòng)
INSERT INTO "favorite_jobs" ("candidate_id", "job_id", "created_at") VALUES
  ('33333333333333333333333333333310'::uuid, '55555555555555555555555555555501'::uuid, now() - interval '3 days 0 hours'),
  ('33333333333333333333333333333310'::uuid, '55555555555555555555555555555503'::uuid, now() - interval '3 days 0 hours'),
  ('33333333333333333333333333333311'::uuid, '55555555555555555555555555555504'::uuid, now() - interval '3 days 0 hours'),
  ('33333333333333333333333333333312'::uuid, '55555555555555555555555555555502'::uuid, now() - interval '3 days 0 hours'),
  ('33333333333333333333333333333313'::uuid, '55555555555555555555555555555505'::uuid, now() - interval '3 days 0 hours'),
  ('33333333333333333333333333333314'::uuid, '55555555555555555555555555555508'::uuid, now() - interval '3 days 0 hours'),
  ('33333333333333333333333333333315'::uuid, '55555555555555555555555555555503'::uuid, now() - interval '3 days 0 hours'),
  ('33333333333333333333333333333316'::uuid, '55555555555555555555555555555507'::uuid, now() - interval '3 days 0 hours'),
  ('33333333333333333333333333333317'::uuid, '55555555555555555555555555555516'::uuid, now() - interval '3 days 0 hours'),
  ('33333333333333333333333333333318'::uuid, '55555555555555555555555555555509'::uuid, now() - interval '3 days 0 hours'),
  ('33333333333333333333333333333322'::uuid, '55555555555555555555555555555513'::uuid, now() - interval '3 days 0 hours'),
  ('33333333333333333333333333333324'::uuid, '55555555555555555555555555555506'::uuid, now() - interval '3 days 0 hours');

-- favorite_companies (10 dòng)
INSERT INTO "favorite_companies" ("candidate_id", "company_id", "created_at") VALUES
  ('33333333333333333333333333333310'::uuid, '11111111111111111111111111111101'::uuid, now() - interval '3 days 0 hours'),
  ('33333333333333333333333333333310'::uuid, '11111111111111111111111111111103'::uuid, now() - interval '3 days 0 hours'),
  ('33333333333333333333333333333311'::uuid, '11111111111111111111111111111104'::uuid, now() - interval '3 days 0 hours'),
  ('33333333333333333333333333333312'::uuid, '11111111111111111111111111111102'::uuid, now() - interval '3 days 0 hours'),
  ('33333333333333333333333333333313'::uuid, '11111111111111111111111111111105'::uuid, now() - interval '3 days 0 hours'),
  ('33333333333333333333333333333314'::uuid, '11111111111111111111111111111108'::uuid, now() - interval '3 days 0 hours'),
  ('33333333333333333333333333333315'::uuid, '11111111111111111111111111111103'::uuid, now() - interval '3 days 0 hours'),
  ('33333333333333333333333333333316'::uuid, '11111111111111111111111111111107'::uuid, now() - interval '3 days 0 hours'),
  ('33333333333333333333333333333322'::uuid, '11111111111111111111111111111102'::uuid, now() - interval '3 days 0 hours'),
  ('33333333333333333333333333333323'::uuid, '11111111111111111111111111111105'::uuid, now() - interval '3 days 0 hours');


-- ====================================================================================================
-- 7. ỨNG TUYỂN
-- ====================================================================================================

-- applications (20 dòng)
INSERT INTO "applications" ("id", "job_id", "candidate_id", "cv_id", "cover_letter", "status", "rejection_reason", "recruiter_rating", "status_changed_at", "created_at", "updated_at") VALUES
  ('66666666666666666666666666666601'::uuid, '55555555555555555555555555555501'::uuid, '33333333333333333333333333333310'::uuid, '44444444444444444444444444444410'::uuid, 'Tôi mong muốn đóng góp kinh nghiệm Python và tối ưu dữ liệu cho hệ thống của công ty.', 'interview', '', 4, now() - interval '9 days 0 hours', now() - interval '13 days 0 hours', now() - interval '9 days 0 hours'),
  ('66666666666666666666666666666602'::uuid, '55555555555555555555555555555502'::uuid, '33333333333333333333333333333312'::uuid, '44444444444444444444444444444412'::uuid, 'Với 7 năm kinh nghiệm kiến trúc ngân hàng, tôi tự tin đáp ứng tốt các tiêu chuẩn khắt khe nhất.', 'offer', '', 5, now() - interval '8 days 0 hours', now() - interval '12 days 0 hours', now() - interval '8 days 0 hours'),
  ('66666666666666666666666666666603'::uuid, '55555555555555555555555555555503'::uuid, '33333333333333333333333333333315'::uuid, '44444444444444444444444444444415'::uuid, 'Tôi có các công bố nghiên cứu về nhận diện đối tượng và mong muốn ứng dụng tại AI Solutions.', 'screening', '', 4, now() - interval '9 days 0 hours', now() - interval '11 days 0 hours', now() - interval '9 days 0 hours'),
  ('66666666666666666666666666666604'::uuid, '55555555555555555555555555555504'::uuid, '33333333333333333333333333333311'::uuid, '44444444444444444444444444444411'::uuid, 'Tôi rất ấn tượng với tốc độ phát triển của E-Commerce Stars và mong muốn phụ trách mảng giao diện.', 'interview', '', 4, now() - interval '8 days 0 hours', now() - interval '10 days 0 hours', now() - interval '8 days 0 hours'),
  ('66666666666666666666666666666605'::uuid, '55555555555555555555555555555505'::uuid, '33333333333333333333333333333313'::uuid, '44444444444444444444444444444413'::uuid, 'Thế mạnh của tôi là tự động hóa hạ tầng và giải quyết nghẽn cổ chai Kubernetes.', 'hired', '', 5, now() - interval '3 days 0 hours', now() - interval '9 days 0 hours', now() - interval '3 days 0 hours'),
  ('66666666666666666666666666666606'::uuid, '55555555555555555555555555555506'::uuid, '33333333333333333333333333333324'::uuid, '44444444444444444444444444444424'::uuid, 'Tôi muốn gia nhập đội ngũ pentest chuyên nghiệp để bảo vệ hệ thống trước các mối đe dọa.', 'screening', '', 3, now() - interval '6 days 0 hours', now() - interval '8 days 0 hours', now() - interval '6 days 0 hours'),
  ('66666666666666666666666666666607'::uuid, '55555555555555555555555555555507'::uuid, '33333333333333333333333333333316'::uuid, '44444444444444444444444444444416'::uuid, 'Kinh nghiệm Golang và gRPC của tôi phù hợp hoàn toàn với định hướng của LogiSmart.', 'applied', '', NULL, now() - interval '7 days 0 hours', now() - interval '7 days 0 hours', now() - interval '7 days 0 hours'),
  ('66666666666666666666666666666608'::uuid, '55555555555555555555555555555508'::uuid, '33333333333333333333333333333314'::uuid, '44444444444444444444444444444414'::uuid, 'Tôi đam mê xây dựng giao diện ứng dụng học tập trực quan và truyền cảm hứng.', 'interview', '', 4, now() - interval '4 days 0 hours', now() - interval '6 days 0 hours', now() - interval '4 days 0 hours'),
  ('66666666666666666666666666666609'::uuid, '55555555555555555555555555555509'::uuid, '33333333333333333333333333333318'::uuid, '44444444444444444444444444444418'::uuid, 'Em là sinh viên mới ra trường và rất mong muốn được đào tạo tại TechCorp.', 'applied', '', 3, now() - interval '5 days 0 hours', now() - interval '5 days 0 hours', now() - interval '5 days 0 hours'),
  ('66666666666666666666666666666610'::uuid, '55555555555555555555555555555510'::uuid, '33333333333333333333333333333319'::uuid, '44444444444444444444444444444419'::uuid, 'Em yêu thích làm giao diện người dùng và muốn cống hiến cho mảng thương mại điện tử.', 'screening', '', 3, now() - interval '12 days 0 hours', now() - interval '14 days 0 hours', now() - interval '12 days 0 hours'),
  ('66666666666666666666666666666611'::uuid, '55555555555555555555555555555511'::uuid, '33333333333333333333333333333320'::uuid, '44444444444444444444444444444420'::uuid, 'Em nộp đơn xin thực tập vị trí AI Intern.', 'applied', '', NULL, now() - interval '13 days 0 hours', now() - interval '13 days 0 hours', now() - interval '13 days 0 hours'),
  ('66666666666666666666666666666612'::uuid, '55555555555555555555555555555512'::uuid, '33333333333333333333333333333321'::uuid, '44444444444444444444444444444421'::uuid, 'Em mong muốn được thực tập thiết kế UI/UX tại EdTech.', 'screening', '', 3, now() - interval '10 days 0 hours', now() - interval '12 days 0 hours', now() - interval '10 days 0 hours'),
  ('66666666666666666666666666666613'::uuid, '55555555555555555555555555555513'::uuid, '33333333333333333333333333333322'::uuid, '44444444444444444444444444444422'::uuid, 'Tôi mong muốn nhận trách nhiệm dẫn dắt khối kỹ thuật tại FinTech Global.', 'interview', '', 5, now() - interval '9 days 0 hours', now() - interval '11 days 0 hours', now() - interval '9 days 0 hours'),
  ('66666666666666666666666666666614'::uuid, '55555555555555555555555555555514'::uuid, '33333333333333333333333333333323'::uuid, '44444444444444444444444444444423'::uuid, 'Trao đổi chiến lược vị trí CTO cho CloudScale Networks.', 'screening', '', 5, now() - interval '8 days 0 hours', now() - interval '10 days 0 hours', now() - interval '8 days 0 hours'),
  ('66666666666666666666666666666615'::uuid, '55555555555555555555555555555515'::uuid, '33333333333333333333333333333325'::uuid, '44444444444444444444444444444425'::uuid, 'Tôi có 3.5 năm kinh nghiệm xây dựng hệ thống kiểm thử tự động toàn diện.', 'offer', '', 4, now() - interval '7 days 0 hours', now() - interval '9 days 0 hours', now() - interval '7 days 0 hours'),
  ('66666666666666666666666666666616'::uuid, '55555555555555555555555555555516'::uuid, '33333333333333333333333333333317'::uuid, '44444444444444444444444444444417'::uuid, 'Kỹ năng Node.js và React của tôi có thể đáp ứng tốt tính năng live streaming.', 'interview', '', 4, now() - interval '6 days 0 hours', now() - interval '8 days 0 hours', now() - interval '6 days 0 hours'),
  ('66666666666666666666666666666617'::uuid, '55555555555555555555555555555501'::uuid, '33333333333333333333333333333315'::uuid, '44444444444444444444444444444415'::uuid, 'Ứng tuyển mở rộng sang vị trí Backend Engineer.', 'rejected', 'Kinh nghiệm chưa phù hợp với yêu cầu của vị trí.', 2, now() - interval '5 days 0 hours', now() - interval '7 days 0 hours', now() - interval '5 days 0 hours'),
  ('66666666666666666666666666666618'::uuid, '55555555555555555555555555555504'::uuid, '33333333333333333333333333333317'::uuid, '44444444444444444444444444444417'::uuid, 'Ứng tuyển thử sức thêm vị trí Frontend.', 'withdrawn', '', NULL, now() - interval '4 days 0 hours', now() - interval '6 days 0 hours', now() - interval '4 days 0 hours'),
  ('66666666666666666666666666666619'::uuid, '55555555555555555555555555555505'::uuid, '33333333333333333333333333333310'::uuid, '44444444444444444444444444444410'::uuid, 'Tìm hiểu thêm về mảng DevOps.', 'rejected', 'Kinh nghiệm chưa phù hợp với yêu cầu của vị trí.', 2, now() - interval '3 days 0 hours', now() - interval '5 days 0 hours', now() - interval '3 days 0 hours'),
  ('66666666666666666666666666666620'::uuid, '55555555555555555555555555555503'::uuid, '33333333333333333333333333333310'::uuid, '44444444444444444444444444444410'::uuid, 'Ứng tuyển mảng Data Backend cho dự án AI.', 'screening', '', 3, now() - interval '12 days 0 hours', now() - interval '14 days 0 hours', now() - interval '12 days 0 hours');

-- application_status_history (41 dòng)
INSERT INTO "application_status_history" ("application_id", "from_status", "to_status", "changed_by_id", "note", "created_at") VALUES
  ('66666666666666666666666666666601'::uuid, NULL, 'applied', '00000000000000000000000000000010'::uuid, 'Ứng viên nộp hồ sơ', now() - interval '13 days 0 hours'),
  ('66666666666666666666666666666601'::uuid, 'applied', 'screening', '00000000000000000000000000000002'::uuid, 'Hồ sơ đạt yêu cầu cơ bản', now() - interval '11 days 0 hours'),
  ('66666666666666666666666666666601'::uuid, 'screening', 'interview', '00000000000000000000000000000002'::uuid, 'Gửi lời mời phỏng vấn kỹ thuật', now() - interval '9 days 0 hours'),
  ('66666666666666666666666666666602'::uuid, NULL, 'applied', '00000000000000000000000000000012'::uuid, 'Nộp hồ sơ trực tuyến', now() - interval '12 days 0 hours'),
  ('66666666666666666666666666666602'::uuid, 'applied', 'interview', '00000000000000000000000000000003'::uuid, 'Phỏng vấn trực tiếp với Giám đốc kỹ thuật', now() - interval '10 days 0 hours'),
  ('66666666666666666666666666666602'::uuid, 'interview', 'offer', '00000000000000000000000000000003'::uuid, 'Ứng viên xuất sắc, phát hành thư mời nhận việc', now() - interval '8 days 0 hours'),
  ('66666666666666666666666666666603'::uuid, NULL, 'applied', '00000000000000000000000000000015'::uuid, 'Ứng viên nộp hồ sơ', now() - interval '11 days 0 hours'),
  ('66666666666666666666666666666603'::uuid, 'applied', 'screening', '00000000000000000000000000000004'::uuid, 'Cập nhật trạng thái hồ sơ', now() - interval '9 days 0 hours'),
  ('66666666666666666666666666666604'::uuid, NULL, 'applied', '00000000000000000000000000000011'::uuid, 'Ứng viên nộp hồ sơ', now() - interval '10 days 0 hours'),
  ('66666666666666666666666666666604'::uuid, 'applied', 'interview', '00000000000000000000000000000005'::uuid, 'Cập nhật trạng thái hồ sơ', now() - interval '8 days 0 hours'),
  ('66666666666666666666666666666605'::uuid, NULL, 'applied', '00000000000000000000000000000013'::uuid, 'Nộp hồ sơ vị trí DevOps', now() - interval '9 days 0 hours'),
  ('66666666666666666666666666666605'::uuid, 'applied', 'interview', '00000000000000000000000000000006'::uuid, 'Phỏng vấn kiểm tra kiến thức hạ tầng', now() - interval '7 days 0 hours'),
  ('66666666666666666666666666666605'::uuid, 'interview', 'offer', '00000000000000000000000000000006'::uuid, 'Gửi offer thành công', now() - interval '5 days 0 hours'),
  ('66666666666666666666666666666605'::uuid, 'offer', 'hired', '00000000000000000000000000000006'::uuid, 'Ứng viên đồng ý nhận việc', now() - interval '3 days 0 hours'),
  ('66666666666666666666666666666606'::uuid, NULL, 'applied', '00000000000000000000000000000024'::uuid, 'Ứng viên nộp hồ sơ', now() - interval '8 days 0 hours'),
  ('66666666666666666666666666666606'::uuid, 'applied', 'screening', '00000000000000000000000000000007'::uuid, 'Cập nhật trạng thái hồ sơ', now() - interval '6 days 0 hours'),
  ('66666666666666666666666666666607'::uuid, NULL, 'applied', '00000000000000000000000000000016'::uuid, 'Ứng viên nộp hồ sơ', now() - interval '7 days 0 hours'),
  ('66666666666666666666666666666608'::uuid, NULL, 'applied', '00000000000000000000000000000014'::uuid, 'Ứng viên nộp hồ sơ', now() - interval '6 days 0 hours'),
  ('66666666666666666666666666666608'::uuid, 'applied', 'interview', '00000000000000000000000000000009'::uuid, 'Cập nhật trạng thái hồ sơ', now() - interval '4 days 0 hours'),
  ('66666666666666666666666666666609'::uuid, NULL, 'applied', '00000000000000000000000000000018'::uuid, 'Ứng viên nộp hồ sơ', now() - interval '5 days 0 hours'),
  ('66666666666666666666666666666610'::uuid, NULL, 'applied', '00000000000000000000000000000019'::uuid, 'Ứng viên nộp hồ sơ', now() - interval '14 days 0 hours'),
  ('66666666666666666666666666666610'::uuid, 'applied', 'screening', '00000000000000000000000000000005'::uuid, 'Cập nhật trạng thái hồ sơ', now() - interval '12 days 0 hours'),
  ('66666666666666666666666666666611'::uuid, NULL, 'applied', '00000000000000000000000000000020'::uuid, 'Ứng viên nộp hồ sơ', now() - interval '13 days 0 hours'),
  ('66666666666666666666666666666612'::uuid, NULL, 'applied', '00000000000000000000000000000021'::uuid, 'Ứng viên nộp hồ sơ', now() - interval '12 days 0 hours'),
  ('66666666666666666666666666666612'::uuid, 'applied', 'screening', '00000000000000000000000000000009'::uuid, 'Cập nhật trạng thái hồ sơ', now() - interval '10 days 0 hours'),
  ('66666666666666666666666666666613'::uuid, NULL, 'applied', '00000000000000000000000000000022'::uuid, 'Ứng viên nộp hồ sơ', now() - interval '11 days 0 hours'),
  ('66666666666666666666666666666613'::uuid, 'applied', 'interview', '00000000000000000000000000000003'::uuid, 'Cập nhật trạng thái hồ sơ', now() - interval '9 days 0 hours'),
  ('66666666666666666666666666666614'::uuid, NULL, 'applied', '00000000000000000000000000000023'::uuid, 'Ứng viên nộp hồ sơ', now() - interval '10 days 0 hours'),
  ('66666666666666666666666666666614'::uuid, 'applied', 'screening', '00000000000000000000000000000006'::uuid, 'Cập nhật trạng thái hồ sơ', now() - interval '8 days 0 hours'),
  ('66666666666666666666666666666615'::uuid, NULL, 'applied', '00000000000000000000000000000025'::uuid, 'Ứng viên nộp hồ sơ', now() - interval '9 days 0 hours'),
  ('66666666666666666666666666666615'::uuid, 'applied', 'offer', '00000000000000000000000000000008'::uuid, 'Cập nhật trạng thái hồ sơ', now() - interval '7 days 0 hours'),
  ('66666666666666666666666666666616'::uuid, NULL, 'applied', '00000000000000000000000000000017'::uuid, 'Ứng viên nộp hồ sơ', now() - interval '8 days 0 hours'),
  ('66666666666666666666666666666616'::uuid, 'applied', 'interview', '00000000000000000000000000000005'::uuid, 'Cập nhật trạng thái hồ sơ', now() - interval '6 days 0 hours'),
  ('66666666666666666666666666666617'::uuid, NULL, 'applied', '00000000000000000000000000000015'::uuid, 'Ứng viên nộp hồ sơ', now() - interval '7 days 0 hours'),
  ('66666666666666666666666666666617'::uuid, 'applied', 'rejected', '00000000000000000000000000000002'::uuid, '', now() - interval '5 days 0 hours'),
  ('66666666666666666666666666666618'::uuid, NULL, 'applied', '00000000000000000000000000000017'::uuid, 'Ứng viên nộp hồ sơ', now() - interval '6 days 0 hours'),
  ('66666666666666666666666666666618'::uuid, 'applied', 'withdrawn', '00000000000000000000000000000017'::uuid, 'Ứng viên rút hồ sơ', now() - interval '4 days 0 hours'),
  ('66666666666666666666666666666619'::uuid, NULL, 'applied', '00000000000000000000000000000010'::uuid, 'Ứng viên nộp hồ sơ', now() - interval '5 days 0 hours'),
  ('66666666666666666666666666666619'::uuid, 'applied', 'rejected', '00000000000000000000000000000006'::uuid, '', now() - interval '3 days 0 hours'),
  ('66666666666666666666666666666620'::uuid, NULL, 'applied', '00000000000000000000000000000010'::uuid, 'Ứng viên nộp hồ sơ', now() - interval '14 days 0 hours'),
  ('66666666666666666666666666666620'::uuid, 'applied', 'screening', '00000000000000000000000000000004'::uuid, 'Cập nhật trạng thái hồ sơ', now() - interval '12 days 0 hours');

-- Số hồ sơ của mỗi tin (cột đếm sẵn)
UPDATE "jobs" SET "application_count" = (SELECT COUNT(*) FROM "applications" a WHERE a."job_id" = "jobs"."id");

COMMIT;
