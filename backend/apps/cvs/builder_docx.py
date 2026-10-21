"""Dựng file DOCX từ nội dung CV tạo trên web (trình dựng CV).

Chỉ dùng thư viện chuẩn (zipfile) giống docx_parser nên không thêm phụ thuộc. Kết quả là CV thật: tải xuống,
gửi nhà tuyển dụng, bóc tách (cvs.parsers) và dùng cho AI như file ứng viên tự tải lên.
Đầu ra ổn định theo nội dung (cố định thời gian trong zip) để SHA-256 chỉ đổi khi nội dung CV đổi.
"""
import io
import re
import zipfile
from xml.sax.saxutils import escape

FONT = 'Arial'
ZIP_TIME = (2024, 1, 1, 0, 0, 0)
_CONTROL_CHARS = re.compile(r'[\x00-\x08\x0b-\x1f\x7f]')

SECTION_TITLES = {
    'summary': 'GIỚI THIỆU',
    'experiences': 'KINH NGHIỆM LÀM VIỆC',
    'educations': 'HỌC VẤN',
    'skills': 'KỸ NĂNG',
    'projects': 'DỰ ÁN',
}

_NS = 'xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"'
_CONTENT_TYPES = (
    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
    '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
    '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
    '<Default Extension="xml" ContentType="application/xml"/>'
    '<Override PartName="/word/document.xml" '
    'ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>'
    '<Override PartName="/word/styles.xml" '
    'ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>'
    '</Types>'
)
_ROOT_RELS = (
    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
    '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
    '<Relationship Id="rId1" '
    'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" '
    'Target="word/document.xml"/></Relationships>'
)
_DOCUMENT_RELS = (
    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
    '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
    '<Relationship Id="rId1" '
    'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>'
    '</Relationships>'
)
_STYLES = (
    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
    f'<w:styles {_NS}><w:docDefaults><w:rPrDefault><w:rPr>'
    f'<w:rFonts w:ascii="{FONT}" w:hAnsi="{FONT}" w:eastAsia="{FONT}" w:cs="{FONT}"/>'
    '<w:sz w:val="21"/><w:szCs w:val="21"/><w:lang w:val="vi-VN"/>'
    '</w:rPr></w:rPrDefault><w:pPrDefault><w:pPr><w:spacing w:after="80"/></w:pPr></w:pPrDefault></w:docDefaults>'
    '</w:styles>'
)


def _text(value) -> str:
    """Giá trị người dùng nhập -> chuỗi sạch (nội dung JSON có thể sai kiểu)."""
    if value is None or isinstance(value, (dict, list)):
        return ''
    return _CONTROL_CHARS.sub('', str(value)).strip()


def _items(content: dict, key: str) -> list[dict]:
    value = content.get(key)
    return [item for item in value if isinstance(item, dict)] if isinstance(value, list) else []


def _experiences(content: dict) -> list[dict]:
    items = [
        {k: _text(item.get(k)) for k in ('role', 'company', 'period', 'description')}
        for item in _items(content, 'experiences')
    ]
    return [i for i in items if i['role'] or i['company'] or i['description']]


def _educations(content: dict) -> list[dict]:
    items = [
        {k: _text(item.get(k)) for k in ('degree', 'school', 'period', 'description')}
        for item in _items(content, 'educations')
    ]
    return [i for i in items if i['degree'] or i['school'] or i['description']]


def _skills(content: dict) -> list[str]:
    return [s.strip() for s in _text(content.get('skills')).split(',') if s.strip()]


def has_content(content: dict) -> bool:
    """Đủ nội dung để thành một CV: có họ tên và ít nhất một mục."""
    return bool(_text(content.get('fullName'))) and bool(
        _text(content.get('summary'))
        or _experiences(content)
        or _educations(content)
        or _skills(content)
        or _text(content.get('projects'))
    )


def cv_title(content: dict) -> str:
    """Tên CV trong danh sách "CV của tôi", vd. "Nguyễn Văn An - Backend Developer"."""
    return ' - '.join(p for p in (_text(content.get('fullName')), _text(content.get('title'))) if p)[:150]


