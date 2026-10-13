-- =====================================================================
-- SEED DATA FOR RECRUITMENT ATS DATABASE (EXPANDED DATASET)
-- File: database/seed.sql
-- =====================================================================

-- 1. Locations (38 provinces and centrally-run cities)
INSERT INTO locations (name, slug, country_code) VALUES
('Hà Nội', 'ha-noi', 'VN'),
('TP. Hồ Chí Minh', 'tp-ho-chi-minh', 'VN'),
('Đà Nẵng', 'da-nang', 'VN'),
('Cần Thơ', 'can-tho', 'VN'),
('Hải Phòng', 'hai-phong', 'VN'),
('Bình Dương', 'binh-duong', 'VN'),
('Đồng Nai', 'dong-nai', 'VN'),
('Bà Rịa - Vũng Tàu', 'ba-ria-vung-tau', 'VN'),
('Thừa Thiên Huế', 'thua-thien-hue', 'VN'),
('Quảng Ninh', 'quang-ninh', 'VN'),
('Khánh Hòa', 'khanh-hoa', 'VN'),
('Lâm Đồng', 'lam-dong', 'VN'),
('Bắc Ninh', 'bac-ninh', 'VN'),
('Nghệ An', 'nghe-an', 'VN'),
('Tiền Giang', 'tien-giang', 'VN'),
('Hải Dương', 'hai-duong', 'VN'),
('Hưng Yên', 'hung-yen', 'VN'),
('Vĩnh Phúc', 'vinh-phuc', 'VN'),
('Thái Nguyên', 'thai-nguyen', 'VN'),
('Bắc Giang', 'bac-giang', 'VN'),
('Nam Định', 'nam-dinh', 'VN'),
('Thái Bình', 'thai-binh', 'VN'),
('Ninh Bình', 'ninh-binh', 'VN'),
('Thanh Hóa', 'thanh-hoa', 'VN'),
('Hà Tĩnh', 'ha-tinh', 'VN'),
('Quảng Bình', 'quang-binh', 'VN'),
('Quảng Trị', 'quang-tri', 'VN'),
('Quảng Nam', 'quang-nam', 'VN'),
('Quảng Ngãi', 'quang-ngai', 'VN'),
('Bình Định', 'binh-dinh', 'VN'),
('Phú Yên', 'phu-yen', 'VN'),
('Ninh Thuận', 'ninh-thuan', 'VN'),
('Bình Thuận', 'binh-thuan', 'VN'),
('Đắk Lắk', 'dak-lak', 'VN'),
('Gia Lai', 'gia-lai', 'VN'),
('Long An', 'long-an', 'VN'),
('Bến Tre', 'ben-tre', 'VN'),
('An Giang', 'an-giang', 'VN');

-- 2. Industries (12 industries, with parent-child hierarchy)
INSERT INTO industries (name, slug, parent_id) VALUES
('Công nghệ thông tin', 'cong-nghe-thong-tin', NULL),
('Phát triển phần mềm', 'phat-trien-phan-mem', 1),
('Tài chính - Ngân hàng', 'tai-chinh-ngan-hang', NULL),
('Thương mại điện tử', 'thuong-mai-dien-tu', 1),
('Trí tuệ nhân tạo & Data Science', 'tri-tue-nhan-tao-data-science', 1),
('Thiết kế UI/UX & Đồ họa', 'thiet-ke-ui-ux-do-hoa', NULL),
('Viễn thông & Mạng', 'vien-thong-mang', 1),
('Bảo mật & An toàn thông tin', 'bao-mat-an-toan-thong-tin', 1),
('Logistics & Vận tải', 'logistics-van-tai', NULL),
('Giáo dục & Đào tạo trực tuyến', 'giao-duc-dao-tao-truc-tuyen', NULL),
('Công nghệ sinh học & Y tế', 'cong-nghe-sinh-hoc-y-te', NULL),
('Bất động sản công nghệ', 'bat-dong-san-cong-nghe', NULL);

-- 3. Skills (30 skills across categories)
INSERT INTO skills (name, slug, category, aliases, is_verified) VALUES
('Python', 'python', 'technical', ARRAY['Python3', 'Py']::text[], TRUE),
('ReactJS', 'reactjs', 'technical', ARRAY['React', 'React.js']::text[], TRUE),
('PostgreSQL', 'postgresql', 'technical', ARRAY['Postgres', 'PG']::text[], TRUE),
('Docker', 'docker', 'tool', ARRAY['Container', 'Docker-compose']::text[], TRUE),
('Tiếng Anh', 'tieng-anh', 'language', ARRAY['English', 'TOEIC', 'IELTS']::text[], TRUE),
('Node.js', 'nodejs', 'technical', ARRAY['NodeJS', 'ExpressJS', 'NestJS']::text[], TRUE),
('Java', 'java', 'technical', ARRAY['Core Java', 'Java8', 'Java17']::text[], TRUE),
('Spring Boot', 'spring-boot', 'technical', ARRAY['Spring', 'SpringBoot']::text[], TRUE),
('VueJS', 'vuejs', 'technical', ARRAY['Vue', 'Vue.js']::text[], TRUE),
('Figma', 'figma', 'tool', ARRAY['UI Design', 'Wireframing']::text[], TRUE),
('Kubernetes', 'kubernetes', 'tool', ARRAY['K8s']::text[], TRUE),
('Giao tiếp & Thuyết trình', 'giao-tiep-thuyet-trinh', 'soft', ARRAY['Communication', 'Presentation']::text[], TRUE),
('Go (Golang)', 'go-golang', 'technical', ARRAY['Go', 'Golang']::text[], TRUE),
('TypeScript', 'typescript', 'technical', ARRAY['TS']::text[], TRUE),
('AWS Cloud', 'aws-cloud', 'tool', ARRAY['Amazon Web Services', 'AWS']::text[], TRUE),
('Redis', 'redis', 'technical', ARRAY['In-memory cache']::text[], TRUE),
('MongoDB', 'mongodb', 'technical', ARRAY['Mongo', 'NoSQL']::text[], TRUE),
('Làm việc nhóm', 'lam-viec-nhom', 'soft', ARRAY['Teamwork']::text[], TRUE),
('Giải quyết vấn đề', 'giai-quyet-van-de', 'soft', ARRAY['Problem Solving']::text[], TRUE),
('Tiếng Nhật', 'tieng-nhat', 'language', ARRAY['Japanese', 'JLPT N2', 'JLPT N3']::text[], TRUE),
('CI/CD Pipelines', 'cicd-pipelines', 'tool', ARRAY['GitHub Actions', 'GitLab CI', 'Jenkins']::text[], TRUE),
('TensorFlow', 'tensorflow', 'technical', ARRAY['TF', 'Deep Learning']::text[], TRUE),
('PyTorch', 'pytorch', 'technical', ARRAY['Torch']::text[], TRUE),
('Data Warehousing', 'data-warehousing', 'domain', ARRAY['DWH', 'Snowflake', 'BigQuery']::text[], TRUE),
('Fintech & Payment Gateway', 'fintech-payment-gateway', 'domain', ARRAY['Thanh toan truc tuyen']::text[], TRUE),
('E-Commerce Architecture', 'e-commerce-architecture', 'domain', ARRAY['San TMDT']::text[], TRUE),
('GraphQL', 'graphql', 'technical', ARRAY['GQL']::text[], TRUE),
('Next.js', 'nextjs', 'technical', ARRAY['Next', 'Next.js']::text[], TRUE),
('Linux OS Administration', 'linux-os-administration', 'tool', ARRAY['Ubuntu', 'CentOS', 'RHEL']::text[], TRUE),
('Quản lý thời gian', 'quan-ly-thoi-gian', 'soft', ARRAY['Time Management']::text[], TRUE);

-- 4. Users (1 Admin, 8 Recruiters/Employers, 16 Candidates)
INSERT INTO users (id, email, password, full_name, phone, role, is_active, is_staff, is_superuser, email_verified_at) VALUES
('00000000-0000-0000-0000-000000000001', 'admin@example.com', 'pbkdf2_sha256$260000$hashedpassword', 'Quản Trị Viên Hệ Thống', '0900000000', 'admin', TRUE, TRUE, TRUE, NOW()),
-- Employers
('00000000-0000-0000-0000-000000000002', 'hr@techcorp.vn', 'pbkdf2_sha256$260000$hashedpassword', 'Nguyễn Thị Hồng HR', '0901111111', 'employer', TRUE, FALSE, FALSE, NOW()),
('00000000-0000-0000-0000-000000000003', 'recruitment@fintechglobal.com', 'pbkdf2_sha256$260000$hashedpassword', 'Trần Văn Minh HR', '0902222222', 'employer', TRUE, FALSE, FALSE, NOW()),
('00000000-0000-0000-0000-000000000004', 'careers@aisolutions.io', 'pbkdf2_sha256$260000$hashedpassword', 'Hoàng Thu Trang Talent Lead', '0903333333', 'employer', TRUE, FALSE, FALSE, NOW()),
('00000000-0000-0000-0000-000000000005', 'jobs@ecomstars.vn', 'pbkdf2_sha256$260000$hashedpassword', 'Vũ Quốc Anh Head of HR', '0904444444', 'employer', TRUE, FALSE, FALSE, NOW()),
('00000000-0000-0000-0000-000000000006', 'talent@cloudscale.net', 'pbkdf2_sha256$260000$hashedpassword', 'Đặng Thùy Dung HR Specialist', '0905555555', 'employer', TRUE, FALSE, FALSE, NOW()),
('00000000-0000-0000-0000-000000000007', 'hiring@cyberdefense.vn', 'pbkdf2_sha256$260000$hashedpassword', 'Lý Hải Đăng Recruiter', '0906666666', 'employer', TRUE, FALSE, FALSE, NOW()),
('00000000-0000-0000-0000-000000000008', 'recruiter@logismart.com', 'pbkdf2_sha256$260000$hashedpassword', 'Phan Thanh Bình HR Lead', '0907777777', 'employer', TRUE, FALSE, FALSE, NOW()),
('00000000-0000-0000-0000-000000000009', 'contact@edutech.vn', 'pbkdf2_sha256$260000$hashedpassword', 'Mai Lan Hương People Operations', '0908888888', 'employer', TRUE, FALSE, FALSE, NOW()),
-- Candidates
('00000000-0000-0000-0000-000000000010', 'candidate.python@gmail.com', 'pbkdf2_sha256$260000$hashedpassword', 'Lê Tuấn Kiệt', '0910000001', 'candidate', TRUE, FALSE, FALSE, NOW()),
('00000000-0000-0000-0000-000000000011', 'candidate.frontend@gmail.com', 'pbkdf2_sha256$260000$hashedpassword', 'Trần Bảo Anh', '0910000002', 'candidate', TRUE, FALSE, FALSE, NOW()),
('00000000-0000-0000-0000-000000000012', 'candidate.java@gmail.com', 'pbkdf2_sha256$260000$hashedpassword', 'Nguyễn Đăng Khoa', '0910000003', 'candidate', TRUE, FALSE, FALSE, NOW()),
('00000000-0000-0000-0000-000000000013', 'candidate.devops@gmail.com', 'pbkdf2_sha256$260000$hashedpassword', 'Phạm Hoàng Nam', '0910000004', 'candidate', TRUE, FALSE, FALSE, NOW()),
('00000000-0000-0000-0000-000000000014', 'candidate.uiux@gmail.com', 'pbkdf2_sha256$260000$hashedpassword', 'Đinh Thảo Vy', '0910000005', 'candidate', TRUE, FALSE, FALSE, NOW()),
('00000000-0000-0000-0000-000000000015', 'candidate.ai@gmail.com', 'pbkdf2_sha256$260000$hashedpassword', 'Võ Trọng Nghĩa', '0910000006', 'candidate', TRUE, FALSE, FALSE, NOW()),
('00000000-0000-0000-0000-000000000016', 'candidate.golang@gmail.com', 'pbkdf2_sha256$260000$hashedpassword', 'Bùi Đức Huy', '0910000007', 'candidate', TRUE, FALSE, FALSE, NOW()),
('00000000-0000-0000-0000-000000000017', 'candidate.fullstack@gmail.com', 'pbkdf2_sha256$260000$hashedpassword', 'Dương Gia Hân', '0910000008', 'candidate', TRUE, FALSE, FALSE, NOW()),
('00000000-0000-0000-0000-000000000018', 'candidate.fresher1@gmail.com', 'pbkdf2_sha256$260000$hashedpassword', 'Trương Minh Trí', '0910000009', 'candidate', TRUE, FALSE, FALSE, NOW()),
('00000000-0000-0000-0000-000000000019', 'candidate.fresher2@gmail.com', 'pbkdf2_sha256$260000$hashedpassword', 'Lâm Khánh Linh', '0910000010', 'candidate', TRUE, FALSE, FALSE, NOW()),
('00000000-0000-0000-0000-000000000020', 'candidate.intern1@gmail.com', 'pbkdf2_sha256$260000$hashedpassword', 'Hà Quang Sáng', '0910000011', 'candidate', TRUE, FALSE, FALSE, NOW()),
('00000000-0000-0000-0000-000000000021', 'candidate.intern2@gmail.com', 'pbkdf2_sha256$260000$hashedpassword', 'Chu Ngọc Mai', '0910000012', 'candidate', TRUE, FALSE, FALSE, NOW()),
('00000000-0000-0000-0000-000000000022', 'candidate.manager@gmail.com', 'pbkdf2_sha256$260000$hashedpassword', 'Đoàn Nhật Quang', '0910000013', 'candidate', TRUE, FALSE, FALSE, NOW()),
('00000000-0000-0000-0000-000000000023', 'candidate.director@gmail.com', 'pbkdf2_sha256$260000$hashedpassword', 'Ngô Kiến Huy', '0910000014', 'candidate', TRUE, FALSE, FALSE, NOW()),
('00000000-0000-0000-0000-000000000024', 'candidate.security@gmail.com', 'pbkdf2_sha256$260000$hashedpassword', 'Lý Tuấn Kiệt', '0910000015', 'candidate', TRUE, FALSE, FALSE, NOW()),
('00000000-0000-0000-0000-000000000025', 'candidate.qa@gmail.com', 'pbkdf2_sha256$260000$hashedpassword', 'Tống Ánh Tuyết', '0910000016', 'candidate', TRUE, FALSE, FALSE, NOW());

