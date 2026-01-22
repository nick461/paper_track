# 论文跟踪器分析器的数据模型

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional


@dataclass
class Paper:
    """表示来自arXiv的学术论文及其元数据。

    arxiv_id: str
    title: str
    authors: List[str]
    published_date: datetime
    updated_date: datetime
    summary: str
    categories: List[str]
    pdf_url: str
    comment: Optional[str] = None
    journal_ref: Optional[str] = None

    def __str__(self) -> str:
        authors_str = ", ".join(self.authors[:3])
        if len(self.authors) > 3:
            authors_str += f" et al. ({len(self.authors)} authors)"

        return (
            f"Paper: {self.title}\n"
            f"Authors: {authors_str}\n"
            f"arXiv ID: {self.arxiv_id}\n"
            f"Published: {self.published_date.strftime('%Y-%m-%d')}"
        )

    def __repr__(self) -> str:
        return (
            f"Paper(arxiv_id={self.arxiv_id!r}, "
            f"title={self.title!r}, "
            f"authors={self.authors!r}, "
            f"published_date={self.published_date!r}, "
            f"updated_date={self.updated_date!r}, "
            f"summary={self.summary[:50]!r}..., "
            f"categories={self.categories!r}, "
            f"pdf_url={self.pdf_url!r}, "
            f"comment={self.comment!r}, "
            f"journal_ref={self.journal_ref!r})"
        )


@dataclass
class AnalysisResult:
    """表示使用LLM分析论文的结果。

    paper: Paper
    analysis_text: str
    report_path: str
    generated_at: datetime
    tokens_used: Optional[int] = None
    processing_time: float = 0.0

    def __str__(self) -> str:
        return (
            f"Analysis Result for: {self.paper.title}\n"
            f"Report saved to: {self.report_path}\n"
            f"Generated at: {self.generated_at.strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"Processing time: {self.processing_time:.2f}s"
        )

    def __repr__(self) -> str:
        return (
            f"AnalysisResult(paper={self.paper.arxiv_id!r}, "
            f"analysis_text={self.analysis_text[:50]!r}..., "
            f"report_path={self.report_path!r}, "
            f"generated_at={self.generated_at!r}, "
            f"tokens_used={self.tokens_used!r}, "
            f"processing_time={self.processing_time!r})"
        )
