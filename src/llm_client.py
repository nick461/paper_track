"""LLM client module for Paper Tracker Analyzer.

This module handles communication with LLM APIs to generate paper analysis reports.
It includes prompt template management, API calls with retry logic, and error handling.
"""

import logging
import time
from typing import Dict, Any, Optional

import requests

from src.models import Paper
from src.logging_config import get_logger

logger = get_logger(__name__)


# Prompt template for paper analysis
PROMPT_TEMPLATE = """你是一位资深的学术研究专家。请仔细阅读以下论文并生成一份专业、详细的技术分析报告。

论文信息:
- 标题: {title}
- 作者: {authors}
- 发布日期: {published_date}
- arXiv ID: {arxiv_id}
- 分类: {categories}

论文内容:
{content}

请按照以下结构生成阅读报告，使用专业的学术语言，特别注重技术细节的描述:

## 1. 论文概述（详细版）
提供论文的全面概述（5-8句话），包括：
- 研究的核心问题和目标
- 提出的主要方法/模型的名称和基本思想
- 关键技术创新点
- 主要实验结果的量化指标
- 论文的主要贡献

## 2. 研究背景与动机
- 论文要解决什么具体问题？
- 为什么这个问题重要？有什么实际应用价值？
- 现有方法的局限性是什么？具体存在哪些技术瓶颈？
- 本文的研究动机和切入点是什么？

## 3. 核心方法（详细技术描述）
详细描述论文提出的方法、模型或算法，必须包括：

### 3.1 整体架构
- 模型/系统的整体架构设计
- 各个模块的功能和相互关系
- 数据流和处理流程

### 3.2 关键技术细节
- 核心算法的具体实现步骤
- **重要公式**：列出论文中的关键数学公式（使用 LaTeX 格式）
- **损失函数**：详细说明 loss 的组成，包括各项的含义和权重
- 模型的输入输出格式
- 特殊的技术技巧或优化策略

### 3.3 创新点分析
- 与现有方法的具体区别
- 技术上的突破点在哪里
- 为什么这些创新能够解决之前的问题

## 4. 实验设置与结果
### 4.1 实验设置
- 使用的数据集及其特点
- 评估指标的定义
- 对比的基线方法
- 实验的硬件和软件环境

### 4.2 主要结果
- 定量结果：列出关键性能指标的具体数值
- 与基线方法的详细对比（用表格形式呈现）
- 消融实验的结果和分析
- 可视化结果的关键发现

### 4.3 结果分析
- 为什么方法能取得这样的效果？
- 哪些因素对性能影响最大？
- 实验结果验证了哪些假设？

## 5. 创新点与贡献
列出论文的主要贡献（3-5点），每点都要具体说明：
- 技术创新的具体内容
- 相比现有工作的改进
- 对领域的影响和意义

## 6. 局限性与不足
客观分析论文存在的问题或局限：
- 方法本身的理论或技术限制
- 实验设计的不足
- 适用场景的限制
- 未解决的问题

请确保报告内容准确、客观、专业，特别注重技术细节的完整性。对于公式、算法步骤、loss 组成等关键技术内容，务必详细描述。避免过度解读或添加论文中未提及的内容。
"""


