"""DOCX -> văn bản bằng thư viện chuẩn (zipfile + ElementTree), không cần python-docx.

Đọc header, nội dung chính (gồm cả bảng, text box) rồi footer theo đúng thứ tự xuất hiện; mỗi đoạn
văn một dòng. Nhiều CV đặt họ tên / liên hệ trong header nên không bỏ qua phần này.
"""
import re
import zipfile
from xml.etree import ElementTree

from . import CVParseError, ExtractedText

W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
MC_FALLBACK = '{http://schemas.openxmlformats.org/markup-compatibility/2006}Fallback'
MAIN_PART = 'word/document.xml'
HEADER_PART = re.compile(r'^word/header\d*\.xml$')
FOOTER_PART = re.compile(r'^word/footer\d*\.xml$')
# Chống zip bomb: tổng dung lượng XML giải nén được đọc
MAX_XML_SIZE = 30 * 1024 * 1024

BROKEN_MESSAGE = 'Không đọc được file DOCX (file hỏng hoặc không đúng định dạng).'


def extract_text(file) -> ExtractedText:
    try:
        with zipfile.ZipFile(file) as archive:
            names = archive.namelist()
            parts = (
                sorted(n for n in names if HEADER_PART.match(n))
                + [MAIN_PART]
                + sorted(n for n in names if FOOTER_PART.match(n))
            )
            infos = [archive.getinfo(name) for name in parts]
            if sum(info.file_size for info in infos) > MAX_XML_SIZE:
                raise CVParseError('File DOCX có cấu trúc bất thường (dung lượng giải nén quá lớn).')
            texts = [_part_text(ElementTree.fromstring(archive.read(info))) for info in infos]
    except CVParseError:
        raise
    except Exception as exc:  # BadZipFile, KeyError, ParseError, RecursionError...
        raise CVParseError(BROKEN_MESSAGE) from exc
    return ExtractedText(text='\n'.join(t for t in texts if t))


def _part_text(root) -> str:
    out: list[str] = []
    _render(root, out)
    return ''.join(out)


def _render(node, out: list[str]) -> None:
    for child in node:
        tag = child.tag
        if tag == MC_FALLBACK:
            continue  # bản dự phòng của mc:AlternateContent, trùng nội dung mc:Choice
        if tag == f'{W}t':
            out.append(child.text or '')
        elif tag == f'{W}tab':
            out.append('\t')
        elif tag in (f'{W}br', f'{W}cr'):
            out.append('\n')
        elif tag == f'{W}noBreakHyphen':
            out.append('-')
        else:
            _render(child, out)
            if tag == f'{W}p':
                out.append('\n')
