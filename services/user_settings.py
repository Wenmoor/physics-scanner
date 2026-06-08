import json
from pathlib import Path
from typing import Any

SETTINGS_DIR = Path(".local")
SETTINGS_FILE = SETTINGS_DIR / "user_settings.json"

DEFAULTS: dict[str, Any] = {
    "dashscope_api_key": "",
    "dashscope_base_url": "https://dashscope.aliyuncs.com/api/v1",
    "qwen_vl_model": "qwen-vl-max",
    "ai_provider": "qwen",
}


def load_user_settings() -> dict[str, Any]:
    data = DEFAULTS.copy()
    if SETTINGS_FILE.exists():
        try:
            stored = json.loads(SETTINGS_FILE.read_text(encoding="utf-8"))
            if isinstance(stored, dict):
                data.update({k: stored[k] for k in DEFAULTS if k in stored})
        except (json.JSONDecodeError, OSError):
            pass
    return data


def save_user_settings(data: dict[str, Any]) -> None:
    payload = {key: data.get(key, DEFAULTS[key]) for key in DEFAULTS}
    SETTINGS_DIR.mkdir(parents=True, exist_ok=True)
    SETTINGS_FILE.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
