from typing import Literal

from pydantic import BaseModel, Field


class ContentSegment(BaseModel):
    type: Literal["text", "math"]
    value: str


class ExtractedProblem(BaseModel):
    """单道题目：正文（文字+公式）+ 手写留白行数预估。"""

    paragraphs: list[list[ContentSegment]] = Field(default_factory=list)
    handwriting_lines: int = Field(default=8, ge=2, le=40)
