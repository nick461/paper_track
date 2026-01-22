# 论文获取模块 - 从arXiv检索论文

import logging
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional
import urllib.request
import urllib.error

import arxiv

from src.models import Paper
from src.logging_config import get_logger
from src.scholar_client import ScholarClient

logger = get_logger(__name__)


class PaperFetcher:
    """从arXiv获取论文，支持搜索、下载和元数据提取。"""

    def __init__(self, use_scholar_api: bool = True, request_delay: float = 1.0):
        self.client = arxiv.Client()
        self.use_scholar_api = use_scholar_api
        if use_scholar_api:
            self.scholar_client = ScholarClient()
            self.scholar_client.request_delay = request_delay
            logger.info(
                f"已初始化用于引用数据的Semantic Scholar API客户端 "
                f"(请求延迟: {request_delay}秒)"
            )
        else:
            self.scholar_client = None
            logger.info("Semantic Scholar API已禁用 - 使用基于相关性的排序")

    def search_papers(
        self, category: str, days: int, max_results: int, sort_by: str = "submittedDate"
    ) -> List[Paper]:
        logger.info(
            f"正在类别'{category}'中搜索arXiv论文 "
            f"来自最近{days}天，最多结果: {max_results}"
        )

        # 计算日期范围（使用时区感知的datetime）
        from datetime import timezone

        end_date = datetime.now(timezone.utc)
        start_date = end_date - timedelta(days=days)

        # 构建类别搜索查询
        query = f"cat:{category}"

        # 确定排序顺序
        if sort_by == "submittedDate":
            sort_order = arxiv.SortCriterion.SubmittedDate
        elif sort_by == "lastUpdatedDate":
            sort_order = arxiv.SortCriterion.LastUpdatedDate
        else:
            logger.warning(f"未知的sort_by值'{sort_by}'，默认为'submittedDate'")
            sort_order = arxiv.SortCriterion.SubmittedDate

        try:
            # 创建搜索对象
            search = arxiv.Search(
                query=query,
                max_results=max_results * 2,  # 获取更多结果以按日期筛选
                sort_by=sort_order,
                sort_order=arxiv.SortOrder.Descending,
            )

            papers = []

            # 获取并筛选结果
            for result in self.client.results(search):
                # 按日期范围筛选
                if result.published >= start_date and result.published <= end_date:
                    paper = self.extract_metadata(result)
                    papers.append(paper)

                    # 如果有足够的论文就停止
                    if len(papers) >= max_results:
                        break

            logger.info(f"找到{len(papers)}篇匹配条件的论文")

            if len(papers) == 0:
                logger.warning(
                    f"在类别'{category}'中最近{days}天未找到论文"
                )

            return papers

        except arxiv.ArxivError as e:
            logger.error(f"arXiv API错误: {e}")
            return []
        except Exception as e:
            logger.error(f"论文搜索过程中发生意外错误: {e}")
            return []

    def search_classic_papers(
        self,
        category: str,
        years_back: int,
        max_results: int,
        keywords: Optional[List[str]] = None,
        sort_by: str = "relevance",
        min_citations: int = 10,
        min_influential_citations: int = 5
    ) -> List[Paper]:
        """
        Search for classic papers on arXiv by category, time range, and keywords.

        This method searches for influential papers published within a specified
        time range, optionally filtered by keywords. If Semantic Scholar API is
        enabled, it uses citation data to identify classic papers. Otherwise,
        it uses relevance ranking and keyword matching.

        Args:
            category: arXiv category (e.g., "cs.AI", "cs.LG")
            years_back: Search for papers from the last N years
            max_results: Maximum number of papers to return
            keywords: Optional list of keywords to search for (e.g., ["deep learning", "neural network"])
            sort_by: Sort criterion ("relevance", "lastUpdatedDate", "submittedDate")
            min_citations: Minimum citation count to consider a paper as classic
            min_influential_citations: Minimum influential citation count to consider a paper as classic

        Returns:
            List of Paper objects matching the search criteria

        Validates:
            Requirements for classic paper search functionality
        """
        logger.info(
            f"Searching arXiv for classic papers in category '{category}' "
            f"from the last {years_back} years, max results: {max_results}"
        )

        if keywords:
            logger.info(f"Keywords: {', '.join(keywords)}")

        if self.use_scholar_api:
            logger.info(
                f"Using Semantic Scholar API for citation filtering "
                f"(min_citations: {min_citations}, min_influential: {min_influential_citations})"
            )
        else:
            logger.info("Semantic Scholar API disabled - using relevance-based ranking")

        # Calculate date range (use timezone-aware datetime)
        from datetime import timezone

        end_date = datetime.now(timezone.utc)
        start_date = end_date - timedelta(days=years_back * 365)

        # Build search query
        # Combine category with keywords if provided
        if keywords and len(keywords) > 0:
            # Join keywords with OR for broader search
            keyword_query = " OR ".join([f'all:{kw}' for kw in keywords])
            query = f"cat:{category} AND ({keyword_query})"
        else:
            query = f"cat:{category}"

        # Determine sort order
        if sort_by == "relevance":
            sort_order = arxiv.SortCriterion.Relevance
        elif sort_by == "lastUpdatedDate":
            sort_order = arxiv.SortCriterion.LastUpdatedDate
        elif sort_by == "submittedDate":
            sort_order = arxiv.SortCriterion.SubmittedDate
        else:
            logger.warning(f"Unknown sort_by value '{sort_by}', defaulting to 'relevance'")
            sort_order = arxiv.SortCriterion.Relevance

        try:
            # Create search object
            # Fetch more results to allow for filtering and ranking
            search = arxiv.Search(
                query=query,
                max_results=max_results * 5,  # Fetch more to filter by date and citations
                sort_by=sort_order,
                sort_order=arxiv.SortOrder.Descending,
            )

            papers = []
            seen_titles = set()  # To avoid duplicates

            # Fetch and filter results
            for result in self.client.results(search):
                # Filter by date range
                if result.published >= start_date and result.published <= end_date:
                    # Avoid duplicates
                    title_lower = result.title.lower().strip()
                    if title_lower in seen_titles:
                        continue
                    seen_titles.add(title_lower)

                    # If using Semantic Scholar API, check citation count
                    if self.use_scholar_api and self.scholar_client:
                        is_classic = self.scholar_client.is_classic_paper(
                            result.title,
                            min_citations=min_citations,
                            min_influential_citations=min_influential_citations
                        )

                        if not is_classic:
                            logger.debug(f"Paper filtered out (low citations): {result.title[:50]}...")
                            continue

                    paper = self.extract_metadata(result)
                    papers.append(paper)

                    # Stop if we have enough papers
                    if len(papers) >= max_results:
                        break

            logger.info(f"Found {len(papers)} classic papers matching criteria")

            if len(papers) == 0:
                logger.warning(
                    f"No classic papers found for category '{category}' "
                    f"in the last {years_back} years"
                )
                if self.use_scholar_api:
                    logger.warning(
                        "Try reducing the citation thresholds or increasing the time range"
                    )

            return papers

        except arxiv.ArxivError as e:
            logger.error(f"arXiv API error: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error during classic paper search: {e}")
            return []

    def download_pdf(self, paper: Paper, output_dir: str) -> Optional[str]:
        """
        Download the PDF for a paper.

        Args:
            paper: Paper object containing PDF URL
            output_dir: Directory to save the PDF

        Returns:
            Path to the downloaded PDF file, or None if download failed

        Validates:
            Requirements 2.1, 2.4
        """
        logger.info(f"Downloading PDF for paper: {paper.arxiv_id}")

        # Create output directory if it doesn't exist
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # Generate filename
        safe_title = "".join(
            c if c.isalnum() or c in (" ", "-", "_") else "_" for c in paper.title
        )[
            :100
        ]  # Limit filename length
        filename = f"{paper.arxiv_id.replace('/', '_')}_{safe_title}.pdf"
        pdf_path = output_path / filename

        try:
            # Download PDF with retry logic
            max_retries = 3
            retry_delay = 2  # seconds

            for attempt in range(max_retries):
                try:
                    urllib.request.urlretrieve(paper.pdf_url, pdf_path)
                    logger.info(f"Successfully downloaded PDF to: {pdf_path}")
                    return str(pdf_path)

                except urllib.error.HTTPError as e:
                    if e.code == 429:  # Rate limit
                        if attempt < max_retries - 1:
                            wait_time = retry_delay * (2**attempt)
                            logger.warning(f"Rate limit hit, waiting {wait_time}s before retry")
                            time.sleep(wait_time)
                        else:
                            raise
                    else:
                        raise

        except Exception as e:
            logger.error(
                f"Failed to download PDF for {paper.arxiv_id}: {e}. " "Continuing with next paper."
            )
            return None

    def extract_metadata(self, result: arxiv.Result) -> Paper:
        """
        Extract metadata from an arxiv.Result object.

        Args:
            result: arxiv.Result object from the arXiv API

        Returns:
            Paper object with all metadata fields populated

        Validates:
            Requirement 2.2
        """
        # Extract author names
        authors = [author.name for author in result.authors]

        # Extract categories
        categories = result.categories

        # Create Paper object
        paper = Paper(
            arxiv_id=result.entry_id.split("/abs/")[-1],  # Extract ID from URL
            title=result.title,
            authors=authors,
            published_date=result.published,
            updated_date=result.updated,
            summary=result.summary,
            categories=categories,
            pdf_url=result.pdf_url,
            comment=result.comment if hasattr(result, "comment") else None,
            journal_ref=result.journal_ref if hasattr(result, "journal_ref") else None,
        )

        logger.debug(f"Extracted metadata for paper: {paper.arxiv_id}")

        return paper
