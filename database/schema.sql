-- =====================================================================
-- ATS + AI: PostgreSQL schema (tài liệu thiết kế)
--
-- Nguồn chính vẫn là Django migrations. File này dùng để review thiết kế
-- và đối chiếu khi viết models. Giải thích chi tiết: docs/database-design.md
--
-- Yêu cầu PostgreSQL >= 13 (có sẵn gen_random_uuid()).
-- Quy ước:
--   * Bảng nghiệp vụ dùng khóa UUID; bảng danh mục/log dùng BIGINT identity.
--   * Enum = VARCHAR + CHECK (tương ứng TextChoices của Django, dễ migrate).
--   * deleted_at != NULL nghĩa là đã xóa mềm.
--   * updated_at do Django cập nhật (auto_now), không dùng trigger.
--   * Embedding lưu ở ChromaDB, không lưu trong PostgreSQL.
-- =====================================================================


-- =====================================================================
-- CATALOG: danh mục dùng chung (app mới: apps/catalog)
-- =====================================================================

CREATE TABLE skills (
    id           BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name         VARCHAR(100) NOT NULL,
    slug         VARCHAR(120) NOT NULL UNIQUE,
    category     VARCHAR(20)  NOT NULL DEFAULT 'technical'
                 CHECK (category IN ('technical', 'soft', 'language', 'tool', 'domain')),
    aliases      TEXT[]       NOT NULL DEFAULT '{}',      -- "ReactJS", "React.js" -> React
    is_verified  BOOLEAN      NOT NULL DEFAULT FALSE,     -- FALSE: do AI/NLP tự thêm, chờ admin duyệt
    created_at   TIMESTAMPTZ  NOT NULL DEFAULT now()
);
CREATE INDEX idx_skills_aliases ON skills USING GIN (aliases);

CREATE TABLE industries (
    id         BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name       VARCHAR(150) NOT NULL,
    slug       VARCHAR(170) NOT NULL UNIQUE,
    parent_id  BIGINT REFERENCES industries (id) ON DELETE SET NULL
);

CREATE TABLE locations (
    id            BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name          VARCHAR(150) NOT NULL,                  -- Tỉnh/thành phố
    slug          VARCHAR(170) NOT NULL UNIQUE,
    country_code  CHAR(2)      NOT NULL DEFAULT 'VN'
);


-- =====================================================================
-- ACCOUNTS
-- =====================================================================

CREATE TABLE users (
    id                 UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email              VARCHAR(254) NOT NULL,
    password           VARCHAR(128) NOT NULL,             -- hash của Django
    full_name          VARCHAR(150) NOT NULL DEFAULT '',
    phone              VARCHAR(20),
    avatar_url         VARCHAR(500),
    role               VARCHAR(20)  NOT NULL
                       CHECK (role IN ('candidate', 'employer', 'admin')),
    is_active          BOOLEAN      NOT NULL DEFAULT TRUE,
    is_staff           BOOLEAN      NOT NULL DEFAULT FALSE,
    is_superuser       BOOLEAN      NOT NULL DEFAULT FALSE,
    email_verified_at  TIMESTAMPTZ,
    last_login         TIMESTAMPTZ,
    created_at         TIMESTAMPTZ  NOT NULL DEFAULT now(),
    updated_at         TIMESTAMPTZ  NOT NULL DEFAULT now(),
    deleted_at         TIMESTAMPTZ
);
CREATE UNIQUE INDEX uq_users_email ON users (lower(email));
-- Bảng phụ do Django/thư viện tự sinh, không cần thiết kế tay:
--   users_groups, users_user_permissions (PermissionsMixin)
--   token_blacklist_* (djangorestframework-simplejwt)
-- Token xác thực email/reset mật khẩu dùng signed token (stateless), không cần bảng.


-- =====================================================================
-- CANDIDATES
-- =====================================================================