-- 5. Candidate Profiles (16 candidate profiles)
INSERT INTO candidate_profiles (id, user_id, headline, date_of_birth, gender, address, location_id, summary, years_of_experience, current_level, desired_position, desired_salary_min, desired_salary_max, salary_currency, desired_job_type, desired_work_mode, is_open_to_work, is_public) VALUES
('33333333-3333-3333-3333-333333333310', '00000000-0000-0000-0000-000000000010', 'Backend Engineer | 3 năm kinh nghiệm Python/Django', '1998-05-15', 'male', '123 Cầu Giấy, Hà Nội', 1, 'Lập trình viên Backend có thế mạnh về thiết kế API RESTful, tối ưu cơ sở dữ liệu và microservices.', 3.0, 'staff', 'Senior Python Developer', 22000000, 38000000, 'VND', 'full_time', 'hybrid', TRUE, TRUE),
('33333333-3333-3333-3333-333333333311', '00000000-0000-0000-0000-000000000011', 'Frontend Developer | ReactJS & TypeScript', '2000-09-20', 'female', '456 Lê Duẩn, Đà Nẵng', 3, 'Chuyên xây dựng web app tương tác cao bằng ReactJS, Redux Toolkit, TailwindCSS và Next.js.', 2.5, 'staff', 'Senior Frontend Engineer', 18000000, 30000000, 'VND', 'full_time', 'remote', TRUE, TRUE),
('33333333-3333-3333-3333-333333333312', '00000000-0000-0000-0000-000000000012', 'Java Enterprise Architect | Spring Boot Specialist', '1993-02-10', 'male', '789 Nguyễn Huệ, Quận 1, TP.HCM', 2, 'Hơn 7 năm kinh nghiệm với hạ tầng tài chính, hệ thống ngân hàng chịu tải lớn bằng Java và Spring Cloud.', 7.0, 'supervisor', 'Software Architect / Tech Lead', 45000000, 70000000, 'VND', 'full_time', 'onsite', TRUE, TRUE),
('33333333-3333-3333-3333-333333333313', '00000000-0000-0000-0000-000000000013', 'DevOps & Site Reliability Engineer (SRE)', '1996-07-28', 'male', '12 Cách Mạng Tháng 8, Cần Thơ', 4, 'Chuyên gia xây dựng pipeline CI/CD, quản trị hạ tầng AWS và cụm Kubernetes đa vùng.', 4.5, 'staff', 'Lead DevOps Engineer', 30000000, 50000000, 'VND', 'full_time', 'remote', TRUE, TRUE),
('33333333-3333-3333-3333-333333333314', '00000000-0000-0000-0000-000000000014', 'Senior UI/UX Designer | Product Design', '1997-12-05', 'female', '55 Quang Trung, Hải Phòng', 5, 'Kinh nghiệm thiết kế trải nghiệm người dùng các hệ thống SaaS B2B và siêu ứng dụng bán lẻ.', 3.5, 'staff', 'Lead Product Designer', 20000000, 35000000, 'VND', 'full_time', 'hybrid', TRUE, TRUE),
('33333333-3333-3333-3333-333333333315', '00000000-0000-0000-0000-000000000015', 'AI/ML Engineer | Computer Vision & NLP', '1995-04-18', 'male', '100 Đại Cồ Việt, Hai Bà Trưng, Hà Nội', 1, 'Phát triển mô hình Deep Learning ứng dụng cho nhận diện khuôn mặt và chatbot thông minh.', 4.0, 'staff', 'Senior AI Engineer', 35000000, 60000000, 'VND', 'full_time', 'hybrid', TRUE, TRUE),
('33333333-3333-3333-3333-333333333316', '00000000-0000-0000-0000-000000000016', 'Golang Backend Developer | High Throughput System', '1997-08-30', 'male', '68 Hoàng Văn Thụ, Bình Dương', 6, 'Xây dựng core giao dịch tốc độ cao bằng Go, gRPC, Kafka và Redis.', 3.0, 'staff', 'Backend Go Engineer', 25000000, 42000000, 'VND', 'full_time', 'remote', TRUE, TRUE),
('33333333-3333-3333-3333-333333333317', '00000000-0000-0000-0000-000000000017', 'Fullstack JavaScript Developer (Node.js + React)', '1999-03-12', 'female', '200 Võ Thị Sáu, Quận 3, TP.HCM', 2, 'Xây dựng ứng dụng hoàn chỉnh từ giao diện đến server backend phục vụ thương mại điện tử.', 2.5, 'staff', 'Fullstack Engineer', 18000000, 28000000, 'VND', 'full_time', 'hybrid', TRUE, TRUE),
('33333333-3333-3333-3333-333333333318', '00000000-0000-0000-0000-000000000018', 'Fresher Backend Developer | Java & Spring Boot', '2002-11-20', 'male', '45 Hoàng Diệu, Đà Nẵng', 3, 'Tốt nghiệp loại Giỏi ngành CNTT, có dự án thực tế về REST API và cơ sở dữ liệu quan hệ.', 0.5, 'fresher', 'Junior Backend Developer', 9000000, 14000000, 'VND', 'full_time', 'onsite', TRUE, TRUE),
('33333333-3333-3333-3333-333333333319', '00000000-0000-0000-0000-000000000019', 'Fresher Frontend Developer | VueJS & Nuxt', '2002-06-15', 'female', '32 Hùng Vương, Huế', 9, 'Nắm vững kiến thức HTML/CSS/JavaScript hiện đại, ham học hỏi và tư duy thiết kế giao diện tốt.', 0.5, 'fresher', 'Junior Frontend Developer', 8000000, 13000000, 'VND', 'full_time', 'hybrid', TRUE, TRUE),
('33333333-3333-3333-3333-333333333320', '00000000-0000-0000-0000-000000000020', 'Intern Python Developer', '2003-01-22', 'male', '88 Trần Phú, Hà Đông, Hà Nội', 1, 'Sinh viên năm cuối tìm kiếm cơ hội thực tập phát triển web và xử lý dữ liệu với Python.', 0.0, 'intern', 'Python Intern', 3000000, 6000000, 'VND', 'internship', 'onsite', TRUE, TRUE),
('33333333-3333-3333-3333-333333333321', '00000000-0000-0000-0000-000000000021', 'Intern UI/UX Designer', '2003-08-08', 'female', '15 Lê Lợi, TP. Vũng Tàu', 8, 'Yêu thích thiết kế trải nghiệm người dùng, thành thạo công cụ Figma và vẽ vector.', 0.0, 'intern', 'Design Intern', 3000000, 5000000, 'VND', 'internship', 'hybrid', TRUE, TRUE),
('33333333-3333-3333-3333-333333333322', '00000000-0000-0000-0000-000000000022', 'Engineering Manager | 10+ năm kinh nghiệm quản lý', '1988-10-14', 'male', '50 Nam Kỳ Khởi Nghĩa, Quận 1, TP.HCM', 2, 'Kinh nghiệm dẫn dắt đội ngũ kỹ thuật 40+ kỹ sư, triển khai quy trình Agile/Scrum và chuyển đổi số.', 10.0, 'manager', 'Engineering Manager / Head of Tech', 60000000, 95000000, 'VND', 'full_time', 'hybrid', TRUE, TRUE),
('33333333-3333-3333-3333-333333333323', '00000000-0000-0000-0000-000000000023', 'Chief Technology Officer (CTO) | Định hướng công nghệ', '1984-05-02', 'male', '12 Xuân Diệu, Tây Hồ, Hà Nội', 1, 'Từng giữ vai trò CTO tại các startup kỳ lân công nghệ, quản trị kiến trúc tổng thể và ngân sách R&D.', 14.0, 'director', 'CTO / VP of Engineering', 100000000, 160000000, 'VND', 'full_time', 'hybrid', FALSE, TRUE),
('33333333-3333-3333-3333-333333333324', '00000000-0000-0000-0000-000000000024', 'Cybersecurity Specialist | SOC & Pentest', '1996-09-09', 'male', '230 Lê Duẩn, TP. Vinh, Nghệ An', 14, 'Chứng chỉ CEH, OSCP, chuyên đánh giá an ninh mạng và rà soát lỗ hổng hệ thống.', 4.0, 'staff', 'Security Specialist', 28000000, 48000000, 'VND', 'full_time', 'remote', TRUE, TRUE),
('33333333-3333-3333-3333-333333333325', '00000000-0000-0000-0000-000000000025', 'QA/QC Automation Lead | Cypress & Selenium', '1998-02-28', 'female', '77 Nguyễn Trãi, Thanh Xuân, Hà Nội', 1, 'Xây dựng khung kiểm thử tự động, tích hợp CI/CD để đảm bảo chất lượng phát hành liên tục.', 3.5, 'staff', 'QA Automation Lead', 20000000, 32000000, 'VND', 'full_time', 'hybrid', TRUE, TRUE);

-- 6. Candidate Preferred Locations
INSERT INTO candidate_preferred_locations (candidate_id, location_id) VALUES
('33333333-3333-3333-3333-333333333310', 1),
('33333333-3333-3333-3333-333333333310', 2),
('33333333-3333-3333-3333-333333333311', 3),
('33333333-3333-3333-3333-333333333311', 2),
('33333333-3333-3333-3333-333333333312', 2),
('33333333-3333-3333-3333-333333333313', 4),
('33333333-3333-3333-3333-333333333313', 2),
('33333333-3333-3333-3333-333333333314', 5),
('33333333-3333-3333-3333-333333333314', 1),
('33333333-3333-3333-3333-333333333315', 1),
('33333333-3333-3333-3333-333333333316', 6),
('33333333-3333-3333-3333-333333333316', 2),
('33333333-3333-3333-3333-333333333317', 2),
('33333333-3333-3333-3333-333333333318', 3),
('33333333-3333-3333-3333-333333333319', 9),
('33333333-3333-3333-3333-333333333320', 1),
('33333333-3333-3333-3333-333333333321', 8),
('33333333-3333-3333-3333-333333333322', 2),
('33333333-3333-3333-3333-333333333323', 1),
('33333333-3333-3333-3333-333333333324', 14),
('33333333-3333-3333-3333-333333333325', 1);

-- 7. Candidate Educations (16 records)
INSERT INTO candidate_educations (id, candidate_id, school, degree, major, gpa, start_date, end_date, description, sort_order) VALUES
('a1111111-1111-1111-1111-111111111110', '33333333-3333-3333-3333-333333333310', 'Đại học Bách Khoa Hà Nội', 'Kỹ sư', 'Công nghệ thông tin', 3.45, '2016-09-01', '2021-06-30', 'Hệ đào tạo Kỹ sư chất lượng cao CNTT', 1),
('a1111111-1111-1111-1111-111111111111', '33333333-3333-3333-3333-333333333311', 'Đại học Bách Khoa Đà Nẵng', 'Kỹ sư', 'Kỹ thuật phần mềm', 3.30, '2018-09-01', '2022-06-30', 'Học bổng khuyến khích học tập 3 kỳ liên tiếp', 1),
('a1111111-1111-1111-1111-111111111112', '33333333-3333-3333-3333-333333333312', 'Đại học Khoa học Tự nhiên TP.HCM', 'Cử nhân', 'Khoa học máy tính', 3.65, '2011-09-01', '2015-06-30', 'Tốt nghiệp loại Giỏi chuyên ngành Hệ thống', 1),
('a1111111-1111-1111-1111-111111111113', '33333333-3333-3333-3333-333333333313', 'Đại học Cần Thơ', 'Kỹ sư', 'Mạng máy tính và Truyền thông', 3.20, '2014-09-01', '2018-06-30', 'Nghiên cứu ứng dụng SDN và hạ tầng mạng ảo hóa', 1),
('a1111111-1111-1111-1111-111111111114', '33333333-3333-3333-3333-333333333314', 'Đại học Mỹ thuật Công nghiệp Hà Nội', 'Cử nhân', 'Thiết kế đồ họa', 3.40, '2015-09-01', '2019-06-30', 'Giải Nhất đồ án tốt nghiệp thiết kế sản phẩm số', 1),
('a1111111-1111-1111-1111-111111111115', '33333333-3333-3333-3333-333333333315', 'Đại học Công nghệ - ĐHQGHN', 'Kỹ sư', 'Khoa học dữ liệu', 3.75, '2013-09-01', '2017-06-30', 'Đại diện trường tham gia kỳ thi sinh viên NCKH toàn quốc', 1),
('a1111111-1111-1111-1111-111111111116', '33333333-3333-3333-3333-333333333316', 'Đại học Quốc tế - ĐHQG TP.HCM', 'Cử nhân', 'Computer Science', 3.50, '2015-09-01', '2019-06-30', 'Chương trình giảng dạy 100% bằng tiếng Anh', 1),
('a1111111-1111-1111-1111-111111111117', '33333333-3333-3333-3333-333333333317', 'Đại học Sư phạm Kỹ thuật TP.HCM', 'Kỹ sư', 'Công nghệ thông tin', 3.15, '2017-09-01', '2021-06-30', 'Chuyên ngành Kỹ thuật phần mềm', 1),
('a1111111-1111-1111-1111-111111111118', '33333333-3333-3333-3333-333333333318', 'Đại học Sư phạm Đà Nẵng', 'Cử nhân', 'Tin học ứng dụng', 3.55, '2020-09-01', '2024-06-30', 'Thủ khoa đầu ra của khoa', 1),
('a1111111-1111-1111-1111-111111111119', '33333333-3333-3333-3333-333333333319', 'Đại học Khoa học Huế', 'Cử nhân', 'Công nghệ thông tin', 3.40, '2020-09-01', '2024-06-30', 'Nghiên cứu giao diện người dùng trên web', 1),
('a1111111-1111-1111-1111-111111111120', '33333333-3333-3333-3333-333333333320', 'Học viện Công nghệ Bưu chính Viễn thông', 'Sinh viên', 'Công nghệ thông tin', 3.20, '2021-09-01', NULL, 'Đang học năm thứ 4', 1),
('a1111111-1111-1111-1111-111111111121', '33333333-3333-3333-3333-333333333321', 'Đại học Kiến trúc TP.HCM', 'Sinh viên', 'Thiết kế đa phương tiện', 3.35, '2021-09-01', NULL, 'Đang học năm thứ 4', 1),
('a1111111-1111-1111-1111-111111111122', '33333333-3333-3333-3333-333333333322', 'Đại học Bách Khoa TP.HCM', 'Thạc sĩ', 'Kỹ thuật máy tính', 3.80, '2006-09-01', '2012-06-30', 'Hoàn thành chương trình Thạc sĩ nghiên cứu', 1),
('a1111111-1111-1111-1111-111111111123', '33333333-3333-3333-3333-333333333323', 'National University of Singapore (NUS)', 'Thạc sĩ', 'Software Engineering', 3.90, '2002-09-01', '2008-06-30', 'Học bổng toàn phần chính phủ', 1),
('a1111111-1111-1111-1111-111111111124', '33333333-3333-3333-3333-333333333324', 'Học viện Kỹ thuật Mật mã', 'Kỹ sư', 'An toàn thông tin', 3.40, '2014-09-01', '2019-06-30', 'Chứng chỉ quốc tế CEH v11', 1),
('a1111111-1111-1111-1111-111111111125', '33333333-3333-3333-3333-333333333325', 'Đại học Thăng Long', 'Cử nhân', 'Hệ thống thông tin quản lý', 3.25, '2016-09-01', '2020-06-30', 'Chứng chỉ kiểm thử ISTQB Foundation Level', 1);

