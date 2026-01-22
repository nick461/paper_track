# 日志配置 - 论文跟踪器分析器系统的日志配置

import logging
import os
from datetime import datetime
from pathlib import Path


def setup_logging(log_level: str = "INFO", log_dir: str = "logs") -> logging.Logger:
    # Create logs directory if it doesn't exist
    log_path = Path(log_dir)
    log_path.mkdir(parents=True, exist_ok=True)

    # Generate log filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = log_path / f"paper_tracker_{timestamp}.log"

    # Configure root logger
    logger = logging.getLogger("paper_tracker")
    logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))

    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()

    # Create formatters
    detailed_formatter = logging.Formatter(
        fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )

    console_formatter = logging.Formatter(fmt="%(levelname)s: %(message)s")

    # File handler - detailed logging
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(detailed_formatter)
    logger.addHandler(file_handler)

    # Console handler - less verbose
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    logger.info(f"日志已初始化。日志文件: {log_file}")

    return logger


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(f"paper_tracker.{name}")
