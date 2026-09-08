import os
from typing import Any

import yaml

DEFAULT_CONFIG: dict[str, Any] = {
    "version": "1.0",
    "app": {"name": "hermes", "port": 8080},
}


def _merge_configs(default: dict[str, Any], user: dict[str, Any]) -> dict[str, Any]:
    """Recursively merge user config into default config."""
    merged = default.copy()
    for key, value in user.items():
        if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
            merged[key] = _merge_configs(merged[key], value)
        else:
            merged[key] = value
    return merged


def load_config(path: str | None = None) -> dict[str, Any]:
    """
    Load configuration. Merges user YAML with built-in defaults.
    """
    if path is None:
        return DEFAULT_CONFIG.copy()

    if not os.path.exists(path):
        raise FileNotFoundError(f"Config file not found: {path}")

    with open(path, "r", encoding="utf-8") as f:
        user_config = yaml.safe_load(f) or {}

    return _merge_configs(DEFAULT_CONFIG, user_config)
