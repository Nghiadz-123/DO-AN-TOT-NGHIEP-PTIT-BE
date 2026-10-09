"""PDF -> văn bản bằng pypdf (thuần Python, không cần cài thêm phần mềm hệ thống).

PDF dạng ảnh/scan không có lớp chữ nên trả về văn bản rỗng (OCR: giai đoạn sau).
"""
from pypdf import PdfReader
from pypdf.errors import PdfReadError

from . import CVParseError, ExtractedText

# CV thường 1-4 trang; giới hạn để file bất thường không làm chậm hệ thống
MAX_PAGES = 20

PASSWORD_MESSAGE = 'File PDF được đặt mật khẩu. Vui lòng tải lên bản không có mật khẩu.'
BROKEN_MESSAGE = 'Không đọc được file PDF (file hỏng hoặc cấu trúc không được hỗ trợ).'


def extract_text(file) -> ExtractedText:
    try:
        reader = PdfReader(file)
        # PDF chỉ đặt mật khẩu chủ sở hữu (hạn chế in/sửa) vẫn mở được bằng mật khẩu rỗng
        if reader.is_encrypted and not reader.decrypt(''):
            raise CVParseError(PASSWORD_MESSAGE)
        page_count = len(reader.pages)
        texts = [page.extract_text() or '' for page in reader.pages[:MAX_PAGES]]
    except CVParseError:
        raise
    except PdfReadError as exc:
        # pypdf báo lỗi giải mã bằng PdfReadError khi file cần mật khẩu người dùng
        message = PASSWORD_MESSAGE if 'decrypt' in str(exc).lower() else BROKEN_MESSAGE
        raise CVParseError(message) from exc
    except Exception as exc:  # file từ người dùng có thể gây đủ loại lỗi trong thư viện
        raise CVParseError(BROKEN_MESSAGE) from exc
    return ExtractedText(text='\n'.join(texts), page_count=page_count)