-- 8. Candidate Experiences (18 records)
INSERT INTO candidate_experiences (id, candidate_id, company_name, position, start_date, end_date, is_current, description, sort_order) VALUES
('b1111111-1111-1111-1111-111111111110', '33333333-3333-3333-3333-333333333310', 'Công ty Giải Pháp Phần Mềm NextGen', 'Python Backend Developer', '2021-08-01', NULL, TRUE, 'Xây dựng core backend phục vụ hơn 500k người dùng hoạt động hàng tháng.', 1),
('b1111111-1111-1111-1111-111111111111', '33333333-3333-3333-3333-333333333311', 'Danang Digital Agency', 'Frontend Developer', '2022-07-01', NULL, TRUE, 'Xây dựng giao diện Single Page App với ReactJS, Next.js và TailwindCSS.', 1),
('b1111111-1111-1111-1111-111111111112', '33333333-3333-3333-3333-333333333312', 'Ngân hàng Thương mại Cổ phần Sài Gòn', 'Senior Java Developer', '2016-01-01', '2021-05-31', FALSE, 'Phát triển lõi Core Banking kết nối cổng thanh toán quốc tế.', 2),
('b1111111-1111-1111-1111-111111111113', '33333333-3333-3333-3333-333333333312', 'Fintech Vietnam Hub', 'Lead Solution Architect', '2021-06-01', NULL, TRUE, 'Thiết kế kiến trúc hệ thống xử lý giao dịch thời gian thực với Kafka và Spring Cloud.', 1),
('b1111111-1111-1111-1111-111111111114', '33333333-3333-3333-3333-333333333313', 'Công ty Dịch vụ Đám mây Mekong', 'DevOps Specialist', '2019-03-01', NULL, TRUE, 'Quản trị cụm Kubernetes hơn 100 nodes trên hạ tầng AWS và GCP.', 1),
('b1111111-1111-1111-1111-111111111115', '33333333-3333-3333-3333-333333333314', 'Studio Thiết kế Sáng tạo Pixel', 'Product Designer', '2020-02-01', NULL, TRUE, 'Nghiên cứu người dùng, xây dựng Design System hoàn chỉnh trên Figma.', 1),
('b1111111-1111-1111-1111-111111111116', '33333333-3333-3333-3333-333333333315', 'Trung tâm Nghiên cứu AI Đông Á', 'Computer Vision Engineer', '2018-09-01', NULL, TRUE, 'Triển khai các pipeline huấn luyện mô hình Object Detection và OCR.', 1),
('b1111111-1111-1111-1111-111111111117', '33333333-3333-3333-3333-333333333316', 'Binh Duong Payment Gateway', 'Go Backend Engineer', '2020-10-01', NULL, TRUE, 'Thiết kế API gRPC hiệu năng cao phục vụ thanh toán mã QR.', 1),
('b1111111-1111-1111-1111-111111111118', '33333333-3333-3333-3333-333333333317', 'E-Store Retail JSC', 'Fullstack JavaScript Developer', '2021-11-01', NULL, TRUE, 'Tích hợp hệ thống quản lý kho hàng và giỏ hàng trực tuyến.', 1),
('b1111111-1111-1111-1111-111111111119', '33333333-3333-3333-3333-333333333322', 'Tập đoàn Công nghệ Viễn thông Vina', 'Engineering Director', '2014-05-01', '2022-12-31', FALSE, 'Điều hành 5 nhóm phát triển phần mềm gồm 50 thành viên.', 2),
('b1111111-1111-1111-1111-111111111120', '33333333-3333-3333-3333-333333333322', 'Global Tech Services', 'VP of Engineering', '2023-01-01', NULL, TRUE, 'Hoạch định chiến lược công nghệ và tuyển dụng các vị trí cấp cao.', 1),
('b1111111-1111-1111-1111-111111111121', '33333333-3333-3333-3333-333333333323', 'Singapore Unicorn Tech', 'Chief Technology Officer (CTO)', '2015-01-01', '2023-06-30', FALSE, 'Đưa công ty từ quy mô 20 người lên 600 nhân sự trên toàn Đông Nam Á.', 1),
('b1111111-1111-1111-1111-111111111122', '33333333-3333-3333-3333-333333333324', 'Trung tâm Giám sát An toàn Không gian mạng', 'Security Engineer', '2019-10-01', NULL, TRUE, 'Giám sát cảnh báo SIEM, rà soát mã độc và phân tích log hệ thống.', 1),
('b1111111-1111-1111-1111-111111111123', '33333333-3333-3333-3333-333333333325', 'Quality Software Lab', 'Automation Test Lead', '2020-07-01', NULL, TRUE, 'Tự động hóa hơn 1,500 kịch bản kiểm thử hồi quy cho ứng dụng web và mobile.', 1);

-- 9. Candidate Skills (40 records)
INSERT INTO candidate_skills (candidate_id, skill_id, level, years_of_experience) VALUES
('33333333-3333-3333-3333-333333333310', 1, 4, 3.0),
('33333333-3333-3333-3333-333333333310', 3, 4, 3.0),
('33333333-3333-3333-3333-333333333310', 4, 3, 2.0),
('33333333-3333-3333-3333-333333333310', 16, 3, 2.0),
('33333333-3333-3333-3333-333333333311', 2, 4, 2.5),
('33333333-3333-3333-3333-333333333311', 14, 4, 2.0),
('33333333-3333-3333-3333-333333333311', 28, 3, 1.5),
('33333333-3333-3333-3333-333333333311', 5, 4, 4.0),
('33333333-3333-3333-3333-333333333312', 7, 5, 7.0),
('33333333-3333-3333-3333-333333333312', 8, 5, 6.0),
('33333333-3333-3333-3333-333333333312', 3, 5, 7.0),
('33333333-3333-3333-3333-333333333312', 25, 4, 5.0),
('33333333-3333-3333-3333-333333333313', 4, 5, 4.5),
('33333333-3333-3333-3333-333333333313', 11, 5, 4.0),
('33333333-3333-3333-3333-333333333313', 15, 4, 3.5),
('33333333-3333-3333-3333-333333333313', 21, 4, 4.0),
('33333333-3333-3333-3333-333333333314', 10, 5, 3.5),
('33333333-3333-3333-3333-333333333314', 12, 4, 3.0),
('33333333-3333-3333-3333-333333333315', 1, 5, 4.0),
('33333333-3333-3333-3333-333333333315', 22, 4, 3.0),
('33333333-3333-3333-3333-333333333315', 23, 4, 3.0),
('33333333-3333-3333-3333-333333333316', 13, 4, 3.0),
('33333333-3333-3333-3333-333333333316', 3, 4, 3.0),
('33333333-3333-3333-3333-333333333316', 16, 4, 3.0),
('33333333-3333-3333-3333-333333333317', 6, 4, 2.5),
('33333333-3333-3333-3333-333333333317', 2, 4, 2.5),
('33333333-3333-3333-3333-333333333317', 17, 3, 2.0),
('33333333-3333-3333-3333-333333333318', 7, 3, 0.5),
('33333333-3333-3333-3333-333333333318', 8, 3, 0.5),
('33333333-3333-3333-3333-333333333319', 9, 3, 0.5),
('33333333-3333-3333-3333-333333333320', 1, 2, 0.0),
('33333333-3333-3333-3333-333333333321', 10, 3, 0.0),
('33333333-3333-3333-3333-333333333322', 12, 5, 8.0),
('33333333-3333-3333-3333-333333333322', 18, 5, 10.0),
('33333333-3333-3333-3333-333333333323', 19, 5, 14.0),
('33333333-3333-3333-3333-333333333323', 5, 5, 12.0),
('33333333-3333-3333-3333-333333333324', 29, 4, 4.0),
('33333333-3333-3333-3333-333333333324', 8, 3, 2.0),
('33333333-3333-3333-3333-333333333325', 1, 3, 2.0),
('33333333-3333-3333-3333-333333333325', 18, 4, 3.5);

-- 10. Companies (8 Companies)
INSERT INTO companies (id, name, slug, tax_code, logo_url, website, email, phone, address, location_id, industry_id, company_size, founded_year, description, verification_status, verified_at, verified_by, created_by) VALUES
('11111111-1111-1111-1111-111111111101', 'Công ty Cổ phần Công nghệ TechCorp Vietnam', 'techcorp-vietnam', '0101234567', 'https://cdn.example.com/techcorp-logo.png', 'https://techcorp.vn', 'contact@techcorp.vn', '02439998888', 'Tầng 5, Tòa nhà A, Cầu Giấy, Hà Nội', 1, 2, '51-200', 2018, 'Doanh nghiệp tiên phong cung cấp giải pháp Cloud và phát triển phần mềm theo yêu cầu.', 'verified', NOW(), '00000000-0000-0000-0000-000000000001', '00000000-0000-0000-0000-000000000002'),
('11111111-1111-1111-1111-111111111102', 'Tập đoàn Giải pháp Tài chính FinTech Global', 'fintech-global', '0309876543', 'https://cdn.example.com/fintech-logo.png', 'https://fintechglobal.com', 'hr@fintechglobal.com', '02837776666', 'Tầng 12, Tòa nhà Bitexco, Quận 1, TP.HCM', 2, 3, '201-500', 2015, 'Cung cấp hạ tầng thanh toán số và ngân hàng mở cho các định chế tài chính quốc tế.', 'verified', NOW(), '00000000-0000-0000-0000-000000000001', '00000000-0000-0000-0000-000000000003'),
('11111111-1111-1111-1111-111111111103', 'Công ty TNHH Giải pháp Trí tuệ Nhân tạo AI Solutions Corp', 'ai-solutions-corp', '0109998877', 'https://cdn.example.com/aisolutions-logo.png', 'https://aisolutions.io', 'info@aisolutions.io', '02431112222', 'Tầng 8, Tòa Keangnam, Nam Từ Liêm, Hà Nội', 1, 5, '11-50', 2021, 'R&D các sản phẩm thị giác máy tính và xử lý ngôn ngữ tự nhiên ứng dụng trong doanh nghiệp.', 'verified', NOW(), '00000000-0000-0000-0000-000000000001', '00000000-0000-0000-0000-000000000004'),
('11111111-1111-1111-1111-111111111104', 'Sàn Thương mại Điện tử E-Commerce Stars', 'e-commerce-stars', '0301112233', 'https://cdn.example.com/ecom-logo.png', 'https://ecomstars.vn', 'recruitment@ecomstars.vn', '02834445555', 'Tầng 3, Tòa nhà D, Quận 3, TP.HCM', 2, 4, '501-1000', 2017, 'Nền tảng mua sắm trực tuyến với chuỗi logistics hiện đại và độ phủ sóng toàn quốc.', 'verified', NOW(), '00000000-0000-0000-0000-000000000001', '00000000-0000-0000-0000-000000000005'),
('11111111-1111-1111-1111-111111111105', 'Công ty Hạ tầng Đám mây CloudScale Networks', 'cloudscale-networks', '0405556677', 'https://cdn.example.com/cloudscale-logo.png', 'https://cloudscale.net', 'career@cloudscale.net', '02363888999', 'Khu Công viên Phần mềm Đà Nẵng, Hải Châu, Đà Nẵng', 3, 1, '51-200', 2019, 'Cung cấp hạ tầng ảo hóa bare-metal, cụm máy chủ Kubernetes và dịch vụ an toàn mạng.', 'verified', NOW(), '00000000-0000-0000-0000-000000000001', '00000000-0000-0000-0000-000000000006'),
('11111111-1111-1111-1111-111111111106', 'Công ty An toàn Thông tin CyberDefense Vietnam', 'cyberdefense-vietnam', '0106667788', 'https://cdn.example.com/cyberdef-logo.png', 'https://cyberdefense.vn', 'security@cyberdefense.vn', '02437778899', 'Tòa CMC Tower, Cầu Giấy, Hà Nội', 1, 8, '11-50', 2020, 'Đơn vị kiểm định an ninh ứng dụng và phản ứng sự cố không gian mạng chuyên nghiệp.', 'verified', NOW(), '00000000-0000-0000-0000-000000000001', '00000000-0000-0000-0000-000000000007'),
('11111111-1111-1111-1111-111111111107', 'LogiSmart Vận tải Thông minh', 'logismart-van-tai', '0308889900', 'https://cdn.example.com/logismart-logo.png', 'https://logismart.com', 'jobs@logismart.com', '02839991122', 'Khu Công nghệ cao Quận 9, TP. Thủ Đức, TP.HCM', 2, 9, '201-500', 2016, 'Giải pháp số hóa chuỗi cung ứng và điều phối vận tải chặng cuối tự động bằng IoT.', 'verified', NOW(), '00000000-0000-0000-0000-000000000001', '00000000-0000-0000-0000-000000000008'),
('11111111-1111-1111-1111-111111111108', 'Công ty Giáo dục Số EduTech Future', 'edutech-future', '0103334455', 'https://cdn.example.com/edutech-logo.png', 'https://edutech.vn', 'hello@edutech.vn', '02435556677', 'Tầng 4, Tòa Hapulico, Thanh Xuân, Hà Nội', 1, 10, '51-200', 2022, 'Hệ thống học trực tuyến cá nhân hóa với trợ lý gia sư trí tuệ nhân tạo.', 'verified', NOW(), '00000000-0000-0000-0000-000000000001', '00000000-0000-0000-0000-000000000009');