class LLMClient:
    def __init__(
        self,
        api_endpoint: str,
        api_key: str,
        model: str,
        max_tokens: int = 4000,
        temperature: float = 0.3,
        timeout: int = 60,
        max_content_length: int = -1,
    ):
        """
        Initialize the LLM client.

        Args:
            api_endpoint: URL endpoint for the LLM API
            api_key: Authentication key for the API
            model: Name of the LLM model to use
            max_tokens: Maximum tokens for generation (default: 4000)
            temperature: Sampling temperature (default: 0.3)
            timeout: Request timeout in seconds (default: 60)
            max_content_length: Maximum content length in characters (-1 for no limit, default: -1)
        """
        self.api_endpoint = api_endpoint
        self.api_key = api_key
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.timeout = timeout
        self.max_content_length = max_content_length

        limit_str = "unlimited" if max_content_length == -1 else str(max_content_length)
        logger.info(
            f"LLMClient initialized with model={model}, "
            f"max_tokens={max_tokens}, temperature={temperature}, "
            f"max_content_length={limit_str}"
        )

    def _build_prompt(self, paper: Paper, content: str, template: str = PROMPT_TEMPLATE) -> str:
        # Format authors list
        authors_str = ", ".join(paper.authors)

        # Format published date
        published_date_str = paper.published_date.strftime("%Y-%m-%d")

        # Format categories
        categories_str = ", ".join(paper.categories)

        # Build the prompt by filling in the template
        prompt = template.format(
            title=paper.title,
            authors=authors_str,
            published_date=published_date_str,
            arxiv_id=paper.arxiv_id,
            categories=categories_str,
            content=content,
        )

        logger.debug(
            f"Built prompt for paper {paper.arxiv_id}, "
            f"prompt length: {len(prompt)} characters"
        )

        return prompt

    def _call_api(self, prompt: str, max_retries: int = 3) -> str:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
        }

        for attempt in range(max_retries):
            try:
                logger.info(f"Calling LLM API (attempt {attempt + 1}/{max_retries})")

                start_time = time.time()
                response = requests.post(
                    self.api_endpoint, json=payload, headers=headers, timeout=self.timeout
                )
                elapsed_time = time.time() - start_time

                # Handle rate limiting (429 status code)
                if response.status_code == 429:
                    # Try to get retry-after header
                    retry_after = response.headers.get("Retry-After")
                    if retry_after:
                        wait_time = int(retry_after)
                    else:
                        # Exponential backoff: 2^attempt seconds
                        wait_time = 2 ** attempt

                    logger.warning(
                        f"Rate limit hit (429). Waiting {wait_time} seconds before retry."
                    )

                    if attempt < max_retries - 1:
                        time.sleep(wait_time)
                        continue
                    else:
                        raise requests.exceptions.RequestException(
                            f"Rate limit exceeded after {max_retries} attempts"
                        )

                # Raise exception for other HTTP errors
                response.raise_for_status()

                # Parse the response
                response_data = response.json()

                # Extract the generated text
                if "choices" not in response_data or len(response_data["choices"]) == 0:
                    raise ValueError("Invalid API response format: missing 'choices'")

                generated_text = response_data["choices"][0].get("message", {}).get("content", "")

                if not generated_text:
                    raise ValueError("API returned empty response")

                # Log success
                tokens_used = response_data.get("usage", {}).get("total_tokens", "unknown")
                logger.info(
                    f"LLM API call successful. "
                    f"Time: {elapsed_time:.2f}s, Tokens: {tokens_used}"
                )

                return generated_text

            except requests.exceptions.Timeout as e:
                logger.warning(f"API request timeout (attempt {attempt + 1}/{max_retries}): {e}")

                if attempt < max_retries - 1:
                    # Exponential backoff
                    wait_time = 2 ** attempt
                    logger.info(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    logger.error(f"API request failed after {max_retries} timeout attempts")
                    raise

            except requests.exceptions.RequestException as e:
                logger.warning(f"API request failed (attempt {attempt + 1}/{max_retries}): {e}")

                if attempt < max_retries - 1:
                    # Exponential backoff
                    wait_time = 2 ** attempt
                    logger.info(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    logger.error(f"API request failed after {max_retries} attempts")
                    raise

            except ValueError as e:
                # Don't retry on parsing errors
                logger.error(f"Failed to parse API response: {e}")
                raise

        # This should never be reached, but just in case
        raise requests.exceptions.RequestException(
            f"Failed to call API after {max_retries} attempts"
        )

    def analyze_paper(
        self, paper: Paper, content: str, prompt_template: str = PROMPT_TEMPLATE
    ) -> str:
        logger.info(f"Starting analysis for paper: {paper.arxiv_id}")

        # Limit content length to avoid token limits if configured
        if self.max_content_length > 0 and len(content) > self.max_content_length:
            logger.warning(
                f"Content length ({len(content)} chars) exceeds limit. "
                f"Truncating to {self.max_content_length} chars"
            )
            content = content[:self.max_content_length] + "\n\n[内容已截断...]"

        # Build the prompt
        prompt = self._build_prompt(paper, content, prompt_template)

        # Call the API
        try:
            analysis_text = self._call_api(prompt)
            logger.info(
                f"Successfully analyzed paper {paper.arxiv_id}. "
                f"Analysis length: {len(analysis_text)} characters"
            )
            return analysis_text

        except Exception as e:
            logger.error(f"Failed to analyze paper {paper.arxiv_id}: {e}")
            raise
