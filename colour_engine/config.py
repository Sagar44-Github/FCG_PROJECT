"""Single source of truth for initial project parameters."""
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "config.json"

def load_config() -> dict:
    with CONFIG_PATH.open(encoding="utf-8") as stream:
        return json.load(stream)

CONFIG = load_config()
