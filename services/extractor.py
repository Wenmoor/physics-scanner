from pathlib import Path

from models.content import ExtractedProblem
from providers import get_provider
from services.docx_builder import build_docx


def process_images(
    image_paths: list[Path],
    provider_name: str | None = None,
    api_key: str | None = None,
    model: str | None = None,
    base_url: str | None = None,
    output_path: Path | None = None,
) -> tuple[list[ExtractedProblem], Path]:
    if not image_paths:
        raise ValueError("请至少上传一张图片")

    provider = get_provider(
        provider_name=provider_name,
        api_key=api_key,
        model=model,
        base_url=base_url,
    )
    problems: list[ExtractedProblem] = []

    for image_path in image_paths:
        problems.append(provider.extract_problem(image_path))

    docx_path = build_docx(problems, output_path=output_path)
    return problems, docx_path


def process_image(
    image_path: Path,
    provider_name: str | None = None,
    api_key: str | None = None,
    model: str | None = None,
    base_url: str | None = None,
    output_path: Path | None = None,
) -> tuple[ExtractedProblem, Path]:
    problems, docx_path = process_images(
        [image_path],
        provider_name=provider_name,
        api_key=api_key,
        model=model,
        base_url=base_url,
        output_path=output_path,
    )
    return problems[0], docx_path