def _run(text: str, *, bold=False, size=None, color=None) -> str:
    props = ''.join(
        [
            '<w:b/>' if bold else '',
            f'<w:color w:val="{color}"/>' if color else '',
            f'<w:sz w:val="{size}"/><w:szCs w:val="{size}"/>' if size else '',
        ]
    )
    rpr = f'<w:rPr>{props}</w:rPr>' if props else ''
    return f'<w:r>{rpr}<w:t xml:space="preserve">{escape(text)}</w:t></w:r>'


def _paragraph(*runs: str, before=0, after=None, border=False, tab_right=False) -> str:
    props = ''
    if border:
        props += '<w:pBdr><w:bottom w:val="single" w:sz="6" w:space="1" w:color="2563EB"/></w:pBdr>'
    if tab_right:
        props += '<w:tabs><w:tab w:val="right" w:pos="10200"/></w:tabs>'
    spacing = f' w:before="{before}"' if before else ''
    spacing += f' w:after="{after}"' if after is not None else ''
    if spacing:
        props += f'<w:spacing{spacing}/>'
    ppr = f'<w:pPr>{props}</w:pPr>' if props else ''
    return f'<w:p>{ppr}{"".join(runs)}</w:p>'


def _lines(text: str) -> list[str]:
    """Mỗi dòng người dùng gõ là một đoạn văn (docx_parser cũng đọc theo từng đoạn)."""
    return [line.strip() for line in text.replace('\r\n', '\n').replace('\r', '\n').split('\n') if line.strip()]


def _heading(title: str) -> str:
    return _paragraph(_run(title, bold=True, size=24, color='2563EB'), before=240, after=80, border=True)


def _entry(primary: str, period: str, secondary: str, description: str) -> list[str]:
    head = [_run(primary or ' ', bold=True)]
    if period:
        head += ['<w:r><w:tab/></w:r>', _run(period)]
    out = [_paragraph(*head, before=100, after=20, tab_right=bool(period))]
    if secondary:
        out.append(_paragraph(_run(secondary, color='475569'), after=20))
    out += [_paragraph(_run(line), after=20) for line in _lines(description)]
    return out


def _body(content: dict) -> str:
    parts = [_paragraph(_run(_text(content.get('fullName')), bold=True, size=40), after=20)]
    if _text(content.get('title')):
        parts.append(_paragraph(_run(_text(content.get('title')), size=26, color='2563EB'), after=40))
    contact = [_text(content.get(k)) for k in ('email', 'phone', 'location', 'website')]
    if any(contact):
        parts.append(_paragraph(_run('  |  '.join(c for c in contact if c), color='475569')))

    if _text(content.get('summary')):
        parts.append(_heading(SECTION_TITLES['summary']))
        parts += [_paragraph(_run(line)) for line in _lines(_text(content.get('summary')))]
    if (experiences := _experiences(content)):
        parts.append(_heading(SECTION_TITLES['experiences']))
        for e in experiences:
            parts += _entry(e['role'], e['period'], e['company'], e['description'])
    if (educations := _educations(content)):
        parts.append(_heading(SECTION_TITLES['educations']))
        for e in educations:
            parts += _entry(e['degree'], e['period'], e['school'], e['description'])
    if (skills := _skills(content)):
        parts.append(_heading(SECTION_TITLES['skills']))
        parts.append(_paragraph(_run(', '.join(skills))))
    if _text(content.get('projects')):
        parts.append(_heading(SECTION_TITLES['projects']))
        parts += [_paragraph(_run(line)) for line in _lines(_text(content.get('projects')))]
    return ''.join(parts)


def render_docx(content: dict) -> bytes:
    document = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        f'<w:document {_NS}><w:body>{_body(content)}'
        '<w:sectPr><w:pgSz w:w="11906" w:h="16838"/>'
        '<w:pgMar w:top="850" w:right="850" w:bottom="850" w:left="850" w:header="400" w:footer="400" w:gutter="0"/>'
        '</w:sectPr></w:body></w:document>'
    )
    parts = {
        '[Content_Types].xml': _CONTENT_TYPES,
        '_rels/.rels': _ROOT_RELS,
        'word/document.xml': document,
        'word/_rels/document.xml.rels': _DOCUMENT_RELS,
        'word/styles.xml': _STYLES,
    }
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as archive:
        for name, xml in parts.items():
            info = zipfile.ZipInfo(name, date_time=ZIP_TIME)
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, xml.encode('utf-8'))
    return buffer.getvalue()