CREATE TABLE candidate_profiles (
    id                   UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id              UUID NOT NULL UNIQUE REFERENCES users (id) ON DELETE CASCADE,
    headline             VARCHAR(200),                    -- "Backend Developer | 3 năm Python"
    date_of_birth        DATE,
    gender               VARCHAR(10) CHECK (gender IN ('male', 'female', 'other')),
    address              VARCHAR(255),
    location_id          BIGINT REFERENCES locations (id) ON DELETE SET NULL,
    summary              TEXT,
    years_of_experience  NUMERIC(4,1) CHECK (years_of_experience >= 0),
    current_level        VARCHAR(20)
                         CHECK (current_level IN ('intern', 'fresher', 'junior', 'middle',
                                                  'senior', 'lead', 'manager')),
    desired_position     VARCHAR(150),
    desired_salary_min   BIGINT CHECK (desired_salary_min >= 0),
    desired_salary_max   BIGINT,
    salary_currency      CHAR(3)     NOT NULL DEFAULT 'VND',
    desired_job_type     VARCHAR(20)
                         CHECK (desired_job_type IN ('full_time', 'part_time', 'internship',
                                                     'contract', 'freelance')),
    desired_work_mode    VARCHAR(20) CHECK (desired_work_mode IN ('onsite', 'remote', 'hybrid')),
    is_open_to_work      BOOLEAN     NOT NULL DEFAULT TRUE,
    is_public            BOOLEAN     NOT NULL DEFAULT FALSE,  -- cho phép NTD tìm thấy (talent pool)
    created_at           TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at           TIMESTAMPTZ NOT NULL DEFAULT now(),
    CHECK (desired_salary_max IS NULL OR desired_salary_min IS NULL
           OR desired_salary_max >= desired_salary_min)
);

CREATE TABLE candidate_preferred_locations (
    id            BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    candidate_id  UUID   NOT NULL REFERENCES candidate_profiles (id) ON DELETE CASCADE,
    location_id   BIGINT NOT NULL REFERENCES locations (id) ON DELETE CASCADE,
    UNIQUE (candidate_id, location_id)
);

