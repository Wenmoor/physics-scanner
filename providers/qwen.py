import base64
import mimetypes
from pathlib import Path

import dashscope
from dashscope import MultiModalConversation

from config import settings
from models.content import ExtractedProblem
from providers.base import VisionProvider
from services.content_parser import build_problem_from_api
from services.response_parser import parse_extraction_response

EXTRACTION_PROMPT = """请识别图片中的高中物理题目，原样转录题干内容。

要求：
1. 只转录题目文字和公式，不要分析、不要解答、不要标注知识点
2. 公式用 LaTeX，以 $...$ 嵌入正文，例如：由 $F=ma$ 可知
3. 多段文字用换行符 \\n 分隔
4. 预估学生手写解析所需留白行数 handwriting_lines（整数 6~30，题目越复杂数值越大）
5. 只输出 JSON，不要 markdown 代码块
6. JSON 字符串内的 LaTeX 反斜杠必须写成双反斜杠，例如 $\\frac{1}{2}$ 在 JSON 里写作 $\\\\frac{1}{2}$

JSON 格式：
{
  "content": "题目正文，公式用 $LaTeX$ 嵌入",
  "handwriting_lines": 12
}"""


def _encode_image(image_path: Path) -> str:
    mime_type, _ = mimetypes.guess_type(str(image_path))
    if not mime_type or not mime_type.startswith("image/"):
        mime_type = "image/jpeg"
    data = base64.b64encode(image_path.read_bytes()).decode("utf-8")
    return f"data:{mime_type};base64,{data}"


class QwenVisionProvider(VisionProvider):
    """千问多模态 API（DashScope MultiModalConversation）。"""

    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None,
        base_url: str | None = None,
    ) -> None:
        self.api_key = api_key or settings.dashscope_api_key
        self.model = model or settings.qwen_vl_model
        if base_url or settings.dashscope_base_url:
            dashscope.base_http_api_url = base_url or settings.dashscope_base_url

    def extract_problem(self, image_path: Path) -> ExtractedProblem:
        if not self.api_key:
            raise ValueError(
                "未配置 API Key。请在侧边栏填写并点击「保存设置」。"
            )

        messages = [
            {
                "role": "user",
                "content": [
                    {"image": _encode_image(image_path)},
                    {"text": EXTRACTION_PROMPT},
                ],
            }
        ]

        response = MultiModalConversation.call(
            api_key=self.api_key,
            model=self.model,
            messages=messages,
        )

        if response.status_code != 200:
            raise RuntimeError(
                f"千问 API 调用失败: {response.code} - {response.message}"
            )

        content = response.output.choices[0].message.content
        if isinstance(content, list):
            text_parts = [item.get("text", "") for item in content if "text" in item]
            raw_text = "\n".join(text_parts)
        else:
            raw_text = str(content)

        data = parse_extraction_response(raw_text)
        return build_problem_from_api(data)
