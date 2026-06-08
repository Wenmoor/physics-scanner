import re

from models.content import ContentSegment, ExtractedProblem

_INLINE_MATH = re.compile(r"\$([^$]+)\$")


def parse_inline_content(text: str) -> list[ContentSegment]:
    """将含 $LaTeX$ 的正文解析为文字/公式片段。"""
    segments: list[ContentSegment] = []
    last = 0
    for match in _INLINE_MATH.finditer(text):
        if match.start() > last:
            segments.append(ContentSegment(type="text", value=text[last : match.start()]))
        segments.append(ContentSegment(type="math", value=match.group(1).strip()))
        last = match.end()
    if last < len(text):
        segments.append(ContentSegment(type="text", value=text[last:]))
    return [s for s in segments if s.value]


def content_to_paragraphs(text: str) -> list[list[ContentSegment]]:
    blocks = [b.strip() for b in text.split("\n") if b.strip()]
    return [parse_inline_content(block) for block in blocks]


def build_problem_from_api(data: dict) -> ExtractedProblem:
    content = (data.get("content") or "").strip()
    paragraphs = content_to_paragraphs(content) if content else []

    if "handwriting_lines" in data:
        try:
            handwriting_lines = max(2, min(40, int(data["handwriting_lines"])))
        except (TypeError, ValueError):
            handwriting_lines = estimate_handwriting_lines(paragraphs)
    else:
        handwriting_lines = estimate_handwriting_lines(paragraphs)

    return ExtractedProblem(
        paragraphs=paragraphs,
        handwriting_lines=handwriting_lines,
    )


def estimate_handwriting_lines(paragraphs: list[list[ContentSegment]]) -> int:
    """根据题目篇幅粗略预估手写解析留白行数。"""
    char_count = sum(
        len(seg.value) for para in paragraphs for seg in para if seg.type == "text"
    )
    math_count = sum(1 for para in paragraphs for seg in para if seg.type == "math")
    base = 6
    base += char_count // 40
    base += math_count * 2
    return max(6, min(30, base))
