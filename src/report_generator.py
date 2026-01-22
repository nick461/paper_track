# 报告生成模块 - 从论文分析结果创建结构化Markdown报告

import os
import re
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
import logging

from src.models import Paper, AnalysisResult


logger = logging.getLogger(__name__)


class ReportGenerator:
    """从论文分析结果生成结构化Markdown报告。

    def __init__(self, output_dir: str):
        self.output_dir = Path(output_dir)

        # 如果不存在则创建输出目录
        try:
            self.output_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"报告输出目录已初始化: {self.output_dir}")
        except OSError as e:
            logger.error(f"创建输出目录失败 {self.output_dir}: {e}")
            raise

    def _sanitize_filename(self, text: str, max_length: int = 50) -> str:
        # 转换为小写并用下划线替换空格
        sanitized = text.lower().replace(" ", "_")

        # 移除无效的文件名字符
        sanitized = re.sub(r"[^\w\-_]", "", sanitized)

        # 移除多个连续的下划线
        sanitized = re.sub(r"_+", "_", sanitized)

        # 修剪到最大长度
        if len(sanitized) > max_length:
            sanitized = sanitized[:max_length]

        # 移除末尾的下划线
        sanitized = sanitized.rstrip("_")

        return sanitized

    def generate_report(self, paper: Paper, analysis: str) -> str:
        # Generate filename: arxiv_id + sanitized_title
        sanitized_title = self._sanitize_filename(paper.title)
        filename = f"{paper.arxiv_id.replace('/', '_')}_{sanitized_title}.md"
        report_path = self.output_dir / filename

        # Format paper information
        authors_str = ", ".join(paper.authors)
        categories_str = ", ".join(paper.categories)
        published_str = paper.published_date.strftime("%Y-%m-%d")

        # Build the report content
        report_content = f"""# {paper.title}

## 论文基本信息

- **arXiv ID**: {paper.arxiv_id}
- **作者**: {authors_str}
- **发布日期**: {published_str}
- **分类**: {categories_str}
- **PDF链接**: {paper.pdf_url}
"""

        # Add optional fields if present
        if paper.journal_ref:
            report_content += f"- **期刊引用**: {paper.journal_ref}\n"

        if paper.comment:
            report_content += f"- **备注**: {paper.comment}\n"

        # Add abstract
        report_content += f"""
## 摘要

{paper.summary}

---

## 详细分析

{analysis}

---

*报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""

        # 将报告写入文件
        try:
            with open(report_path, "w", encoding="utf-8") as f:
                f.write(report_content)
            logger.info(f"报告生成成功: {report_path}")
            return str(report_path)
        except IOError as e:
            logger.error(f"无法将报告写入{report_path}: {e}")
            raise

    def generate_index(
        self, reports: List[Dict[str, any]], search_params: Optional[Dict[str, any]] = None
    ) -> str:
        index_path = self.output_dir / "index.md"

        # Build index content
        generation_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        index_content = f"""# 论文阅读报告索引

**生成时间**: {generation_time}
"""

        # Add search parameters if provided
        if search_params:
            index_content += f"""
## 搜索参数

- **研究领域**: {search_params.get('category', 'N/A')}
- **时间范围**: 最近 {search_params.get('days', 'N/A')} 天
- **论文数量**: {search_params.get('max_results', 'N/A')}
"""

        # Add report list
        index_content += f"""
## 报告列表

共处理 {len(reports)} 篇论文：

"""

        # Add each report entry
        for idx, report_info in enumerate(reports, 1):
            paper = report_info["paper"]
            report_path = Path(report_info["report_path"])

            # Get relative path for the link
            report_filename = report_path.name

            # Format authors (limit to first 3)
            authors_str = ", ".join(paper.authors[:3])
            if len(paper.authors) > 3:
                authors_str += " et al."

            # Format date
            published_str = paper.published_date.strftime("%Y-%m-%d")

            # Add entry
            index_content += (
                f"{idx}. [{paper.title}](./{report_filename}) - {authors_str} ({published_str})\n"
            )

        index_content += f"""
---

*索引文件生成于 {generation_time}*
"""

        # Write index to file
        try:
            with open(index_path, "w", encoding="utf-8") as f:
                f.write(index_content)
            logger.info(f"Index file generated successfully: {index_path}")
            return str(index_path)
        except IOError as e:
            logger.error(f"Failed to write index file to {index_path}: {e}")
            raise
