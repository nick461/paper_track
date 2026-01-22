# 配置管理模块

import logging
from pathlib import Path
from typing import Any, Dict, Optional

import yaml

from src.logging_config import get_logger

logger = get_logger(__name__)


class ConfigManager:
    """管理YAML文件的系统配置，支持默认值回退。"""

    # Default configuration values
    DEFAULT_CONFIG = {
        "llm": {
            "api_endpoint": "https://api.openai.com/v1/chat/completions",
            "api_key": "",
            "model": "gpt-4",
            "max_tokens": 4000,
            "temperature": 0.3,
            "max_content_length": -1,  # -1 means no limit
        },
        "search": {
            "default_category": "cs.AI",
            "default_days": 7,
            "default_max_results": 5,
            "classic": {
                "enabled": False,
                "years_back": 3,
                "use_scholar_api": False,
                "request_delay": 2.0,
                "min_citations": 10,
                "min_influential_citations": 5,
                "sort_by": "relevance"
            }
        },
        "output": {"directory": "./reports"},
        "logging": {"level": "INFO", "file": "./logs/paper_tracker.log"},
    }

    def __init__(self, config_path: str = "config.yaml"):
        self.config_path = Path(config_path)
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        if not self.config_path.exists():
            logger.warning(
                f"Configuration file not found: {self.config_path}. " "Using default configuration."
            )
            return self.DEFAULT_CONFIG.copy()

        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                loaded_config = yaml.safe_load(f)

            if loaded_config is None:
                logger.warning(
                    f"Configuration file is empty: {self.config_path}. "
                    "Using default configuration."
                )
                return self.DEFAULT_CONFIG.copy()

            # 合并加载的配置与默认值（默认值提供备用值）
            config = self._merge_configs(self.DEFAULT_CONFIG, loaded_config)
            logger.info(f"配置已从 {self.config_path} 成功加载")
            return config

        except yaml.YAMLError as e:
            logger.error(
                f"Error parsing YAML configuration file {self.config_path}: {e}. "
                "Using default configuration."
            )
            return self.DEFAULT_CONFIG.copy()
        except Exception as e:
            logger.error(
                f"Unexpected error loading configuration from {self.config_path}: {e}. "
                "Using default configuration."
            )
            return self.DEFAULT_CONFIG.copy()

    def _merge_configs(self, default: Dict[str, Any], loaded: Dict[str, Any]) -> Dict[str, Any]:
        merged = default.copy()

        for key, value in loaded.items():
            if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
                # Recursively merge nested dictionaries
                merged[key] = self._merge_configs(merged[key], value)
            else:
                # 用加载的值覆盖
                merged[key] = value

        return merged

    def get_llm_config(self) -> Dict[str, Any]:
        return self.config.get("llm", self.DEFAULT_CONFIG["llm"]).copy()

    def get_search_config(self) -> Dict[str, Any]:
        return self.config.get("search", self.DEFAULT_CONFIG["search"]).copy()

    def get_output_dir(self) -> str:
        output_config = self.config.get("output", self.DEFAULT_CONFIG["output"])
        return output_config.get("directory", self.DEFAULT_CONFIG["output"]["directory"])

    def get_logging_config(self) -> Dict[str, Any]:
        return self.config.get("logging", self.DEFAULT_CONFIG["logging"]).copy()

    def get_classic_config(self) -> Dict[str, Any]:
        search_config = self.config.get("search", self.DEFAULT_CONFIG["search"])
        classic_config = search_config.get(
            "classic",
            {
                "enabled": False,
                "years_back": 3,
                "min_citations": 10,
                "sort_by": "relevance"
            }
        )
        return classic_config.copy()

    def override_config(self, overrides: Dict[str, Any]) -> None:
        for key, value in overrides.items():
            if (
                key in self.config
                and isinstance(self.config[key], dict)
                and isinstance(value, dict)
            ):
                # Merge nested dictionaries
                self.config[key].update(value)
            else:
                # 直接覆盖
                self.config[key] = value

        logger.debug(f"配置被覆盖为: {overrides}")
