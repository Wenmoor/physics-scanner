from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    dashscope_api_key: str = ""
    dashscope_base_url: str = "https://dashscope.aliyuncs.com/api/v1"
    qwen_vl_model: str = "qwen-vl-max"
    ai_provider: str = "qwen"

    output_dir: Path = Path("output")

    # B5 活页纸（176×250 mm），左侧留出装订孔边距
    page_width_mm: float = 176.0
    page_height_mm: float = 250.0
    margin_left_mm: float = 25.0
    margin_right_mm: float = 15.0
    margin_top_mm: float = 20.0
    margin_bottom_mm: float = 20.0


settings = Settings()
