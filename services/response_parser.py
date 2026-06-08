import json
import re

_JSON_FENCE = re.compile(r"```(?:json)?\s*([\s\S]*?)\s*```", re.IGNORECASE)
_HANDWRITING_RE = re.compile(r'"handwriting_lines"\s*:\s*(\d+)', re.IGNORECASE)


def _strip_fence(text: str) -> str:
    text = text.strip()
    match = _JSON_FENCE.search(text)
    return match.group(1).strip() if match else text


def _repair_latex_backslashes_in_json_strings(text: str) -> str:
    """将 JSON 字符串值里 LaTeX 的反斜杠补成双反斜杠。"""
    out: list[str] = []
    i = 0
    in_string = False

    while i < len(text):
        ch = text[i]
        if not in_string:
            out.append(ch)
            if ch == '"':
                in_string = True
            i += 1
            continue

        if ch == "\\":
            if i + 1 >= len(text):
                out.append("\\\\")
                i += 1
                continue

            nxt = text[i + 1]
            if nxt == "u" and i + 5 < len(text):
                out.append(text[i : i + 6])
                i += 6
                continue

            if nxt in '"\\/':
                out.append(ch)
                out.append(nxt)
                i += 2
                continue

            if nxt in "bfnrt" and (i + 2 >= len(text) or not text[i + 2].isalpha()):
                out.append(ch)
                out.append(nxt)
                i += 2
                continue

            if nxt.isalpha():
                out.append("\\\\")
                i += 1
                continue

            out.append("\\\\")
            i += 1
            continue

        if ch == '"':
            out.append('"')
            in_string = False
            i += 1
            continue

        out.append(ch)
        i += 1

    return "".join(out)


def _extract_json_string_value(text: str, key: str) -> str | None:
    """从可能损坏的 JSON 中提取某个字符串字段的值。"""
    pattern = re.compile(rf'"{re.escape(key)}"\s*:\s*"', re.IGNORECASE)
    match = pattern.search(text)
    if not match:
        return None

    i = match.end()
    chars: list[str] = []
    while i < len(text):
        ch = text[i]
        if ch == '"':
            break
        if ch == "\\" and i + 1 < len(text):
            nxt = text[i + 1]
            if nxt == "n":
                chars.append("\n")
            elif nxt == "t":
                chars.append("\t")
            elif nxt == "r":
                chars.append("\r")
            elif nxt == '"':
                chars.append('"')
            elif nxt == "\\":
                chars.append("\\")
            elif nxt == "/":
                chars.append("/")
            else:
                chars.append(nxt)
            i += 2
            continue
        chars.append(ch)
        i += 1

    return "".join(chars)


def _fallback_parse(text: str) -> dict:
    content = _extract_json_string_value(text, "content")
    if content is None:
        content = text.strip()

    handwriting_lines = 8
    hw_match = _HANDWRITING_RE.search(text)
    if hw_match:
        try:
            handwriting_lines = int(hw_match.group(1))
        except ValueError:
            pass

    return {
        "content": content,
        "handwriting_lines": handwriting_lines,
    }


def parse_extraction_response(text: str) -> dict:
    text = _strip_fence(text)

    for candidate in (text, _repair_latex_backslashes_in_json_strings(text)):
        try:
            data = json.loads(candidate)
            if isinstance(data, dict):
                return data
        except json.JSONDecodeError:
            continue

    return _fallback_parse(text)
