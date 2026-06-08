from pathlib import Path

from models.content import ExtractedProblem
from providers.base import VisionProvider
from services.content_parser import build_problem_from_api


class MockVisionProvider(VisionProvider):
    """无需 API Key 的演示模式。"""

    def extract_problem(self, image_path: Path) -> ExtractedProblem:
        return build_problem_from_api(
            {
                "content": (
                    "一物体从静止开始做匀加速直线运动，经过 $t=4\\,\\mathrm{s}$ 位移为 $s=32\\,\\mathrm{m}$，"
                    "求物体的加速度大小。\n"
                    "已知匀加速直线运动位移公式为 $s=\\frac{1}{2}at^2$。"
                ),
                "handwriting_lines": 14,
            }
        )