-- 11. Recruiters (8 Recruiters)
INSERT INTO recruiters (id, user_id, company_id, position, company_role, status, joined_at) VALUES
('22222222-2222-2222-2222-222222222201', '00000000-0000-0000-0000-000000000002', '11111111-1111-1111-1111-111111111101', 'HR Director', 'owner', 'active', NOW()),
('22222222-2222-2222-2222-222222222202', '00000000-0000-0000-0000-000000000003', '11111111-1111-1111-1111-111111111102', 'Head of Talent Acquisition', 'owner', 'active', NOW()),
('22222222-2222-2222-2222-222222222203', '00000000-0000-0000-0000-000000000004', '11111111-1111-1111-1111-111111111103', 'Talent Partner', 'owner', 'active', NOW()),
('22222222-2222-2222-2222-222222222204', '00000000-0000-0000-0000-000000000005', '11111111-1111-1111-1111-111111111104', 'Senior Recruiter', 'owner', 'active', NOW()),
('22222222-2222-2222-2222-222222222205', '00000000-0000-0000-0000-000000000006', '11111111-1111-1111-1111-111111111105', 'HR Lead', 'owner', 'active', NOW()),
('22222222-2222-2222-2222-222222222206', '00000000-0000-0000-0000-000000000006', '11111111-1111-1111-1111-111111111106', 'Recruitment Specialist', 'owner', 'active', NOW()),
('22222222-2222-2222-2222-222222222207', '00000000-0000-0000-0000-000000000007', '11111111-1111-1111-1111-111111111107', 'HR Manager', 'owner', 'active', NOW()),
('22222222-2222-2222-2222-222222222208', '00000000-0000-0000-0000-000000000008', '11111111-1111-1111-1111-111111111108', 'People Lead', 'owner', 'active', NOW());

