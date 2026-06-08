from abc import ABC, abstractmethod
from pathlib import Path

from models.content import ExtractedProblem


class VisionProvider(ABC):
    @abstractmethod
    def extract_problem(self, image_path: Path) -> ExtractedProblem:
        """从错题图片中提取结构化内容。"""