CREATE TABLE candidate_educations (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    candidate_id  UUID NOT NULL REFERENCES candidate_profiles (id) ON DELETE CASCADE,
    school        VARCHAR(200) NOT NULL,
    degree        VARCHAR(100),                           -- Cử nhân, Kỹ sư, Thạc sĩ...
    major         VARCHAR(150),
    gpa           NUMERIC(4,2),
    start_date    DATE,
    end_date      DATE,
    description   TEXT,
    sort_order    SMALLINT    NOT NULL DEFAULT 0,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_cand_edu_candidate ON candidate_educations (candidate_id);

CREATE TABLE candidate_experiences (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    candidate_id  UUID NOT NULL REFERENCES candidate_profiles (id) ON DELETE CASCADE,
    company_name  VARCHAR(200) NOT NULL,
    position      VARCHAR(150) NOT NULL,
    start_date    DATE NOT NULL,
    end_date      DATE,
    is_current    BOOLEAN     NOT NULL DEFAULT FALSE,
    description   TEXT,
    sort_order    SMALLINT    NOT NULL DEFAULT 0,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    CHECK (end_date IS NULL OR end_date >= start_date)
);
CREATE INDEX idx_cand_exp_candidate ON candidate_experiences (candidate_id);

-- Kỹ năng ứng viên TỰ KHAI trên hồ sơ (khác cv_skills do hệ thống trích xuất từ CV)
CREATE TABLE candidate_skills (
    id                   BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    candidate_id         UUID   NOT NULL REFERENCES candidate_profiles (id) ON DELETE CASCADE,
    skill_id             BIGINT NOT NULL REFERENCES skills (id) ON DELETE CASCADE,
    level                SMALLINT CHECK (level BETWEEN 1 AND 5),
    years_of_experience  NUMERIC(4,1),
    UNIQUE (candidate_id, skill_id)
);
CREATE INDEX idx_cand_skills_skill ON candidate_skills (skill_id);


-- =====================================================================
-- EMPLOYERS
-- =====================================================================

CREATE TABLE companies (
    id                   UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name                 VARCHAR(255) NOT NULL,
    slug                 VARCHAR(280) NOT NULL UNIQUE,
    tax_code             VARCHAR(20) UNIQUE,              -- Mã số thuế, dùng để xác minh
    logo_url             VARCHAR(500),
    cover_url            VARCHAR(500),
    website              VARCHAR(255),
    email                VARCHAR(254),
    phone                VARCHAR(20),
    address              VARCHAR(255),
    location_id          BIGINT REFERENCES locations (id) ON DELETE SET NULL,
    industry_id          BIGINT REFERENCES industries (id) ON DELETE SET NULL,
    company_size         VARCHAR(20)
                         CHECK (company_size IN ('1-10', '11-50', '51-200', '201-500',
                                                 '501-1000', '1000+')),
    founded_year         SMALLINT,
    description          TEXT,
    verification_status  VARCHAR(20) NOT NULL DEFAULT 'pending'
                         CHECK (verification_status IN ('pending', 'verified', 'rejected')),
    verified_at          TIMESTAMPTZ,
    verified_by          UUID REFERENCES users (id) ON DELETE SET NULL,   -- admin duyệt
    created_by           UUID REFERENCES users (id) ON DELETE SET NULL,
    created_at           TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at           TIMESTAMPTZ NOT NULL DEFAULT now(),
    deleted_at           TIMESTAMPTZ
);

-- Nhà tuyển dụng = User (role=employer) thuộc về một Company
CREATE TABLE recruiters (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id       UUID NOT NULL UNIQUE REFERENCES users (id) ON DELETE CASCADE,
    company_id    UUID NOT NULL REFERENCES companies (id) ON DELETE RESTRICT,
    position      VARCHAR(100),                           -- HR Manager, Talent Acquisition...
    company_role  VARCHAR(20) NOT NULL DEFAULT 'member'
                  CHECK (company_role IN ('owner', 'admin', 'member')),
    status        VARCHAR(20) NOT NULL DEFAULT 'pending'
                  CHECK (status IN ('pending', 'active', 'removed')),
    joined_at     TIMESTAMPTZ,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_recruiters_company ON recruiters (company_id);


-- =====================================================================
-- CVS
-- =====================================================================

-- Mỗi lần upload là một bản ghi mới. Đã nộp vào application thì không sửa file.
CREATE TABLE cvs (
    id                 UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    candidate_id       UUID NOT NULL REFERENCES candidate_profiles (id) ON DELETE CASCADE,
    title              VARCHAR(150) NOT NULL,             -- "CV Backend - tiếng Anh"
    file_key           VARCHAR(500) NOT NULL,             -- key trong storage (local/S3/MinIO)
    original_filename  VARCHAR(255) NOT NULL,
    mime_type          VARCHAR(100) NOT NULL
                       CHECK (mime_type IN (
                           'application/pdf',
                           'application/vnd.openxmlformats-officedocument.wordprocessingml.document')),
    file_size          INTEGER  NOT NULL CHECK (file_size > 0),
    file_hash          CHAR(64) NOT NULL,                 -- SHA-256: phát hiện trùng, khóa cache AI
    language           VARCHAR(10),                       -- vi, en...
    is_default         BOOLEAN  NOT NULL DEFAULT FALSE,
    -- Kết quả parse (NLP, không dùng LLM)
    parse_status       VARCHAR(20) NOT NULL DEFAULT 'pending'
                       CHECK (parse_status IN ('pending', 'processing', 'completed', 'failed')),
    parse_error        TEXT,
    raw_text           TEXT,
    parsed_data        JSONB,                             -- contact, education, experience, skills...
    parsed_at          TIMESTAMPTZ,
    -- Đồng bộ ChromaDB (document id = cvs.id)
    vector_model       VARCHAR(100),
    vector_indexed_at  TIMESTAMPTZ,
    created_at         TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at         TIMESTAMPTZ NOT NULL DEFAULT now(),
    deleted_at         TIMESTAMPTZ
);
CREATE INDEX idx_cvs_candidate ON cvs (candidate_id, created_at DESC) WHERE deleted_at IS NULL;
CREATE INDEX idx_cvs_file_hash ON cvs (file_hash);
-- Mỗi ứng viên có tối đa 1 CV mặc định
CREATE UNIQUE INDEX uq_cvs_default ON cvs (candidate_id) WHERE is_default AND deleted_at IS NULL;

-- Kỹ năng trích xuất từ CV (spaCy/LLM), đã chuẩn hóa về catalog -> lọc nhanh bằng SQL
CREATE TABLE cv_skills (
    id                   BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    cv_id                UUID   NOT NULL REFERENCES cvs (id) ON DELETE CASCADE,
    skill_id             BIGINT NOT NULL REFERENCES skills (id) ON DELETE CASCADE,
    source               VARCHAR(10) NOT NULL CHECK (source IN ('nlp', 'llm', 'manual')),
    confidence           REAL CHECK (confidence BETWEEN 0 AND 1),
    years_of_experience  NUMERIC(4,1),
    UNIQUE (cv_id, skill_id)
);
CREATE INDEX idx_cv_skills_skill ON cv_skills (skill_id);


-- =====================================================================
-- JOBS
-- =====================================================================

CREATE TABLE jobs (
    id                     UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id             UUID NOT NULL REFERENCES companies (id) ON DELETE RESTRICT,
    created_by             UUID REFERENCES users (id) ON DELETE SET NULL,
    title                  VARCHAR(255) NOT NULL,
    slug                   VARCHAR(300) NOT NULL UNIQUE,
    description            TEXT NOT NULL,
    requirements           TEXT NOT NULL,
    benefits               TEXT,
    job_type               VARCHAR(20) NOT NULL
                           CHECK (job_type IN ('full_time', 'part_time', 'internship',
                                               'contract', 'freelance')),
    work_mode              VARCHAR(20) NOT NULL DEFAULT 'onsite'
                           CHECK (work_mode IN ('onsite', 'remote', 'hybrid')),
    level                  VARCHAR(20) NOT NULL
                           CHECK (level IN ('intern', 'fresher', 'junior', 'middle',
                                            'senior', 'lead', 'manager')),
    min_years_experience   NUMERIC(4,1) NOT NULL DEFAULT 0,
    salary_min             BIGINT CHECK (salary_min >= 0),
    salary_max             BIGINT,
    salary_currency        CHAR(3) NOT NULL DEFAULT 'VND',
    is_salary_negotiable   BOOLEAN NOT NULL DEFAULT FALSE,
    headcount              SMALLINT NOT NULL DEFAULT 1 CHECK (headcount > 0),
    location_id            BIGINT REFERENCES locations (id) ON DELETE SET NULL,
    address                VARCHAR(255),
    industry_id            BIGINT REFERENCES industries (id) ON DELETE SET NULL,
    deadline               DATE,
    status                 VARCHAR(20) NOT NULL DEFAULT 'draft'
                           CHECK (status IN ('draft', 'published', 'paused', 'closed', 'expired')),
    published_at           TIMESTAMPTZ,
    closed_at              TIMESTAMPTZ,
    view_count             INTEGER NOT NULL DEFAULT 0,
    application_count      INTEGER NOT NULL DEFAULT 0,   -- denormalized, cập nhật trong service
    search_vector          TSVECTOR,                     -- full-text search (title + description)
    vector_model           VARCHAR(100),                 -- đồng bộ ChromaDB (document id = jobs.id)
    vector_indexed_at      TIMESTAMPTZ,
    created_at             TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at             TIMESTAMPTZ NOT NULL DEFAULT now(),
    deleted_at             TIMESTAMPTZ,
    CHECK (salary_max IS NULL OR salary_min IS NULL OR salary_max >= salary_min)
);
CREATE INDEX idx_jobs_company ON jobs (company_id, created_at DESC);
CREATE INDEX idx_jobs_public_list ON jobs (published_at DESC)
    WHERE status = 'published' AND deleted_at IS NULL;
CREATE INDEX idx_jobs_filter ON jobs (location_id, level, job_type)
    WHERE status = 'published' AND deleted_at IS NULL;
CREATE INDEX idx_jobs_search ON jobs USING GIN (search_vector);

CREATE TABLE job_skills (
    id          BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    job_id      UUID   NOT NULL REFERENCES jobs (id) ON DELETE CASCADE,
    skill_id    BIGINT NOT NULL REFERENCES skills (id) ON DELETE CASCADE,
    is_required BOOLEAN  NOT NULL DEFAULT TRUE,          -- FALSE = "nice to have"
    min_years   NUMERIC(4,1),
    weight      SMALLINT NOT NULL DEFAULT 3 CHECK (weight BETWEEN 1 AND 5),  -- trọng số khi matching
    UNIQUE (job_id, skill_id)
);
CREATE INDEX idx_job_skills_skill ON job_skills (skill_id);

-- Job ứng viên đã lưu (thuộc app candidates)
CREATE TABLE saved_jobs (
    id            BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    candidate_id  UUID NOT NULL REFERENCES candidate_profiles (id) ON DELETE CASCADE,
    job_id        UUID NOT NULL REFERENCES jobs (id) ON DELETE CASCADE,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (candidate_id, job_id)
);


-- =====================================================================
-- APPLICATIONS (ATS)
-- =====================================================================

CREATE TABLE applications (
    id                 UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id             UUID NOT NULL REFERENCES jobs (id) ON DELETE RESTRICT,
    candidate_id       UUID NOT NULL REFERENCES candidate_profiles (id) ON DELETE CASCADE,
    cv_id              UUID NOT NULL REFERENCES cvs (id) ON DELETE RESTRICT,
    cover_letter       TEXT,
    status             VARCHAR(20) NOT NULL DEFAULT 'applied'
                       CHECK (status IN ('applied', 'screening', 'interview', 'offer',
                                         'hired', 'rejected', 'withdrawn')),
    rejection_reason   TEXT,
    recruiter_rating   SMALLINT CHECK (recruiter_rating BETWEEN 1 AND 5),
    status_changed_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_at         TIMESTAMPTZ NOT NULL DEFAULT now(),  -- = thời điểm nộp
    updated_at         TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (job_id, candidate_id)                            -- chống nộp trùng
);
CREATE INDEX idx_applications_job_status ON applications (job_id, status);
CREATE INDEX idx_applications_candidate ON applications (candidate_id, created_at DESC);

CREATE TABLE application_status_history (
    id              BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    application_id  UUID NOT NULL REFERENCES applications (id) ON DELETE CASCADE,
    from_status     VARCHAR(20),                          -- NULL ở bản ghi đầu tiên
    to_status       VARCHAR(20) NOT NULL,
    changed_by      UUID REFERENCES users (id) ON DELETE SET NULL,
    note            TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_app_history_app ON application_status_history (application_id, created_at);

CREATE TABLE interviews (
    id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    application_id    UUID NOT NULL REFERENCES applications (id) ON DELETE CASCADE,
    round             SMALLINT NOT NULL DEFAULT 1,
    title             VARCHAR(150),
    scheduled_at      TIMESTAMPTZ NOT NULL,
    duration_minutes  SMALLINT NOT NULL DEFAULT 60,
    mode              VARCHAR(20) NOT NULL CHECK (mode IN ('online', 'offline', 'phone')),
    location          VARCHAR(255),
    meeting_url       VARCHAR(500),
    interviewer_id    UUID REFERENCES users (id) ON DELETE SET NULL,
    status            VARCHAR(20) NOT NULL DEFAULT 'scheduled'
                      CHECK (status IN ('scheduled', 'completed', 'cancelled', 'no_show')),
    result            VARCHAR(20) NOT NULL DEFAULT 'pending'
                      CHECK (result IN ('pending', 'passed', 'failed')),
    rating            SMALLINT CHECK (rating BETWEEN 1 AND 5),
    feedback          TEXT,
    created_by        UUID REFERENCES users (id) ON DELETE SET NULL,
    created_at        TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at        TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_interviews_application ON interviews (application_id);
CREATE INDEX idx_interviews_interviewer ON interviews (interviewer_id, scheduled_at);


-- =====================================================================
-- AI
-- Các bảng kết quả AI dùng chung bộ cột theo dõi:
--   status, provider, model_name, prompt_version, input_hash, task_id,
--   error_message, created_at, completed_at
-- input_hash = SHA-256(dữ liệu đầu vào + prompt_version + model): nếu trùng
-- thì dùng lại kết quả cũ, không gọi LLM lần nữa.
-- =====================================================================

-- (1) CV analysis: phân tích, chấm điểm tổng quát một CV
CREATE TABLE cv_analyses (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cv_id           UUID NOT NULL REFERENCES cvs (id) ON DELETE CASCADE,
    status          VARCHAR(20) NOT NULL DEFAULT 'pending'
                    CHECK (status IN ('pending', 'processing', 'completed', 'failed')),
    overall_score   SMALLINT CHECK (overall_score BETWEEN 0 AND 100),
    section_scores  JSONB,          -- {"format": 80, "experience": 65, "skills": 70, ...}
    strengths       JSONB,          -- ["...", "..."]
    weaknesses      JSONB,
    summary         TEXT,
    detected_level  VARCHAR(20),    -- level AI ước lượng (junior/middle...)
    provider        VARCHAR(30),
    model_name      VARCHAR(100),
    prompt_version  VARCHAR(20),
    input_hash      CHAR(64),
    task_id         VARCHAR(255),   -- Celery task id
    error_message   TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    completed_at    TIMESTAMPTZ
);
CREATE INDEX idx_cv_analyses_cv ON cv_analyses (cv_id, created_at DESC);
CREATE INDEX idx_cv_analyses_hash ON cv_analyses (input_hash);

-- (2) CV suggestion: gợi ý sửa CV, tổng quát (job_id NULL) hoặc theo một JD
CREATE TABLE cv_suggestions (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cv_id           UUID NOT NULL REFERENCES cvs (id) ON DELETE CASCADE,
    job_id          UUID REFERENCES jobs (id) ON DELETE SET NULL,
    analysis_id     UUID REFERENCES cv_analyses (id) ON DELETE SET NULL,
    status          VARCHAR(20) NOT NULL DEFAULT 'pending'
                    CHECK (status IN ('pending', 'processing', 'completed', 'failed')),
    suggestions     JSONB NOT NULL DEFAULT '[]',
                    -- [{"section": "experience", "issue": "...", "suggestion": "...",
                    --   "priority": "high", "example": "..."}]
    provider        VARCHAR(30),
    model_name      VARCHAR(100),
    prompt_version  VARCHAR(20),
    input_hash      CHAR(64),
    task_id         VARCHAR(255),
    error_message   TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    completed_at    TIMESTAMPTZ
);
CREATE INDEX idx_cv_suggestions_cv ON cv_suggestions (cv_id, created_at DESC);
CREATE INDEX idx_cv_suggestions_hash ON cv_suggestions (input_hash);

-- (3)+(4) Điểm khớp của cặp (CV, Job), dùng chung cho cả hai chiều:
--   * Candidate matching: lấy theo job_id, sắp xếp theo overall_score
--   * Job recommendation: lấy theo cv_id
-- Mỗi cặp chỉ chấm một lần; tính lại khi input_hash thay đổi (CV hoặc JD đã sửa).
CREATE TABLE match_results (
    id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id           UUID NOT NULL REFERENCES jobs (id) ON DELETE CASCADE,
    cv_id            UUID NOT NULL REFERENCES cvs (id) ON DELETE CASCADE,
    status           VARCHAR(20) NOT NULL DEFAULT 'pending'
                     CHECK (status IN ('pending', 'processing', 'completed', 'failed')),
    vector_score     REAL,          -- cosine similarity từ ChromaDB (lọc nhanh)
    overall_score    SMALLINT CHECK (overall_score BETWEEN 0 AND 100),   -- LLM chấm
    score_breakdown  JSONB,         -- {"skills": 80, "experience": 60, "education": 90, ...}
    matched_skills   JSONB,
    missing_skills   JSONB,
    explanation      TEXT,
    provider         VARCHAR(30),
    model_name       VARCHAR(100),
    prompt_version   VARCHAR(20),
    input_hash       CHAR(64),
    task_id          VARCHAR(255),
    error_message    TEXT,
    created_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
    completed_at     TIMESTAMPTZ,
    UNIQUE (job_id, cv_id)
);
CREATE INDEX idx_match_job_score ON match_results (job_id, overall_score DESC NULLS LAST);
CREATE INDEX idx_match_cv_score ON match_results (cv_id, overall_score DESC NULLS LAST);

-- (3) Job recommendation: danh sách gợi ý hiển thị cho ứng viên + phản hồi của họ
CREATE TABLE job_recommendations (
    id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cv_id            UUID NOT NULL REFERENCES cvs (id) ON DELETE CASCADE,
    job_id           UUID NOT NULL REFERENCES jobs (id) ON DELETE CASCADE,
    match_result_id  UUID REFERENCES match_results (id) ON DELETE SET NULL,
    rank             SMALLINT NOT NULL,
    final_score      SMALLINT CHECK (final_score BETWEEN 0 AND 100),
    reason           TEXT,          -- "Vì sao job này phù hợp với bạn"
    feedback         VARCHAR(20) NOT NULL DEFAULT 'new'
                     CHECK (feedback IN ('new', 'viewed', 'saved', 'applied', 'dismissed')),
    generated_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (cv_id, job_id)
);
CREATE INDEX idx_job_rec_cv_rank ON job_recommendations (cv_id, rank);

-- Log mọi lời gọi LLM/embedding: chi phí, độ trễ, lỗi, giới hạn lượt dùng theo user
CREATE TABLE llm_requests (
    id              BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    feature         VARCHAR(30) NOT NULL
                    CHECK (feature IN ('cv_analysis', 'cv_suggestion', 'job_recommendation',
                                       'candidate_matching', 'embedding', 'other')),
    provider        VARCHAR(30)  NOT NULL,
    model_name      VARCHAR(100) NOT NULL,
    prompt_version  VARCHAR(20),
    status          VARCHAR(10)  NOT NULL CHECK (status IN ('success', 'error')),
    input_tokens    INTEGER,
    output_tokens   INTEGER,
    cost_usd        NUMERIC(12,6),
    latency_ms      INTEGER,
    error_code      VARCHAR(50),    -- timeout, rate_limit, invalid_output...
    error_message   TEXT,
    request_hash    CHAR(64),
    user_id         UUID REFERENCES users (id) ON DELETE SET NULL,   -- ai kích hoạt
    object_type     VARCHAR(30),    -- 'cv_analysis' | 'match_result' | ...
    object_id       UUID,           -- id bản ghi kết quả tương ứng
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_llm_requests_feature ON llm_requests (feature, created_at DESC);
CREATE INDEX idx_llm_requests_user ON llm_requests (user_id, created_at DESC);
CREATE INDEX idx_llm_requests_object ON llm_requests (object_type, object_id);