-- 12. CVs (16 CVs, one for each candidate profile)
INSERT INTO cvs (id, candidate_id, title, file_key, original_filename, mime_type, file_size, file_hash, language, is_default, parse_status, raw_text, parsed_data, parsed_at) VALUES
('44444444-4444-4444-4444-444444444410', '33333333-3333-3333-3333-333333333310', 'CV Lê Tuấn Kiệt - Python Engineer', 'cvs/2026/01/cv_kiet_python.pdf', 'CV_LeTuanKiet_Python.pdf', 'application/pdf', 154200, 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855', 'vi', TRUE, 'completed', 'Nội dung chi tiết CV Backend Developer...', '{"name": "Lê Tuấn Kiệt", "skills": ["Python", "PostgreSQL", "Docker", "Redis"]}'::jsonb, NOW()),
('44444444-4444-4444-4444-444444444411', '33333333-3333-3333-3333-333333333311', 'CV Trần Bảo Anh - Frontend React', 'cvs/2026/01/cv_baoanh_fe.pdf', 'CV_TranBaoAnh_Frontend.pdf', 'application/pdf', 142000, 'a1b2c3d4e5f678901234567890abcdef1234567890abcdef1234567890abcdef', 'vi', TRUE, 'completed', 'Kinh nghiệm phát triển ReactJS, Next.js...', '{"name": "Trần Bảo Anh", "skills": ["ReactJS", "TypeScript", "Next.js"]}'::jsonb, NOW()),
('44444444-4444-4444-4444-444444444412', '33333333-3333-3333-3333-333333333312', 'CV Nguyễn Đăng Khoa - Java Architect', 'cvs/2026/01/cv_khoa_java.pdf', 'CV_NguyenDangKhoa_Java.pdf', 'application/pdf', 215000, 'b2c3d4e5f678901234567890abcdef1234567890abcdef1234567890abcdef12', 'en', TRUE, 'completed', 'Full profile Java Solution Architect with 7 years experience...', '{"name": "Nguyễn Đăng Khoa", "skills": ["Java", "Spring Boot", "PostgreSQL", "Microservices"]}'::jsonb, NOW()),
('44444444-4444-4444-4444-444444444413', '33333333-3333-3333-3333-333333333313', 'CV Phạm Hoàng Nam - DevOps SRE', 'cvs/2026/01/cv_nam_devops.pdf', 'CV_PhamHoangNam_DevOps.pdf', 'application/pdf', 188000, 'c3d4e5f678901234567890abcdef1234567890abcdef1234567890abcdef1234', 'vi', TRUE, 'completed', 'Kinh nghiệm triển khai Kubernetes, AWS và Terraform...', '{"name": "Phạm Hoàng Nam", "skills": ["Docker", "Kubernetes", "AWS Cloud", "CI/CD"]}'::jsonb, NOW()),
('44444444-4444-4444-4444-444444444414', '33333333-3333-3333-3333-333333333314', 'CV Đinh Thảo Vy - UI UX Product', 'cvs/2026/01/cv_vy_uiux.pdf', 'CV_DinhThaoVy_UIUX.pdf', 'application/pdf', 310000, 'd4e5f678901234567890abcdef1234567890abcdef1234567890abcdef123456', 'vi', TRUE, 'completed', 'Hồ sơ năng lực thiết kế giao diện sản phẩm số Figma...', '{"name": "Đinh Thảo Vy", "skills": ["Figma", "UI/UX", "User Research"]}'::jsonb, NOW()),
('44444444-4444-4444-4444-444444444415', '33333333-3333-3333-3333-333333333315', 'CV Võ Trọng Nghĩa - AI Engineer', 'cvs/2026/01/cv_nghia_ai.pdf', 'CV_VoTrongNghia_AI.pdf', 'application/pdf', 240000, 'e5f678901234567890abcdef1234567890abcdef1234567890abcdef12345678', 'en', TRUE, 'completed', 'Applied AI Researcher with TensorFlow and PyTorch expertise...', '{"name": "Võ Trọng Nghĩa", "skills": ["Python", "TensorFlow", "PyTorch", "Computer Vision"]}'::jsonb, NOW()),
('44444444-4444-4444-4444-444444444416', '33333333-3333-3333-3333-333333333316', 'CV Bùi Đức Huy - Golang Backend', 'cvs/2026/01/cv_huy_golang.pdf', 'CV_BuiDucHuy_Golang.pdf', 'application/pdf', 165000, 'f678901234567890abcdef1234567890abcdef1234567890abcdef1234567890', 'vi', TRUE, 'completed', 'Chuyên gia Golang hệ thống chịu tải cao...', '{"name": "Bùi Đức Huy", "skills": ["Go (Golang)", "PostgreSQL", "Redis", "Kafka"]}'::jsonb, NOW()),
('44444444-4444-4444-4444-444444444417', '33333333-3333-3333-3333-333333333317', 'CV Dương Gia Hân - Fullstack JS', 'cvs/2026/01/cv_han_fullstack.pdf', 'CV_DuongGiaHan_Fullstack.pdf', 'application/pdf', 178000, '0123456789abcdef1234567890abcdef1234567890abcdef1234567890abcdef', 'vi', TRUE, 'completed', 'Fullstack Developer with Node.js, Express and ReactJS...', '{"name": "Dương Gia Hân", "skills": ["Node.js", "ReactJS", "MongoDB"]}'::jsonb, NOW()),
('44444444-4444-4444-4444-444444444418', '33333333-3333-3333-3333-333333333318', 'CV Trương Minh Trí - Fresher Java', 'cvs/2026/01/cv_tri_fresher_java.pdf', 'CV_TruongMinhTri_Java.pdf', 'application/pdf', 120000, '1234567890abcdef0123456789abcdef1234567890abcdef0123456789abcdef', 'vi', TRUE, 'completed', 'Hồ sơ Fresher tốt nghiệp xuất sắc...', '{"name": "Trương Minh Trí", "skills": ["Java", "Spring Boot"]}'::jsonb, NOW()),
('44444444-4444-4444-4444-444444444419', '33333333-3333-3333-3333-333333333319', 'CV Lâm Khánh Linh - Fresher Vue', 'cvs/2026/01/cv_linh_fresher_vue.pdf', 'CV_LamKhanhLinh_Vue.pdf', 'application/pdf', 115000, '234567890abcdef0123456789abcdef1234567890abcdef0123456789abcdef1', 'vi', TRUE, 'completed', 'Hồ sơ Fresher Frontend VueJS...', '{"name": "Lâm Khánh Linh", "skills": ["VueJS", "JavaScript"]}'::jsonb, NOW()),
('44444444-4444-4444-4444-444444444420', '33333333-3333-3333-3333-333333333320', 'CV Hà Quang Sáng - Python Intern', 'cvs/2026/01/cv_sang_intern.pdf', 'CV_HaQuangSang_Intern.pdf', 'application/pdf', 98000, '34567890abcdef0123456789abcdef1234567890abcdef0123456789abcdef12', 'vi', TRUE, 'completed', 'Sinh viên năm cuối ứng tuyển thực tập...', '{"name": "Hà Quang Sáng", "skills": ["Python"]}'::jsonb, NOW()),
('44444444-4444-4444-4444-444444444421', '33333333-3333-3333-3333-333333333321', 'CV Chu Ngọc Mai - UI Design Intern', 'cvs/2026/01/cv_mai_intern_ui.pdf', 'CV_ChuNgocMai_Intern.pdf', 'application/pdf', 110000, '4567890abcdef0123456789abcdef1234567890abcdef0123456789abcdef123', 'vi', TRUE, 'completed', 'Portfolio thiết kế giao diện Figma...', '{"name": "Chu Ngọc Mai", "skills": ["Figma"]}'::jsonb, NOW()),
('44444444-4444-4444-4444-444444444422', '33333333-3333-3333-3333-333333333322', 'CV Đoàn Nhật Quang - Tech Manager', 'cvs/2026/01/cv_quang_manager.pdf', 'CV_DoanNhatQuang_Manager.pdf', 'application/pdf', 280000, '567890abcdef0123456789abcdef1234567890abcdef0123456789abcdef1234', 'en', TRUE, 'completed', 'Executive Profile with 10 years experience...', '{"name": "Đoàn Nhật Quang", "skills": ["Engineering Management", "Agile", "Architecture"]}'::jsonb, NOW()),
('44444444-4444-4444-4444-444444444423', '33333333-3333-3333-3333-333333333323', 'CV Ngô Kiến Huy - Chief Technology Officer', 'cvs/2026/01/cv_huy_cto.pdf', 'CV_NgoKienHuy_CTO.pdf', 'application/pdf', 350000, '67890abcdef0123456789abcdef1234567890abcdef0123456789abcdef12345', 'en', TRUE, 'completed', 'CTO Profile with successful track record...', '{"name": "Ngô Kiến Huy", "skills": ["Strategic Leadership", "Scale-up"]}'::jsonb, NOW()),
('44444444-4444-4444-4444-444444444424', '33333333-3333-3333-3333-333333333324', 'CV Lý Tuấn Kiệt - Cybersecurity', 'cvs/2026/01/cv_kiet_security.pdf', 'CV_LyTuanKiet_Security.pdf', 'application/pdf', 195000, '7890abcdef0123456789abcdef1234567890abcdef0123456789abcdef123456', 'vi', TRUE, 'completed', 'Chuyên môn Pentest và An toàn thông tin...', '{"name": "Lý Tuấn Kiệt", "skills": ["Security", "Linux", "SOC"]}'::jsonb, NOW()),
('44444444-4444-4444-4444-444444444425', '33333333-3333-3333-3333-333333333325', 'CV Tống Ánh Tuyết - QA Automation', 'cvs/2026/01/cv_tuyet_qa.pdf', 'CV_TongAnhTuyet_QA.pdf', 'application/pdf', 160000, '890abcdef0123456789abcdef1234567890abcdef0123456789abcdef1234567', 'vi', TRUE, 'completed', 'Chuyên gia kiểm thử tự động Cypress & Selenium...', '{"name": "Tống Ánh Tuyết", "skills": ["QA Automation", "Python", "CI/CD"]}'::jsonb, NOW());

-- 13. CV Skills (Matching extracted skills from CVs)
INSERT INTO cv_skills (cv_id, skill_id, source, confidence, years_of_experience) VALUES
('44444444-4444-4444-4444-444444444410', 1, 'nlp', 0.98, 3.0),
('44444444-4444-4444-4444-444444444410', 3, 'nlp', 0.94, 3.0),
('44444444-4444-4444-4444-444444444410', 4, 'llm', 0.88, 2.0),
('44444444-4444-4444-4444-444444444411', 2, 'nlp', 0.96, 2.5),
('44444444-4444-4444-4444-444444444411', 14, 'nlp', 0.92, 2.0),
('44444444-4444-4444-4444-444444444411', 28, 'llm', 0.85, 1.5),
('44444444-4444-4444-4444-444444444412', 7, 'llm', 0.99, 7.0),
('44444444-4444-4444-4444-444444444412', 8, 'llm', 0.97, 6.0),
('44444444-4444-4444-4444-444444444412', 3, 'nlp', 0.95, 7.0),
('44444444-4444-4444-4444-444444444413', 4, 'nlp', 0.98, 4.5),
('44444444-4444-4444-4444-444444444413', 11, 'nlp', 0.96, 4.0),
('44444444-4444-4444-4444-444444444413', 15, 'llm', 0.92, 3.5),
('44444444-4444-4444-4444-444444444414', 10, 'nlp', 0.97, 3.5),
('44444444-4444-4444-4444-444444444415', 1, 'nlp', 0.99, 4.0),
('44444444-4444-4444-4444-444444444415', 22, 'llm', 0.94, 3.0),
('44444444-4444-4444-4444-444444444416', 13, 'nlp', 0.95, 3.0),
('44444444-4444-4444-4444-444444444416', 16, 'nlp', 0.91, 3.0),
('44444444-4444-4444-4444-444444444417', 6, 'nlp', 0.93, 2.5),
('44444444-4444-4444-4444-444444444417', 2, 'nlp', 0.92, 2.5),
('44444444-4444-4444-4444-444444444418', 7, 'nlp', 0.88, 0.5),
('44444444-4444-4444-4444-444444444419', 9, 'nlp', 0.86, 0.5),
('44444444-4444-4444-4444-444444444420', 1, 'nlp', 0.82, 0.0),
('44444444-4444-4444-4444-444444444421', 10, 'nlp', 0.85, 0.0),
('44444444-4444-4444-4444-444444444422', 12, 'llm', 0.95, 8.0),
('44444444-4444-4444-4444-444444444423', 19, 'llm', 0.97, 14.0),
('44444444-4444-4444-4444-444444444424', 29, 'nlp', 0.94, 4.0),
('44444444-4444-4444-4444-444444444425', 1, 'nlp', 0.91, 2.0);

-- 14. Jobs (16 Jobs across companies)
INSERT INTO jobs (id, company_id, created_by, title, slug, description, requirements, benefits, job_type, work_mode, level, min_years_experience, salary_min, salary_max, salary_currency, is_salary_negotiable, headcount, location_id, address, industry_id, deadline, status, published_at, view_count, application_count) VALUES
('55555555-5555-5555-5555-555555555501', '11111111-1111-1111-1111-111111111101', '00000000-0000-0000-0000-000000000002', 'Senior Python Backend Engineer', 'senior-python-backend-engineer', 'Phát triển kiến trúc backend microservices cho nền tảng điện toán đám mây.', 'Tối thiểu 3 năm kinh nghiệm Python, Django, PostgreSQL, Docker.', 'Lương thưởng cạnh tranh, BHXH đầy đủ, chế độ làm việc hybrid.', 'full_time', 'hybrid', 'staff', 3.0, 25000000, 40000000, 'VND', FALSE, 2, 1, 'Tầng 5, Tòa nhà A, Cầu Giấy, Hà Nội', 2, '2026-12-31', 'published', NOW(), 340, 3),
('55555555-5555-5555-5555-555555555502', '11111111-1111-1111-1111-111111111102', '00000000-0000-0000-0000-000000000003', 'Lead Java Architect (Fintech)', 'lead-java-architect-fintech', 'Chịu trách nhiệm kiến trúc hệ thống thanh toán cốt lõi xử lý triệu giao dịch/ngày.', 'Tối thiểu 6 năm kinh nghiệm Java/Spring Boot, Kafka, kiến trúc ngân hàng.', 'Gói phúc lợi cao cấp, thưởng KPI quý, hỗ trợ thiết bị làm việc.', 'full_time', 'onsite', 'supervisor', 6.0, 50000000, 80000000, 'VND', FALSE, 1, 2, 'Tầng 12, Tòa nhà Bitexco, Quận 1, TP.HCM', 3, '2026-12-31', 'published', NOW(), 410, 2),
('55555555-5555-5555-5555-555555555503', '11111111-1111-1111-1111-111111111103', '00000000-0000-0000-0000-000000000004', 'Senior AI / Machine Learning Engineer', 'senior-ai-machine-learning-engineer', 'Xây dựng và tối ưu mô hình học sâu (Deep Learning) phục vụ giải pháp nhận dạng thông minh.', 'Thành thạo Python, PyTorch/TensorFlow, kinh nghiệm triển khai production model.', 'Môi trường R&D chuyên nghiệp, tài trợ tham gia các hội nghị khoa học quốc tế.', 'full_time', 'hybrid', 'staff', 3.0, 35000000, 55000000, 'VND', FALSE, 2, 1, 'Tầng 8, Tòa Keangnam, Nam Từ Liêm, Hà Nội', 5, '2026-12-31', 'published', NOW(), 290, 2),
('55555555-5555-5555-5555-555555555504', '11111111-1111-1111-1111-111111111104', '00000000-0000-0000-0000-000000000005', 'Frontend React Developer (E-Commerce)', 'frontend-react-developer-ecom', 'Xây dựng giao diện sàn thương mại điện tử mượt mà trên desktop và mobile web.', 'Thành thạo ReactJS, TypeScript, Next.js, tư duy tối ưu hiệu năng web Core Web Vitals.', 'Thưởng doanh số cuối năm, giảm giá nội bộ khi mua sắm trên sàn.', 'full_time', 'remote', 'staff', 2.0, 20000000, 32000000, 'VND', FALSE, 3, 2, 'Tầng 3, Tòa nhà D, Quận 3, TP.HCM', 4, '2026-12-31', 'published', NOW(), 520, 3),
('55555555-5555-5555-5555-555555555505', '11111111-1111-1111-1111-111111111105', '00000000-0000-0000-0000-000000000006', 'Cloud DevOps & SRE Engineer', 'cloud-devops-sre-engineer', 'Xây dựng hạ tầng Cloud tự động hóa và duy trì độ sẵn sàng 99.99% cho khách hàng.', 'Kinh nghiệm sâu với Kubernetes, Terraform, AWS và giám sát hệ thống bằng Prometheus/Grafana.', 'Thưởng chứng chỉ công nghệ AWS/CKA, làm việc từ xa 100%.', 'full_time', 'remote', 'staff', 3.0, 28000000, 48000000, 'VND', FALSE, 2, 3, 'Công viên Phần mềm Đà Nẵng, Hải Châu, Đà Nẵng', 1, '2026-12-31', 'published', NOW(), 215, 2),
('55555555-5555-5555-5555-555555555506', '11111111-1111-1111-1111-111111111106', '00000000-0000-0000-0000-000000000007', 'Chuyên viên An toàn Thông tin (Pentester)', 'chuyen-vien-an-toan-thong-tin-pentest', 'Thực hiện kiểm thử xâm nhập (Penetration Testing) ứng dụng web và hệ thống máy chủ.', 'Kinh nghiệm đánh giá lỗ hổng bảo mật, sử dụng thành thạo Burp Suite, Nmap, Metasploit.', 'Phụ cấp dự án pentest đặc thù, đào tạo các chứng chỉ bảo mật cao cấp.', 'full_time', 'onsite', 'staff', 2.0, 22000000, 38000000, 'VND', FALSE, 2, 1, 'Tòa CMC Tower, Cầu Giấy, Hà Nội', 8, '2026-12-31', 'published', NOW(), 160, 1),
('55555555-5555-5555-5555-555555555507', '11111111-1111-1111-1111-111111111107', '00000000-0000-0000-0000-000000000008', 'Golang Backend Developer (Logistics Platform)', 'golang-backend-developer-logistics', 'Phát triển backend định tuyến vận chuyển tức thì cho hệ thống điều phối thông minh.', 'Tối thiểu 2 năm Go/Golang, hiểu biết về Message Queue (Kafka/RabbitMQ) và gRPC.', 'Môi trường làm việc trẻ trung, du lịch hàng năm, phụ cấp cơm trưa.', 'full_time', 'hybrid', 'staff', 2.0, 22000000, 36000000, 'VND', FALSE, 2, 2, 'Khu Công nghệ cao Quận 9, TP. Thủ Đức, TP.HCM', 9, '2026-12-31', 'published', NOW(), 185, 1),
('55555555-5555-5555-5555-555555555508', '11111111-1111-1111-1111-111111111108', '00000000-0000-0000-0000-000000000009', 'Senior UI/UX Product Designer', 'senior-ui-ux-product-designer', 'Chịu trách nhiệm thiết kế trải nghiệm người dùng cho ứng dụng học tập trực tuyến EdTech.', 'Thành thạo Figma, xây dựng Design System, kinh nghiệm phỏng vấn người dùng.', 'Môi trường giáo dục nhân văn, thời gian làm việc linh hoạt, thưởng hiệu quả.', 'full_time', 'hybrid', 'staff', 3.0, 20000000, 35000000, 'VND', FALSE, 1, 1, 'Tầng 4, Tòa Hapulico, Thanh Xuân, Hà Nội', 10, '2026-12-31', 'published', NOW(), 230, 2),
('55555555-5555-5555-5555-555555555509', '11111111-1111-1111-1111-111111111101', '00000000-0000-0000-0000-000000000002', 'Fresher Java Backend Developer', 'fresher-java-backend-developer', 'Tham gia dự án đào tạo và làm việc thực tế với Java Spring Boot cho thị trường nước ngoài.', 'Nắm chắc kiến thức OOP, SQL, Java Core. Ưu tiên có điểm GPA khá/giỏi.', 'Được mentor kèm 1:1, lộ trình thăng tiến rõ ràng lên Junior sau 6 tháng.', 'full_time', 'onsite', 'fresher', 0.0, 8000000, 13000000, 'VND', FALSE, 5, 1, 'Tầng 5, Tòa nhà A, Cầu Giấy, Hà Nội', 2, '2026-12-31', 'published', NOW(), 450, 1),
('55555555-5555-5555-5555-555555555510', '11111111-1111-1111-1111-111111111104', '00000000-0000-0000-0000-000000000005', 'Fresher Frontend Developer (VueJS)', 'fresher-frontend-developer-vue', 'Phát triển các module giao diện quản trị Admin portal phục vụ người bán hàng.', 'Hiểu biết căn bản về VueJS, HTML5, CSS3, JavaScript ES6.', 'Trợ cấp ăn trưa, đào tạo bài bản từ các Senior Frontend Kỹ sư.', 'full_time', 'hybrid', 'fresher', 0.0, 9000000, 14000000, 'VND', FALSE, 4, 2, 'Tầng 3, Tòa nhà D, Quận 3, TP.HCM', 4, '2026-12-31', 'published', NOW(), 310, 1),
('55555555-5555-5555-5555-555555555511', '11111111-1111-1111-1111-111111111103', '00000000-0000-0000-0000-000000000004', 'Thực tập sinh Python / AI Intern', 'thuc-tap-sinh-python-ai-intern', 'Hỗ trợ thu thập, gán nhãn dữ liệu và thử nghiệm các mô hình AI mã nguồn mở.', 'Sinh viên năm 3, 4 chuyên ngành CNTT, Toán - Tin, biết lập trình Python cơ bản.', 'Hỗ trợ dấu thực tập tốt nghiệp, phụ cấp thực tập cạnh tranh, cơ hội lên chính thức.', 'internship', 'onsite', 'intern', 0.0, 3500000, 6000000, 'VND', FALSE, 4, 1, 'Tầng 8, Tòa Keangnam, Nam Từ Liêm, Hà Nội', 5, '2026-12-31', 'published', NOW(), 380, 1),
('55555555-5555-5555-5555-555555555512', '11111111-1111-1111-1111-111111111108', '00000000-0000-0000-0000-000000000009', 'Thực tập sinh Thiết kế UI/UX', 'thuc-tap-sinh-thiet-ke-ui-ux', 'Hỗ trợ đội ngũ Product tạo wireframe, icon và chuẩn bị hình ảnh minh họa cho app.', 'Có sản phẩm thiết kế mẫu cá nhân bằng Figma, tư duy thẩm mỹ hiện đại.', 'Được hướng dẫn bởi Lead Designer, nhận trợ cấp thực tập hàng tháng.', 'internship', 'hybrid', 'intern', 0.0, 3000000, 5000000, 'VND', FALSE, 2, 1, 'Tầng 4, Tòa Hapulico, Thanh Xuân, Hà Nội', 10, '2026-12-31', 'published', NOW(), 210, 1),
('55555555-5555-5555-5555-555555555513', '11111111-1111-1111-1111-111111111102', '00000000-0000-0000-0000-000000000003', 'Engineering Manager (Head of Core Banking)', 'engineering-manager-head-of-core', 'Quản lý 3 đội kỹ thuật (Backend, Frontend, DevOps) phát triển hệ thống lõi ngân hàng.', '10+ năm kinh nghiệm kỹ thuật, ít nhất 3 năm ở vị trí Manager, khả năng lãnh đạo xuất sắc.', 'Lương cạnh tranh top thị trường, thưởng cổ phiếu ESOP, gói bảo hiểm toàn diện cho gia đình.', 'full_time', 'hybrid', 'manager', 8.0, 70000000, 110000000, 'VND', FALSE, 1, 2, 'Tầng 12, Tòa nhà Bitexco, Quận 1, TP.HCM', 3, '2026-12-31', 'published', NOW(), 280, 1),
('55555555-5555-5555-5555-555555555514', '11111111-1111-1111-1111-111111111105', '00000000-0000-0000-0000-000000000006', 'Giám đốc Công nghệ (CTO)', 'giam-doc-cong-nghe-cto-cloudscale', 'Định hướng toàn bộ lộ trình phát triển hạ tầng mạng viễn thông đám mây của doanh nghiệp.', 'Từng giữ vị trí Tech Director/CTO tại các công ty công nghệ lớn, có tầm nhìn chiến lược sâu rộng.', 'Thu nhập thỏa thuận xứng tầm, cổ phần sở hữu tại công ty.', 'full_time', 'hybrid', 'director', 12.0, 110000000, 180000000, 'VND', TRUE, 1, 3, 'Công viên Phần mềm Đà Nẵng, Hải Châu, Đà Nẵng', 1, '2026-12-31', 'published', NOW(), 390, 1),
('55555555-5555-5555-5555-555555555515', '11111111-1111-1111-1111-111111111107', '00000000-0000-0000-0000-000000000008', 'Senior QA Automation Engineer', 'senior-qa-automation-engineer', 'Xây dựng framework kiểm thử tự động cho hệ thống tracking xe tải và kho bãi.', 'Tối thiểu 3 năm kinh nghiệm Automation Test (Selenium/Cypress), lập trình Python hoặc Java.', 'Thưởng dự án định kỳ, môi trường ổn định, cơ hội học hỏi hệ thống IoT.', 'full_time', 'hybrid', 'staff', 3.0, 20000000, 32000000, 'VND', FALSE, 2, 2, 'Khu Công nghệ cao Quận 9, TP. Thủ Đức, TP.HCM', 9, '2026-12-31', 'published', NOW(), 145, 1),
('55555555-5555-5555-5555-555555555516', '11111111-1111-1111-1111-111111111104', '00000000-0000-0000-0000-000000000005', 'Fullstack Web Engineer (NodeJS + React)', 'fullstack-web-engineer-ecom', 'Tham gia phát triển hệ thống live-streaming bán hàng trực tiếp trên sàn.', 'Kinh nghiệm với NodeJS, WebSocket, ReactJS và kiến trúc chịu tải phân tán.', 'Thưởng doanh thu stream, môi trường trẻ trung, cởi mở.', 'full_time', 'hybrid', 'staff', 2.5, 22000000, 35000000, 'VND', FALSE, 2, 2, 'Tầng 3, Tòa nhà D, Quận 3, TP.HCM', 4, '2026-12-31', 'published', NOW(), 270, 1);

-- 15. Job Skills (Skills required for jobs)
INSERT INTO job_skills (job_id, skill_id, is_required, min_years, weight) VALUES
('55555555-5555-5555-5555-555555555501', 1, TRUE, 3.0, 5),
('55555555-5555-5555-5555-555555555501', 3, TRUE, 2.0, 4),
('55555555-5555-5555-5555-555555555501', 4, FALSE, 1.0, 3),
('55555555-5555-5555-5555-555555555502', 7, TRUE, 6.0, 5),
('55555555-5555-5555-5555-555555555502', 8, TRUE, 5.0, 5),
('55555555-5555-5555-5555-555555555502', 3, TRUE, 4.0, 4),
('55555555-5555-5555-5555-555555555503', 1, TRUE, 3.0, 5),
('55555555-5555-5555-5555-555555555503', 23, TRUE, 2.0, 5),
('55555555-5555-5555-5555-555555555503', 22, FALSE, 2.0, 3),
('55555555-5555-5555-5555-555555555504', 2, TRUE, 2.0, 5),
('55555555-5555-5555-5555-555555555504', 14, TRUE, 2.0, 4),
('55555555-5555-5555-5555-555555555504', 28, FALSE, 1.0, 3),
('55555555-5555-5555-5555-555555555505', 4, TRUE, 3.0, 5),
('55555555-5555-5555-5555-555555555505', 11, TRUE, 3.0, 5),
('55555555-5555-5555-5555-555555555505', 15, TRUE, 2.0, 4),
('55555555-5555-5555-5555-555555555506', 29, TRUE, 2.0, 5),
('55555555-5555-5555-5555-555555555506', 8, FALSE, 1.0, 3),
('55555555-5555-5555-5555-555555555507', 13, TRUE, 2.0, 5),
('55555555-5555-5555-5555-555555555507', 16, TRUE, 2.0, 4),
('55555555-5555-5555-5555-555555555508', 10, TRUE, 3.0, 5),
('55555555-5555-5555-5555-555555555509', 7, TRUE, 0.0, 5),
('55555555-5555-5555-5555-555555555509', 8, FALSE, 0.0, 3),
('55555555-5555-5555-5555-555555555510', 9, TRUE, 0.0, 5),
('55555555-5555-5555-5555-555555555511', 1, TRUE, 0.0, 5),
('55555555-5555-5555-5555-555555555512', 10, TRUE, 0.0, 5),
('55555555-5555-5555-5555-555555555513', 12, TRUE, 8.0, 5),
('55555555-5555-5555-5555-555555555513', 18, TRUE, 8.0, 5),
('55555555-5555-5555-5555-555555555514', 19, TRUE, 12.0, 5),
('55555555-5555-5555-5555-555555555515', 1, TRUE, 2.0, 4),
('55555555-5555-5555-5555-555555555515', 21, TRUE, 2.0, 4),
('55555555-5555-5555-5555-555555555516', 6, TRUE, 2.5, 5),
('55555555-5555-5555-5555-555555555516', 2, TRUE, 2.0, 4);

-- 16. Favorite Jobs (12 records)
INSERT INTO favorite_jobs (candidate_id, job_id) VALUES
('33333333-3333-3333-3333-333333333310', '55555555-5555-5555-5555-555555555501'),
('33333333-3333-3333-3333-333333333310', '55555555-5555-5555-5555-555555555503'),
('33333333-3333-3333-3333-333333333311', '55555555-5555-5555-5555-555555555504'),
('33333333-3333-3333-3333-333333333312', '55555555-5555-5555-5555-555555555502'),
('33333333-3333-3333-3333-333333333313', '55555555-5555-5555-5555-555555555505'),
('33333333-3333-3333-3333-333333333314', '55555555-5555-5555-5555-555555555508'),
('33333333-3333-3333-3333-333333333315', '55555555-5555-5555-5555-555555555503'),
('33333333-3333-3333-3333-333333333316', '55555555-5555-5555-5555-555555555507'),
('33333333-3333-3333-3333-333333333317', '55555555-5555-5555-5555-555555555516'),
('33333333-3333-3333-3333-333333333318', '55555555-5555-5555-5555-555555555509'),
('33333333-3333-3333-3333-333333333322', '55555555-5555-5555-5555-555555555513'),
('33333333-3333-3333-3333-333333333324', '55555555-5555-5555-5555-555555555506');

-- 17. Favorite Companies (10 records)
INSERT INTO favorite_companies (candidate_id, company_id) VALUES
('33333333-3333-3333-3333-333333333310', '11111111-1111-1111-1111-111111111101'),
('33333333-3333-3333-3333-333333333310', '11111111-1111-1111-1111-111111111103'),
('33333333-3333-3333-3333-333333333311', '11111111-1111-1111-1111-111111111104'),
('33333333-3333-3333-3333-333333333312', '11111111-1111-1111-1111-111111111102'),
('33333333-3333-3333-3333-333333333313', '11111111-1111-1111-1111-111111111105'),
('33333333-3333-3333-3333-333333333314', '11111111-1111-1111-1111-111111111108'),
('33333333-3333-3333-3333-333333333315', '11111111-1111-1111-1111-111111111103'),
('33333333-3333-3333-3333-333333333316', '11111111-1111-1111-1111-111111111107'),
('33333333-3333-3333-3333-333333333322', '11111111-1111-1111-1111-111111111102'),
('33333333-3333-3333-3333-333333333323', '11111111-1111-1111-1111-111111111105');

-- 18. Applications (20 Applications)
INSERT INTO applications (id, job_id, candidate_id, cv_id, cover_letter, status, recruiter_rating, status_changed_at) VALUES
('66666666-6666-6666-6666-666666666601', '55555555-5555-5555-5555-555555555501', '33333333-3333-3333-3333-333333333310', '44444444-4444-4444-4444-444444444410', 'Tôi mong muốn đóng góp kinh nghiệm Python và tối ưu dữ liệu cho hệ thống của công ty.', 'interview', 4, NOW()),
('66666666-6666-6666-6666-666666666602', '55555555-5555-5555-5555-555555555502', '33333333-3333-3333-3333-333333333312', '44444444-4444-4444-4444-444444444412', 'Với 7 năm kinh nghiệm kiến trúc ngân hàng, tôi tự tin đáp ứng tốt các tiêu chuẩn khắt khe nhất.', 'offer', 5, NOW()),
('66666666-6666-6666-6666-666666666603', '55555555-5555-5555-5555-555555555503', '33333333-3333-3333-3333-333333333315', '44444444-4444-4444-4444-444444444415', 'Tôi có các công bố nghiên cứu về nhận diện đối tượng và mong muốn ứng dụng tại AI Solutions.', 'screening', 4, NOW()),
('66666666-6666-6666-6666-666666666604', '55555555-5555-5555-5555-555555555504', '33333333-3333-3333-3333-333333333311', '44444444-4444-4444-4444-444444444411', 'Tôi rất ấn tượng với tốc độ phát triển của E-Commerce Stars và mong muốn phụ trách mảng giao diện.', 'interview', 4, NOW()),
('66666666-6666-6666-6666-666666666605', '55555555-5555-5555-5555-555555555505', '33333333-3333-3333-3333-333333333313', '44444444-4444-4444-4444-444444444413', 'Thế mạnh của tôi là tự động hóa hạ tầng và giải quyết nghẽn cổ chai Kubernetes.', 'hired', 5, NOW()),
('66666666-6666-6666-6666-666666666606', '55555555-5555-5555-5555-555555555506', '33333333-3333-3333-3333-333333333324', '44444444-4444-4444-4444-444444444424', 'Tôi muốn gia nhập đội ngũ pentest chuyên nghiệp để bảo vệ hệ thống trước các mối đe dọa.', 'screening', 3, NOW()),
('66666666-6666-6666-6666-666666666607', '55555555-5555-5555-5555-555555555507', '33333333-3333-3333-3333-333333333316', '44444444-4444-4444-4444-444444444416', 'Kinh nghiệm Golang và gRPC của tôi phù hợp hoàn toàn với định hướng của LogiSmart.', 'applied', NULL, NOW()),
('66666666-6666-6666-6666-666666666608', '55555555-5555-5555-5555-555555555508', '33333333-3333-3333-3333-333333333314', '44444444-4444-4444-4444-444444444414', 'Tôi đam mê xây dựng giao diện ứng dụng học tập trực quan và truyền cảm hứng.', 'interview', 4, NOW()),
('66666666-6666-6666-6666-666666666609', '55555555-5555-5555-5555-555555555509', '33333333-3333-3333-3333-333333333318', '44444444-4444-4444-4444-444444444418', 'Em là sinh viên mới ra trường và rất mong muốn được đào tạo tại TechCorp.', 'applied', 3, NOW()),
('66666666-6666-6666-6666-666666666610', '55555555-5555-5555-5555-555555555510', '33333333-3333-3333-3333-333333333319', '44444444-4444-4444-4444-444444444419', 'Em yêu thích làm giao diện người dùng và muốn cống hiến cho mảng thương mại điện tử.', 'screening', 3, NOW()),
('66666666-6666-6666-6666-666666666611', '55555555-5555-5555-5555-555555555511', '33333333-3333-3333-3333-333333333320', '44444444-4444-4444-4444-444444444420', 'Em nộp đơn xin thực tập vị trí AI Intern.', 'applied', NULL, NOW()),
('66666666-6666-6666-6666-666666666612', '55555555-5555-5555-5555-555555555512', '33333333-3333-3333-3333-333333333321', '44444444-4444-4444-4444-444444444421', 'Em mong muốn được thực tập thiết kế UI/UX tại EdTech.', 'screening', 3, NOW()),
('66666666-6666-6666-6666-666666666613', '55555555-5555-5555-5555-555555555513', '33333333-3333-3333-3333-333333333322', '44444444-4444-4444-4444-444444444422', 'Tôi mong muốn nhận trách nhiệm dẫn dắt khối kỹ thuật tại FinTech Global.', 'interview', 5, NOW()),
('66666666-6666-6666-6666-666666666614', '55555555-5555-5555-5555-555555555514', '33333333-3333-3333-3333-333333333323', '44444444-4444-4444-4444-444444444423', 'Trao đổi chiến lược vị trí CTO cho CloudScale Networks.', 'screening', 5, NOW()),
('66666666-6666-6666-6666-666666666615', '55555555-5555-5555-5555-555555555515', '33333333-3333-3333-3333-333333333325', '44444444-4444-4444-4444-444444444425', 'Tôi có 3.5 năm kinh nghiệm xây dựng hệ thống kiểm thử tự động toàn diện.', 'offer', 4, NOW()),
('66666666-6666-6666-6666-666666666616', '55555555-5555-5555-5555-555555555516', '33333333-3333-3333-3333-333333333317', '44444444-4444-4444-4444-444444444417', 'Kỹ năng Node.js và React của tôi có thể đáp ứng tốt tính năng live streaming.', 'interview', 4, NOW()),
('66666666-6666-6666-6666-666666666617', '55555555-5555-5555-5555-555555555501', '33333333-3333-3333-3333-333333333315', '44444444-4444-4444-4444-444444444415', 'Ứng tuyển mở rộng sang vị trí Backend Engineer.', 'rejected', 2, NOW()),
('66666666-6666-6666-6666-666666666618', '55555555-5555-5555-5555-555555555504', '33333333-3333-3333-3333-333333333317', '44444444-4444-4444-4444-444444444417', 'Ứng tuyển thử sức thêm vị trí Frontend.', 'withdrawn', NULL, NOW()),
('66666666-6666-6666-6666-666666666619', '55555555-5555-5555-5555-555555555505', '33333333-3333-3333-3333-333333333310', '44444444-4444-4444-4444-444444444410', 'Tìm hiểu thêm về mảng DevOps.', 'rejected', 2, NOW()),
('66666666-6666-6666-6666-666666666620', '55555555-5555-5555-5555-555555555503', '33333333-3333-3333-3333-333333333310', '44444444-4444-4444-4444-444444444410', 'Ứng tuyển mảng Data Backend cho dự án AI.', 'screening', 3, NOW());

-- 19. Application Status History (Historical records)
INSERT INTO application_status_history (application_id, from_status, to_status, changed_by, note) VALUES
('66666666-6666-6666-6666-666666666601', NULL, 'applied', '00000000-0000-0000-0000-000000000010', 'Ứng viên nộp hồ sơ'),
('66666666-6666-6666-6666-666666666601', 'applied', 'screening', '00000000-0000-0000-0000-000000000002', 'Hồ sơ đạt yêu cầu cơ bản'),
('66666666-6666-6666-6666-666666666601', 'screening', 'interview', '00000000-0000-0000-0000-000000000002', 'Gửi lời mời phỏng vấn kỹ thuật'),
('66666666-6666-6666-6666-666666666602', NULL, 'applied', '00000000-0000-0000-0000-000000000012', 'Nộp hồ sơ trực tuyến'),
('66666666-6666-6666-6666-666666666602', 'applied', 'interview', '00000000-0000-0000-0000-000000000003', 'Phỏng vấn trực tiếp với Giám đốc kỹ thuật'),
('66666666-6666-6666-6666-666666666602', 'interview', 'offer', '00000000-0000-0000-0000-000000000003', 'Ứng viên xuất sắc, phát hành thư mời nhận việc'),
('66666666-6666-6666-6666-666666666605', NULL, 'applied', '00000000-0000-0000-0000-000000000013', 'Nộp hồ sơ vị trí DevOps'),
('66666666-6666-6666-6666-666666666605', 'applied', 'interview', '00000000-0000-0000-0000-000000000006', 'Phỏng vấn kiểm tra kiến thức hạ tầng'),
('66666666-6666-6666-6666-666666666605', 'interview', 'offer', '00000000-0000-0000-0000-000000000006', 'Gửi offer thành công'),
('66666666-6666-6666-6666-666666666605', 'offer', 'hired', '00000000-0000-0000-0000-000000000006', 'Ứng viên đồng ý nhận việc');

-- 20. Interviews (10 Interviews)
INSERT INTO interviews (id, application_id, round, title, scheduled_at, duration_minutes, mode, location, meeting_url, interviewer_id, status, result, rating, feedback, created_by) VALUES
('77777777-7777-7777-7777-777777777701', '66666666-6666-6666-6666-666666666601', 1, 'Phỏng vấn Kỹ thuật Backend Python', NOW() + INTERVAL '1 day', 60, 'online', NULL, 'https://meet.google.com/abc-defg-hij', '00000000-0000-0000-0000-000000000002', 'scheduled', 'pending', NULL, NULL, '00000000-0000-0000-0000-000000000002'),
('77777777-7777-7777-7777-777777777702', '66666666-6666-6666-6666-666666666602', 1, 'Phỏng vấn Kiến trúc Giải pháp Java', NOW() - INTERVAL '2 days', 90, 'offline', 'Tầng 12, Bitexco, Q1, TP.HCM', NULL, '00000000-0000-0000-0000-000000000003', 'completed', 'passed', 5, 'Chuyên môn sâu rộng, nắm vững hệ thống phân tán chịu tải.', '00000000-0000-0000-0000-000000000003'),
('77777777-7777-7777-7777-777777777703', '66666666-6666-6666-6666-666666666604', 1, 'Phỏng vấn Chuyên môn Frontend React', NOW() + INTERVAL '3 days', 60, 'online', NULL, 'https://meet.google.com/fe-react-interview', '00000000-0000-0000-0000-000000000005', 'scheduled', 'pending', NULL, NULL, '00000000-0000-0000-0000-000000000005'),
('77777777-7777-7777-7777-777777777704', '66666666-6666-6666-6666-666666666605', 1, 'Phỏng vấn DevOps & Hạ tầng Đám mây', NOW() - INTERVAL '5 days', 60, 'online', NULL, 'https://meet.google.com/devops-sre-round1', '00000000-0000-0000-0000-000000000006', 'completed', 'passed', 5, 'Thành thạo Kubernetes và CI/CD thực tế.', '00000000-0000-0000-0000-000000000006'),
('77777777-7777-7777-7777-777777777705', '66666666-6666-6666-6666-666666666608', 1, 'Đánh giá Portfolio & Trải nghiệm UI/UX', NOW() + INTERVAL '2 days', 45, 'online', NULL, 'https://meet.google.com/uiux-design-review', '00000000-0000-0000-0000-000000000009', 'scheduled', 'pending', NULL, NULL, '00000000-0000-0000-0000-000000000009'),
('77777777-7777-7777-7777-777777777706', '66666666-6666-6666-6666-666666666613', 1, 'Phỏng vấn Năng lực Quản lý Kỹ thuật', NOW() - INTERVAL '1 day', 90, 'offline', 'Tầng 12, Bitexco, Q1, TP.HCM', NULL, '00000000-0000-0000-0000-000000000003', 'completed', 'passed', 5, 'Kinh nghiệm quản lý xuất sắc, phong thái đĩnh đạc.', '00000000-0000-0000-0000-000000000003'),
('77777777-7777-7777-7777-777777777707', '66666666-6666-6666-6666-666666666615', 1, 'Kiểm tra Năng lực Tự động hóa QA', NOW() - INTERVAL '4 days', 60, 'online', NULL, 'https://meet.google.com/qa-automation-check', '00000000-0000-0000-0000-000000000008', 'completed', 'passed', 4, 'Viết test case và framework chuẩn chỉ.', '00000000-0000-0000-0000-000000000008'),
('77777777-7777-7777-7777-777777777708', '66666666-6666-6666-6666-666666666616', 1, 'Phỏng vấn Fullstack Web Engineer', NOW() + INTERVAL '4 days', 60, 'online', NULL, 'https://meet.google.com/fullstack-engineer', '00000000-0000-0000-0000-000000000005', 'scheduled', 'pending', NULL, NULL, '00000000-0000-0000-0000-000000000005'),
('77777777-7777-7777-7777-777777777709', '66666666-6666-6666-6666-666666666617', 1, 'Phỏng vấn Sàng lọc Backend', NOW() - INTERVAL '7 days', 30, 'phone', NULL, NULL, '00000000-0000-0000-0000-000000000002', 'completed', 'failed', 2, 'Kỹ năng chưa phù hợp với yêu cầu Senior.', '00000000-0000-0000-0000-000000000002'),
('77777777-7777-7777-7777-777777777710', '66666666-6666-6666-6666-666666666619', 1, 'Phỏng vấn Trao đổi định hướng', NOW() - INTERVAL '6 days', 30, 'phone', NULL, NULL, '00000000-0000-0000-0000-000000000006', 'completed', 'failed', 2, 'Thiếu kinh nghiệm hạ tầng thực tế.', '00000000-0000-0000-0000-000000000006');

-- 21. CV Analyses (11 Records)
INSERT INTO cv_analyses (id, cv_id, status, overall_score, section_scores, strengths, weaknesses, summary, detected_level, provider, model_name, prompt_version) VALUES
('99999999-9999-9999-9999-999999999910', '44444444-4444-4444-4444-444444444410', 'completed', 88, '{"skills": 92, "education": 85, "experience": 88}'::jsonb, '["3 năm kinh nghiệm Python/PostgreSQL vững chắc", "Đã từng làm việc với kiến trúc microservices"]'::jsonb, '["Cần bổ sung chứng chỉ cloud quốc tế"]'::jsonb, 'CV trình bày rõ ràng, chuẩn cấu trúc kỹ thuật cho vị trí Backend.', 'staff', 'openai', 'gpt-4o', 'v1.0'),
('99999999-9999-9999-9999-999999999911', '44444444-4444-4444-4444-444444444411', 'completed', 85, '{"skills": 88, "education": 82, "experience": 85}'::jsonb, '["Kỹ năng ReactJS và TypeScript tốt", "Có kinh nghiệm Next.js hiện đại"]'::jsonb, '["Chưa nêu rõ hiệu quả tối ưu Core Web Vitals"]'::jsonb, 'Hồ sơ phù hợp tốt với các vị trí Frontend Web hiện đại.', 'staff', 'openai', 'gpt-4o', 'v1.0'),
('99999999-9999-9999-9999-999999999912', '44444444-4444-4444-4444-444444444412', 'completed', 96, '{"skills": 98, "education": 95, "experience": 97}'::jsonb, '["7 năm kinh nghiệm hệ thống ngân hàng", "Thành thạo kiến trúc phân tán"]'::jsonb, '[]'::jsonb, 'Hồ sơ chuyên gia cấp cao, đáp ứng mọi tiêu chuẩn khắt khe.', 'supervisor', 'openai', 'gpt-4o', 'v1.0'),
('99999999-9999-9999-9999-999999999913', '44444444-4444-4444-4444-444444444413', 'completed', 92, '{"skills": 95, "education": 85, "experience": 94}'::jsonb, '["Kinh nghiệm thực chiến với Kubernetes và hạ tầng AWS", "Tự động hóa CI/CD tốt"]'::jsonb, '["Nên bổ sung chứng chỉ CKA/CKS"]'::jsonb, 'Hồ sơ DevOps chất lượng cao, rất phù hợp môi trường cloud-native.', 'staff', 'openai', 'gpt-4o', 'v1.0'),
('99999999-9999-9999-9999-999999999914', '44444444-4444-4444-4444-444444444414', 'completed', 89, '{"skills": 92, "education": 88, "experience": 87}'::jsonb, '["Portfolio thiết kế đẹp, chỉn chu", "Nắm vững nguyên lý xây dựng Design System"]'::jsonb, '["Cần thêm số liệu tác động kinh doanh của sản phẩm"]'::jsonb, 'Hồ sơ Product Designer sáng giá.', 'staff', 'openai', 'gpt-4o', 'v1.0'),
('99999999-9999-9999-9999-999999999915', '44444444-4444-4444-4444-444444444415', 'completed', 94, '{"skills": 96, "education": 94, "experience": 92}'::jsonb, '["Nền tảng toán học và khoa học máy tính vững", "Kinh nghiệm thực tế với PyTorch và Vision"]'::jsonb, '[]'::jsonb, 'Kỹ sư AI có trình độ nghiên cứu và ứng dụng cao.', 'staff', 'openai', 'gpt-4o', 'v1.0'),
('99999999-9999-9999-9999-999999999916', '44444444-4444-4444-4444-444444444416', 'completed', 87, '{"skills": 90, "education": 85, "experience": 86}'::jsonb, '["Kỹ năng Go và gRPC thực chiến", "Hiểu rõ về xử lý đồng thời (Concurrency)"]'::jsonb, '["Chưa có nhiều kinh nghiệm về hạ tầng cloud"]'::jsonb, 'Hồ sơ Backend Go tốt cho hệ thống tải cao.', 'staff', 'openai', 'gpt-4o', 'v1.0'),
('99999999-9999-9999-9999-999999999917', '44444444-4444-4444-4444-444444444417', 'completed', 83, '{"skills": 85, "education": 80, "experience": 84}'::jsonb, '["Đảm nhiệm cả Frontend và Backend", "Tích hợp API thanh toán nhanh chóng"]'::jsonb, '["Cần nâng cao kiến thức tối ưu cơ sở dữ liệu lớn"]'::jsonb, 'Ứng viên Fullstack năng động, phù hợp startup.', 'staff', 'openai', 'gpt-4o', 'v1.0'),
('99999999-9999-9999-9999-999999999918', '44444444-4444-4444-4444-444444444418', 'completed', 78, '{"skills": 76, "education": 85, "experience": 72}'::jsonb, '["GPA tốt, nắm chắc lý thuyết Java Core"]'::jsonb, '["Chưa có kinh nghiệm thực chiến dự án lớn"]'::jsonb, 'Fresher tiềm năng cho các chương trình ươm mầm tài năng.', 'fresher', 'openai', 'gpt-4o', 'v1.0'),
('99999999-9999-9999-9999-999999999922', '44444444-4444-4444-4444-444444444422', 'completed', 98, '{"skills": 99, "education": 96, "experience": 99}'::jsonb, '["10 năm kinh nghiệm dẫn dắt đội ngũ kỹ thuật", "Tư duy chiến lược và quản trị Agile chuẩn xác"]'::jsonb, '[]'::jsonb, 'Hồ sơ lãnh đạo công nghệ xuất sắc.', 'manager', 'openai', 'gpt-4o', 'v1.0'),
('99999999-9999-9999-9999-999999999924', '44444444-4444-4444-4444-444444444424', 'completed', 90, '{"skills": 92, "education": 86, "experience": 91}'::jsonb, '["Nắm vững các kỹ thuật rà quét và pentest", "Chứng chỉ CEH chuẩn quốc tế"]'::jsonb, '["Cần tăng cường kỹ năng báo cáo cho ban điều hành"]'::jsonb, 'Chuyên gia an ninh mạng thực chiến.', 'staff', 'openai', 'gpt-4o', 'v1.0');

-- 22. CV Suggestions (10 Suggestions)
INSERT INTO cv_suggestions (id, cv_id, job_id, analysis_id, status, suggestions, provider, model_name, prompt_version) VALUES
('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaa01', '44444444-4444-4444-4444-444444444410', '55555555-5555-5555-5555-555555555501', '99999999-9999-9999-9999-999999999910', 'completed', '[{"section": "experience", "issue": "Chưa nêu số lượng người dùng đồng thời (CCU)", "suggestion": "Bổ sung số liệu lưu lượng truy cập hệ thống đã chịu tải", "priority": "high"}]'::jsonb, 'openai', 'gpt-4o', 'v1.0'),
('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaa02', '44444444-4444-4444-4444-444444444411', '55555555-5555-5555-5555-555555555504', '99999999-9999-9999-9999-999999999911', 'completed', '[{"section": "projects", "issue": "Thiếu minh chứng tối ưu SEO và tốc độ tải trang", "suggestion": "Thêm kết quả kiểm tra Google Lighthouse", "priority": "medium"}]'::jsonb, 'openai', 'gpt-4o', 'v1.0'),
('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaa03', '44444444-4444-4444-4444-444444444413', '55555555-5555-5555-5555-555555555505', '99999999-9999-9999-9999-999999999913', 'completed', '[{"section": "skills", "issue": "Chưa liệt kê cụ thể các công cụ quan sát (Observability)", "suggestion": "Liệt kê Prometheus, Grafana, Datadog nếu có", "priority": "medium"}]'::jsonb, 'openai', 'gpt-4o', 'v1.0'),
('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaa04', '44444444-4444-4444-4444-444444444414', '55555555-5555-5555-5555-555555555508', '99999999-9999-9999-9999-999999999914', 'completed', '[{"section": "summary", "issue": "Phần tóm tắt chưa nổi bật thế mạnh thiết kế EdTech", "suggestion": "Nhấn mạnh kinh nghiệm thiết kế ứng dụng cho học sinh/sinh viên", "priority": "high"}]'::jsonb, 'openai', 'gpt-4o', 'v1.0'),
('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaa05', '44444444-4444-4444-4444-444444444415', '55555555-5555-5555-5555-555555555503', '99999999-9999-9999-9999-999999999915', 'completed', '[{"section": "experience", "issue": "Chưa mô tả kích thước tập dữ liệu đã huấn luyện", "suggestion": "Ghi rõ số lượng mẫu ảnh/video và độ chính xác mAP đạt được", "priority": "high"}]'::jsonb, 'openai', 'gpt-4o', 'v1.0'),
('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaa06', '44444444-4444-4444-4444-444444444416', '55555555-5555-5555-5555-555555555507', '99999999-9999-9999-9999-999999999916', 'completed', '[{"section": "skills", "issue": "Chưa đề cập tới các cơ chế caching phân tán", "suggestion": "Nêu rõ kinh nghiệm với Redis Cluster", "priority": "low"}]'::jsonb, 'openai', 'gpt-4o', 'v1.0'),
('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaa07', '44444444-4444-4444-4444-444444444417', '55555555-5555-5555-5555-555555555516', '99999999-9999-9999-9999-999999999917', 'completed', '[{"section": "projects", "issue": "Chưa chi tiết hóa kỹ thuật xử lý WebSocket thời gian thực", "suggestion": "Mô tả giải pháp tránh rò rỉ bộ nhớ khi mở nhiều connection", "priority": "medium"}]'::jsonb, 'openai', 'gpt-4o', 'v1.0'),
('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaa08', '44444444-4444-4444-4444-444444444418', '55555555-5555-5555-5555-555555555509', '99999999-9999-9999-9999-999999999918', 'completed', '[{"section": "experience", "issue": "Kinh nghiệm thực tập còn ngắn", "suggestion": "Bổ sung link GitHub các bài tập lớn/đồ án tốt nghiệp chất lượng", "priority": "high"}]'::jsonb, 'openai', 'gpt-4o', 'v1.0'),
('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaa09', '44444444-4444-4444-4444-444444444422', '55555555-5555-5555-5555-555555555513', '99999999-9999-9999-9999-999999999922', 'completed', '[{"section": "summary", "issue": "Hồ sơ đã hoàn chỉnh", "suggestion": "Có thể bổ sung chứng chỉ PMP hoặc Agile Coach", "priority": "low"}]'::jsonb, 'openai', 'gpt-4o', 'v1.0'),
('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaa10', '44444444-4444-4444-4444-444444444424', '55555555-5555-5555-5555-555555555506', '99999999-9999-9999-9999-999999999924', 'completed', '[{"section": "experience", "issue": "Chưa nêu quy trình báo cáo lỗ hổng bảo mật", "suggestion": "Trình bày theo tiêu chuẩn báo cáo OWASP Top 10", "priority": "medium"}]'::jsonb, 'openai', 'gpt-4o', 'v1.0');

-- 23. Match Results (16 Match records)
INSERT INTO match_results (id, job_id, cv_id, status, vector_score, overall_score, score_breakdown, matched_skills, missing_skills, explanation, provider, model_name, prompt_version) VALUES
('88888888-8888-8888-8888-888888888801', '55555555-5555-5555-5555-555555555501', '44444444-4444-4444-4444-444444444410', 'completed', 0.91, 92, '{"skills": 95, "experience": 90, "education": 88}'::jsonb, '["Python", "PostgreSQL", "Docker"]'::jsonb, '[]'::jsonb, 'Ứng viên có kỹ năng và số năm kinh nghiệm khớp hoàn toàn với yêu cầu công việc.', 'openai', 'gpt-4o', 'v1.0'),
('88888888-8888-8888-8888-888888888802', '55555555-5555-5555-5555-555555555502', '44444444-4444-4444-4444-444444444412', 'completed', 0.98, 97, '{"skills": 99, "experience": 98, "education": 95}'::jsonb, '["Java", "Spring Boot", "PostgreSQL"]'::jsonb, '[]'::jsonb, 'Ứng viên là chuyên gia giải pháp xuất sắc cho lĩnh vực Fintech.', 'openai', 'gpt-4o', 'v1.0'),
('88888888-8888-8888-8888-888888888803', '55555555-5555-5555-5555-555555555503', '44444444-4444-4444-4444-444444444415', 'completed', 0.94, 94, '{"skills": 96, "experience": 92, "education": 95}'::jsonb, '["Python", "PyTorch", "TensorFlow"]'::jsonb, '[]'::jsonb, 'Chuyên môn AI và Computer Vision hoàn toàn phù hợp.', 'openai', 'gpt-4o', 'v1.0'),
('88888888-8888-8888-8888-888888888804', '55555555-5555-5555-5555-555555555504', '44444444-4444-4444-4444-444444444411', 'completed', 0.89, 90, '{"skills": 92, "experience": 88, "education": 88}'::jsonb, '["ReactJS", "TypeScript", "Next.js"]'::jsonb, '[]'::jsonb, 'Kỹ năng Frontend hiện đại đáp ứng tốt sản phẩm sàn thương mại điện tử.', 'openai', 'gpt-4o', 'v1.0'),
('88888888-8888-8888-8888-888888888805', '55555555-5555-5555-5555-555555555505', '44444444-4444-4444-4444-444444444413', 'completed', 0.96, 95, '{"skills": 98, "experience": 94, "education": 90}'::jsonb, '["Docker", "Kubernetes", "AWS Cloud"]'::jsonb, '[]'::jsonb, 'Kỹ năng hạ tầng điện toán đám mây khớp chính xác với JD.', 'openai', 'gpt-4o', 'v1.0'),
('88888888-8888-8888-8888-888888888806', '55555555-5555-5555-5555-555555555506', '44444444-4444-4444-4444-444444444424', 'completed', 0.92, 91, '{"skills": 94, "experience": 89, "education": 88}'::jsonb, '["Linux", "Security", "Pentest"]'::jsonb, '[]'::jsonb, 'Đáp ứng đầy đủ yêu cầu kiểm thử an ninh ứng dụng web.', 'openai', 'gpt-4o', 'v1.0'),
('88888888-8888-8888-8888-888888888807', '55555555-5555-5555-5555-555555555507', '44444444-4444-4444-4444-444444444416', 'completed', 0.90, 89, '{"skills": 92, "experience": 88, "education": 86}'::jsonb, '["Go (Golang)", "PostgreSQL", "Redis"]'::jsonb, '[]'::jsonb, 'Kỹ sư Golang phù hợp hệ thống xử lý thời gian thực.', 'openai', 'gpt-4o', 'v1.0'),
('88888888-8888-8888-8888-888888888808', '55555555-5555-5555-5555-555555555508', '44444444-4444-4444-4444-444444444414', 'completed', 0.93, 93, '{"skills": 95, "experience": 90, "education": 92}'::jsonb, '["Figma", "UI Design", "User Research"]'::jsonb, '[]'::jsonb, 'Kỹ năng thiết kế sản phẩm và xây dựng Design System xuất sắc.', 'openai', 'gpt-4o', 'v1.0'),
('88888888-8888-8888-8888-888888888809', '55555555-5555-5555-5555-555555555509', '44444444-4444-4444-4444-444444444418', 'completed', 0.85, 84, '{"skills": 85, "experience": 75, "education": 92}'::jsonb, '["Java", "Spring Boot"]'::jsonb, '[]'::jsonb, 'Ứng viên Fresher tiềm năng cho dự án đào tạo.', 'openai', 'gpt-4o', 'v1.0'),
('88888888-8888-8888-8888-888888888810', '55555555-5555-5555-5555-555555555510', '44444444-4444-4444-4444-444444444419', 'completed', 0.84, 82, '{"skills": 82, "experience": 74, "education": 90}'::jsonb, '["VueJS", "JavaScript"]'::jsonb, '[]'::jsonb, 'Fresher Frontend có nền tảng tốt.', 'openai', 'gpt-4o', 'v1.0'),
('88888888-8888-8888-8888-888888888811', '55555555-5555-5555-5555-555555555511', '44444444-4444-4444-4444-444444444420', 'completed', 0.78, 79, '{"skills": 78, "experience": 60, "education": 88}'::jsonb, '["Python"]'::jsonb, '[]'::jsonb, 'Thực tập sinh có thái độ tốt và nắm căn bản.', 'openai', 'gpt-4o', 'v1.0'),
('88888888-8888-8888-8888-888888888812', '55555555-5555-5555-5555-555555555512', '44444444-4444-4444-4444-444444444421', 'completed', 0.80, 81, '{"skills": 82, "experience": 65, "education": 89}'::jsonb, '["Figma"]'::jsonb, '[]'::jsonb, 'Thực tập sinh thiết kế có gu thẩm mỹ tốt.', 'openai', 'gpt-4o', 'v1.0'),
('88888888-8888-8888-8888-888888888813', '55555555-5555-5555-5555-555555555513', '44444444-4444-4444-4444-444444444422', 'completed', 0.98, 98, '{"skills": 99, "experience": 99, "education": 96}'::jsonb, '["Engineering Management", "Agile", "Architecture"]'::jsonb, '[]'::jsonb, 'Kinh nghiệm quản lý dày dạn phù hợp vị trí Head.', 'openai', 'gpt-4o', 'v1.0'),
('88888888-8888-8888-8888-888888888814', '55555555-5555-5555-5555-555555555514', '44444444-4444-4444-4444-444444444423', 'completed', 0.99, 99, '{"skills": 99, "experience": 100, "education": 98}'::jsonb, '["Leadership", "Strategy"]'::jsonb, '[]'::jsonb, 'Hồ sơ tầm cỡ CTO khu vực.', 'openai', 'gpt-4o', 'v1.0'),
('88888888-8888-8888-8888-888888888815', '55555555-5555-5555-5555-555555555515', '44444444-4444-4444-4444-444444444425', 'completed', 0.92, 91, '{"skills": 93, "experience": 90, "education": 88}'::jsonb, '["QA Automation", "Python", "CI/CD"]'::jsonb, '[]'::jsonb, 'Kinh nghiệm kiểm thử tự động đáp ứng trọn vẹn yêu cầu.', 'openai', 'gpt-4o', 'v1.0'),
('88888888-8888-8888-8888-888888888816', '55555555-5555-5555-5555-555555555516', '44444444-4444-4444-4444-444444444417', 'completed', 0.90, 89, '{"skills": 91, "experience": 88, "education": 86}'::jsonb, '["Node.js", "ReactJS", "MongoDB"]'::jsonb, '[]'::jsonb, 'Kỹ năng Fullstack JS phù hợp hệ thống live-streaming.', 'openai', 'gpt-4o', 'v1.0');

-- 24. Job Recommendations (16 Recommendations)
INSERT INTO job_recommendations (id, cv_id, job_id, match_result_id, rank, final_score, reason, feedback) VALUES
('c1111111-1111-1111-1111-111111111101', '44444444-4444-4444-4444-444444444410', '55555555-5555-5555-5555-555555555501', '88888888-8888-8888-8888-888888888801', 1, 92, 'Công việc phù hợp tuyệt vời với kỹ năng Python và PostgreSQL của bạn.', 'applied'),
('c1111111-1111-1111-1111-111111111102', '44444444-4444-4444-4444-444444444412', '55555555-5555-5555-5555-555555555502', '88888888-8888-8888-8888-888888888802', 1, 97, 'Vị trí Lead Java tương thích cao với kinh nghiệm Fintech của bạn.', 'applied'),
('c1111111-1111-1111-1111-111111111103', '44444444-4444-4444-4444-444444444415', '55555555-5555-5555-5555-555555555503', '88888888-8888-8888-8888-888888888803', 1, 94, 'Dự án AI phù hợp với nền tảng nghiên cứu và kinh nghiệm PyTorch.', 'saved'),
('c1111111-1111-1111-1111-111111111104', '44444444-4444-4444-4444-444444444411', '55555555-5555-5555-5555-555555555504', '88888888-8888-8888-8888-888888888804', 1, 90, 'Cơ hội làm việc từ xa vị trí Frontend ReactJS cho sàn thương mại điện tử.', 'applied'),
('c1111111-1111-1111-1111-111111111105', '44444444-4444-4444-4444-444444444413', '55555555-5555-5555-5555-555555555505', '88888888-8888-8888-8888-888888888805', 1, 95, 'Vị trí DevOps tại CloudScale Networks phù hợp chuyên môn Kubernetes.', 'applied'),
('c1111111-1111-1111-1111-111111111106', '44444444-4444-4444-4444-444444444424', '55555555-5555-5555-5555-555555555506', '88888888-8888-8888-8888-888888888806', 1, 91, 'Cơ hội phát triển sự nghiệp pentest chuyên nghiệp tại CyberDefense.', 'viewed'),
('c1111111-1111-1111-1111-111111111107', '44444444-4444-4444-4444-444444444416', '55555555-5555-5555-5555-555555555507', '88888888-8888-8888-8888-888888888807', 1, 89, 'Hệ thống điều phối logistics phù hợp với kỹ năng xử lý tải của Go.', 'applied'),
('c1111111-1111-1111-1111-111111111108', '44444444-4444-4444-4444-444444444414', '55555555-5555-5555-5555-555555555508', '88888888-8888-8888-8888-888888888808', 1, 93, 'Vị trí Product Designer tại EduTech tương đồng với định hướng UI/UX.', 'applied'),
('c1111111-1111-1111-1111-111111111109', '44444444-4444-4444-4444-444444444418', '55555555-5555-5555-5555-555555555509', '88888888-8888-8888-8888-888888888809', 1, 84, 'Vị trí Fresher Java mở rộng cho sinh viên mới ra trường.', 'applied'),
('c1111111-1111-1111-1111-111111111110', '44444444-4444-4444-4444-444444444419', '55555555-5555-5555-5555-555555555510', '88888888-8888-8888-8888-888888888810', 1, 82, 'Vị trí Fresher VueJS tại E-Commerce Stars.', 'viewed'),
('c1111111-1111-1111-1111-111111111111', '44444444-4444-4444-4444-444444444420', '55555555-5555-5555-5555-555555555511', '88888888-8888-8888-8888-888888888811', 1, 79, 'Cơ hội thực tập AI có trợ cấp tại trung tâm R&D.', 'applied'),
('c1111111-1111-1111-1111-111111111112', '44444444-4444-4444-4444-444444444421', '55555555-5555-5555-5555-555555555512', '88888888-8888-8888-8888-888888888812', 1, 81, 'Thực tập sinh UI/UX được đào tạo 1 kèm 1.', 'new'),
('c1111111-1111-1111-1111-111111111113', '44444444-4444-4444-4444-444444444422', '55555555-5555-5555-5555-555555555513', '88888888-8888-8888-8888-888888888813', 1, 98, 'Vị trí lãnh đạo công nghệ quy mô tại ngân hàng quốc tế.', 'applied'),
('c1111111-1111-1111-1111-111111111114', '44444444-4444-4444-4444-444444444423', '55555555-5555-5555-5555-555555555514', '88888888-8888-8888-8888-888888888814', 1, 99, 'Vị trí CTO dẫn dắt hạ tầng đám mây khu vực.', 'saved'),
('c1111111-1111-1111-1111-111111111115', '44444444-4444-4444-4444-444444444425', '55555555-5555-5555-5555-555555555515', '88888888-8888-8888-8888-888888888815', 1, 91, 'Cơ hội phụ trách mảng QA tự động hóa hệ thống Logistics.', 'applied'),
('c1111111-1111-1111-1111-111111111116', '44444444-4444-4444-4444-444444444417', '55555555-5555-5555-5555-555555555516', '88888888-8888-8888-8888-888888888816', 1, 89, 'Vị trí Fullstack Node/React cho sản phẩm streaming tốc độ cao.', 'applied');

-- 25. LLM Requests (10 Log records)
INSERT INTO llm_requests (feature, provider, model_name, prompt_version, status, input_tokens, output_tokens, cost_usd, latency_ms, user_id, object_type, object_id) VALUES
('cv_analysis', 'openai', 'gpt-4o', 'v1.0', 'success', 1250, 380, 0.005520, 1450, '00000000-0000-0000-0000-000000000010', 'cv_analysis', '99999999-9999-9999-9999-999999999910'),
('candidate_matching', 'openai', 'gpt-4o', 'v1.0', 'success', 1820, 410, 0.007820, 1820, '00000000-0000-0000-0000-000000000002', 'match_result', '88888888-8888-8888-8888-888888888801'),
('cv_analysis', 'openai', 'gpt-4o', 'v1.0', 'success', 1400, 420, 0.006240, 1610, '00000000-0000-0000-0000-000000000011', 'cv_analysis', '99999999-9999-9999-9999-999999999911'),
('candidate_matching', 'openai', 'gpt-4o', 'v1.0', 'success', 1950, 450, 0.008450, 1920, '00000000-0000-0000-0000-000000000003', 'match_result', '88888888-8888-8888-8888-888888888802'),
('cv_analysis', 'openai', 'gpt-4o', 'v1.0', 'success', 1600, 480, 0.007120, 1780, '00000000-0000-0000-0000-000000000012', 'cv_analysis', '99999999-9999-9999-9999-999999999912'),
('cv_suggestion', 'openai', 'gpt-4o', 'v1.0', 'success', 1100, 320, 0.004780, 1310, '00000000-0000-0000-0000-000000000010', 'cv_suggestion', 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaa01'),
('cv_analysis', 'openai', 'gpt-4o', 'v1.0', 'success', 1350, 390, 0.005930, 1530, '00000000-0000-0000-0000-000000000013', 'cv_analysis', '99999999-9999-9999-9999-999999999913'),
('candidate_matching', 'openai', 'gpt-4o', 'v1.0', 'success', 1780, 400, 0.007620, 1740, '00000000-0000-0000-0000-000000000006', 'match_result', '88888888-8888-8888-8888-888888888805'),
('job_recommendation', 'openai', 'gpt-4o', 'v1.0', 'success', 2100, 520, 0.009280, 2150, '00000000-0000-0000-0000-000000000010', 'job_recommendation', 'c1111111-1111-1111-1111-111111111101'),
('job_recommendation', 'openai', 'gpt-4o', 'v1.0', 'success', 2050, 510, 0.009060, 2090, '00000000-0000-0000-0000-000000000012', 'job_recommendation', 'c1111111-1111-1111-1111-111111111102');
