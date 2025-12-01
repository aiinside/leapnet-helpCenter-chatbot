import os
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, Optional

import yaml
from pydantic import BaseModel, Field


class LogSettings(BaseModel):
    directory: Path = Field(default=Path("logs"))
    system_file: str = Field(default="system.log")
    request_file: str = Field(default="requests.log")

class Settings(BaseModel):
    api_endpoint: str
    api_key: str
    stg_api_endpoint: str
    stg_api_key: str
    log: LogSettings = Field(default_factory=LogSettings)


CONFIG_ENV_VAR = "APP_CONFIG_PATH"
DEFAULT_CONFIG_FILE = Path(__file__).resolve().with_name("settings.yml")


def _load_config_file(config_path: Path) -> Dict[str, Any]:
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with config_path.open("r", encoding="utf-8") as file:
        return yaml.safe_load(file) or {}


@lru_cache()
def get_settings(config_path: Optional[Path] = None) -> Settings:
    target_path = config_path or Path(os.getenv(CONFIG_ENV_VAR, DEFAULT_CONFIG_FILE))
    data = _load_config_file(target_path)
    settings = Settings(**data)
    settings.log.directory.mkdir(parents=True, exist_ok=True)
    return settings
