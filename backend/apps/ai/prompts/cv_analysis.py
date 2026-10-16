"""Prompt bóc tách cấu trúc CV và chấm điểm CV (lấy từ prototype TestAI/prompts.py).

So với TestAI chỉ đổi phần ví dụ / mô tả tiêu chí cho mọi ngành nghề (hệ thống là web tìm việc đa ngành) và
yêu cầu trả lời tiếng Việt; schema, thang điểm và trọng số giữ nguyên. Sửa ở đây để tinh chỉnh chất lượng.
"""

CV_SCHEMA = """{
  "full_name": str, "email": str|null, "phone": str|null, "location": str|null,
  "title": str,                      // vị trí/chức danh mong muốn hoặc hiện tại
  "summary": str,
  "years_of_experience": number,
  "skills": [str],                   // kỹ năng chuẩn hoá, viết thường, vd "bán hàng", "excel", "autocad", "chăm sóc khách hàng"
  "experiences": [{"company": str, "position": str, "start": str, "end": str, "description": str}],
  "educations": [{"school": str, "degree": str, "major": str, "start": str, "end": str, "gpa": str|null}],
  "projects": [{"name": str, "tech": [str], "description": str}],   // tech: công cụ / công nghệ / phương pháp đã dùng
  "certifications": [str],
  "languages": [str]
}"""

PARSE_CV_SYSTEM = (
    'Bạn là hệ thống ATS. Trích xuất thông tin từ CV thành JSON đúng schema sau, '
    'không bịa thông tin; trường nào không có thì để null hoặc mảng rỗng. Chỉ trả JSON.\n' + CV_SCHEMA
)

# khóa -> (tên tiêu chí hiển thị, điểm tối đa, mô tả cho model). Tổng điểm tối đa = 100.
SCORE_CRITERIA = {
    'completeness': ('Đầy đủ thông tin', 20, 'đủ thông tin liên hệ, học vấn, kinh nghiệm, kỹ năng'),
    'experience': ('Kinh nghiệm', 25, 'độ liên quan, mô tả có kết quả đo lường được'),
    'skills': ('Kỹ năng', 20, 'rõ ràng, phù hợp chức danh'),
    'projects': ('Dự án / thành tích', 15, 'có dự án, thành tích hoặc hoạt động nổi bật, mô tả rõ vai trò, công cụ và kết quả'),
    'presentation': ('Trình bày', 20, 'ngắn gọn, nhất quán, dùng động từ hành động'),
}

SCORE_CV_SYSTEM = (
    'Bạn là chuyên gia tuyển dụng. Chấm điểm chất lượng CV (không so với JD cụ thể) theo thang 0-100.\n'
    'CV có thể thuộc bất kỳ ngành nghề nào (bán lẻ, sản xuất, y tế, giáo dục, khách sạn, công nghệ...): '
    'đánh giá theo chuẩn của chính ngành nghề đó.\n'
    'Tiêu chí và trọng số:\n'
    + '\n'.join(f'- {key} ({maximum}): {description}' for key, (_, maximum, description) in SCORE_CRITERIA.items())
    + '\nViết strengths, weaknesses bằng tiếng Việt.\n'
    'Trả JSON: {"total": number, "breakdown": {'
    + ', '.join(f'"{key}": n' for key in SCORE_CRITERIA)
    + '},\n"strengths": [str], "weaknesses": [str]}'
)
