# 错误处理模块 - 论文跟踪器分析器的错误处理

import logging
import time
from typing import Optional
import urllib.error
import requests

from src.logging_config import get_logger
from src.models import Paper

logger = get_logger(__name__)


class ErrorHandler:
    """论文跟踪器分析器系统的集中式错误处理器。

    def __init__(self, max_retries: int = 3, base_delay: float = 2.0):
        self.max_retries = max_retries
        self.base_delay = base_delay
        logger.info(
            f"ErrorHandler已初始化，最大重试次数={max_retries}，基础延迟={base_delay}秒"
        )

    def handle_network_error(
        self, error: Exception, context: str, operation: Optional[str] = None
    ) -> None:
        # Determine error type for detailed logging
        error_type = type(error).__name__
        error_message = str(error)

        # Build detailed log message
        log_parts = [
            f"Network error in {context}",
            f"Error type: {error_type}",
            f"Error message: {error_message}",
        ]

        if operation:
            log_parts.insert(1, f"Operation: {operation}")

        # Handle specific error types with appropriate logging
        if isinstance(error, urllib.error.HTTPError):
            log_parts.append(f"HTTP status code: {error.code}")
            if error.code == 429:
                logger.warning(" | ".join(log_parts) + " | Rate limit exceeded")
            elif error.code >= 500:
                logger.error(" | ".join(log_parts) + " | Server error")
            else:
                logger.error(" | ".join(log_parts) + " | Client error")

        elif isinstance(error, urllib.error.URLError):
            log_parts.append(f"Reason: {error.reason}")
            logger.error(" | ".join(log_parts) + " | URL error")

        elif isinstance(error, requests.exceptions.Timeout):
            logger.warning(" | ".join(log_parts) + " | Request timeout")

        elif isinstance(error, requests.exceptions.ConnectionError):
            logger.error(" | ".join(log_parts) + " | Connection failed")

        elif isinstance(error, requests.exceptions.RequestException):
            logger.error(" | ".join(log_parts) + " | Request exception")

        else:
            # Generic network error
            logger.error(" | ".join(log_parts))

        # Log additional context for debugging
        logger.debug(f"Full error details: {repr(error)}")

    def handle_parsing_error(
        self, error: Exception, paper: Paper, operation: Optional[str] = None
    ) -> None:
        """Handle parsing and content extraction errors.

        This method logs parsing errors with paper-specific context, allowing
        for better debugging and error tracking. It ensures that parsing failures
        are properly recorded without stopping the entire pipeline.

        Args:
            error: The exception that occurred during parsing
            paper: The Paper object being processed when the error occurred
            operation: Optional specific operation (e.g., "pdf_extraction", "text_cleaning")

        Validates: Requirements 7.1, 7.3
        """
        error_type = type(error).__name__
        error_message = str(error)

        # Build detailed log message with paper context
        log_parts = [
            f"Parsing error for paper {paper.arxiv_id}",
            f"Title: {paper.title[:50]}..." if len(paper.title) > 50 else f"Title: {paper.title}",
            f"Error type: {error_type}",
            f"Error message: {error_message}",
        ]

        if operation:
            log_parts.insert(1, f"Operation: {operation}")

        # Log the error with full context
        logger.warning(" | ".join(log_parts))

        # Log additional debugging information
        logger.debug(
            f"Paper details - Authors: {', '.join(paper.authors[:3])}, "
            f"Published: {paper.published_date}, "
            f"Categories: {', '.join(paper.categories)}"
        )
        logger.debug(f"Full error details: {repr(error)}")

        # Log that processing will continue
        logger.info(f"Continuing with next paper after parsing error for {paper.arxiv_id}")

    def should_retry(
        self, error: Exception, attempt: int, max_retries: Optional[int] = None
    ) -> tuple[bool, float]:
        """Determine if an operation should be retried based on the error type.

        This method implements intelligent retry logic with exponential backoff.
        It determines whether an error is recoverable and calculates the appropriate
        wait time before the next retry attempt.

        Args:
            error: The exception that occurred
            attempt: Current attempt number (0-indexed)
            max_retries: Optional override for max retries (uses instance default if None)

        Returns:
            Tuple of (should_retry: bool, wait_time: float)
            - should_retry: True if the operation should be retried
            - wait_time: Number of seconds to wait before retrying (0 if no retry)

        Validates: Requirements 7.1, 7.3
        """
        if max_retries is None:
            max_retries = self.max_retries

        # Check if we've exceeded max retries
        if attempt >= max_retries:
            logger.info(
                f"Max retries ({max_retries}) reached for {type(error).__name__}. " "Not retrying."
            )
            return False, 0.0

        # Determine if error is retryable
        retryable = False
        wait_time = 0.0

        # HTTP errors
        if isinstance(error, urllib.error.HTTPError):
            if error.code == 429:  # Rate limit
                retryable = True
                # Check for Retry-After header
                retry_after = error.headers.get("Retry-After")
                if retry_after:
                    try:
                        wait_time = float(retry_after)
                    except ValueError:
                        wait_time = self.base_delay * (2**attempt)
                else:
                    wait_time = self.base_delay * (2**attempt)
                logger.info(
                    f"Rate limit error (429). Will retry after {wait_time:.1f}s "
                    f"(attempt {attempt + 1}/{max_retries})"
                )

            elif error.code >= 500:  # Server errors
                retryable = True
                wait_time = self.base_delay * (2**attempt)
                logger.info(
                    f"Server error ({error.code}). Will retry after {wait_time:.1f}s "
                    f"(attempt {attempt + 1}/{max_retries})"
                )

            else:  # Client errors (4xx except 429)
                retryable = False
                logger.info(f"Client error ({error.code}). Not retrying.")

        # Timeout errors
        elif isinstance(error, (urllib.error.URLError, requests.exceptions.Timeout)):
            retryable = True
            wait_time = self.base_delay * (2**attempt)
            logger.info(
                f"Timeout/URL error. Will retry after {wait_time:.1f}s "
                f"(attempt {attempt + 1}/{max_retries})"
            )

        # Connection errors
        elif isinstance(error, requests.exceptions.ConnectionError):
            retryable = True
            wait_time = self.base_delay * (2**attempt)
            logger.info(
                f"Connection error. Will retry after {wait_time:.1f}s "
                f"(attempt {attempt + 1}/{max_retries})"
            )

        # Generic request exceptions
        elif isinstance(error, requests.exceptions.RequestException):
            # Some request exceptions are retryable
            retryable = True
            wait_time = self.base_delay * (2**attempt)
            logger.info(
                f"Request exception. Will retry after {wait_time:.1f}s "
                f"(attempt {attempt + 1}/{max_retries})"
            )

        # Non-network errors (parsing, validation, etc.)
        else:
            retryable = False
            logger.debug(f"Non-retryable error type: {type(error).__name__}. Not retrying.")

        return retryable, wait_time

    def execute_with_retry(self, operation_func, operation_name: str, *args, **kwargs):
        """Execute an operation with automatic retry logic.

        This is a convenience method that wraps an operation with retry logic,
        handling errors and waiting between attempts automatically.

        Args:
            operation_func: The function to execute
            operation_name: Name of the operation for logging
            *args: Positional arguments to pass to operation_func
            **kwargs: Keyword arguments to pass to operation_func

        Returns:
            The result of operation_func if successful

        Raises:
            The last exception encountered if all retries fail
        """
        last_error = None

        for attempt in range(self.max_retries + 1):
            try:
                logger.debug(
                    f"Executing {operation_name} (attempt {attempt + 1}/{self.max_retries + 1})"
                )
                result = operation_func(*args, **kwargs)

                if attempt > 0:
                    logger.info(f"{operation_name} succeeded after {attempt + 1} attempt(s)")

                return result

            except Exception as e:
                last_error = e
                should_retry, wait_time = self.should_retry(e, attempt)

                if should_retry:
                    self.handle_network_error(e, context=operation_name, operation=operation_name)

                    if wait_time > 0:
                        logger.info(f"Waiting {wait_time:.1f}s before retry...")
                        time.sleep(wait_time)
                else:
                    # Not retryable or max retries reached
                    raise

        # If we get here, all retries failed
        if last_error:
            raise last_error
