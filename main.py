#!/usr/bin/env python3
"""论文追踪分析器主入口。

提供命令行接口，编排arXiv论文搜索、下载、分析和报告生成的完整流程。
"""

import sys
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

import click

from src.config_manager import ConfigManager
from src.paper_fetcher import PaperFetcher
from src.content_extractor import ContentExtractor
from src.llm_client import LLMClient
from src.report_generator import ReportGenerator
from src.error_handler import ErrorHandler
from src.models import Paper, AnalysisResult
from src.logging_config import setup_logging, get_logger


logger = None


def process_paper(
    paper: Paper,
    fetcher: PaperFetcher,
    extractor: ContentExtractor,
    llm_client: LLMClient,
    report_generator: ReportGenerator,
    error_handler: ErrorHandler,
    pdf_dir: str
) -> Optional[Dict]:
    """处理单篇论文的完整流程。"""
    start_time = time.time()
    
    try:
        logger.info(f"Downloading PDF for: {paper.title}")
        pdf_path = fetcher.download_pdf(paper, pdf_dir)

        if not pdf_path:
            logger.error(f"Failed to download PDF for {paper.arxiv_id}")
            return None

        logger.info(f"Extracting text from PDF: {paper.arxiv_id}")
        try:
            content = extractor.extract_text_from_pdf(pdf_path)
        except Exception as e:
            error_handler.handle_parsing_error(e, paper, "pdf_extraction")
            return None

        logger.info(f"Analyzing paper with LLM: {paper.arxiv_id}")
        try:
            analysis = llm_client.analyze_paper(paper, content)
        except Exception as e:
            error_handler.handle_network_error(e, f"LLM analysis for {paper.arxiv_id}", "llm_api_call")
            return None

        logger.info(f"Generating report for: {paper.arxiv_id}")
        try:
            report_path = report_generator.generate_report(paper, analysis)
        except Exception as e:
            logger.error(f"Failed to generate report for {paper.arxiv_id}: {e}")
            return None
        
        processing_time = time.time() - start_time
        logger.info(
            f"Successfully processed {paper.arxiv_id} in {processing_time:.2f}s"
        )
        
        return {
            'paper': paper,
            'report_path': report_path,
            'processing_time': processing_time
        }
    
    except Exception as e:
        logger.error(f"Unexpected error processing {paper.arxiv_id}: {e}")
        return None


def main_workflow(
    category: str,
    days: int,
    max_results: int,
    output_dir: str,
    config_path: str,
    classic_mode: bool = False,
    years_back: int = 3,
    keywords: Optional[List[str]] = None
) -> int:
    """执行完整的论文追踪和分析工作流。"""
    global logger
    
    workflow_start_time = time.time()
    
    try:
        logger.info("Loading configuration...")
        config_manager = ConfigManager(config_path)

        config_manager.override_config({
            'search': {
                'default_category': category,
                'default_days': days,
                'default_max_results': max_results
            },
            'output': {
                'directory': output_dir
            }
        })

        llm_config = config_manager.get_llm_config()
        search_config = config_manager.get_search_config()
        classic_config = config_manager.get_classic_config()
        output_directory = config_manager.get_output_dir()

        if not llm_config.get('api_key'):
            logger.error(
                "LLM API key not configured. Please set it in config.yaml or "
                "as an environment variable."
            )
            return 1

        logger.info("Initializing modules...")
        fetcher = PaperFetcher(
            use_scholar_api=classic_config.get('use_scholar_api', True),
            request_delay=classic_config.get('request_delay', 1.0)
        )
        extractor = ContentExtractor()
        llm_client = LLMClient(
            api_endpoint=llm_config['api_endpoint'],
            api_key=llm_config['api_key'],
            model=llm_config['model'],
            max_tokens=llm_config.get('max_tokens', 4000),
            temperature=llm_config.get('temperature', 0.3),
            timeout=120,
            max_content_length=llm_config.get('max_content_length', -1)
        )
        report_generator = ReportGenerator(output_directory)
        error_handler = ErrorHandler()

        pdf_dir = Path(output_directory) / "pdfs"
        pdf_dir.mkdir(parents=True, exist_ok=True)

        if classic_mode:
            logger.info(
                f"Searching for classic papers in category '{category}' "
                f"from the last {years_back} years..."
            )
            if keywords:
                logger.info(f"Keywords: {', '.join(keywords)}")

            papers = fetcher.search_classic_papers(
                category=category,
                years_back=years_back,
                max_results=max_results,
                keywords=keywords,
                sort_by=classic_config.get('sort_by', 'relevance'),
                min_citations=classic_config.get('min_citations', 10),
                min_influential_citations=classic_config.get('min_influential_citations', 5)
            )
        else:
            logger.info(
                f"Searching for papers in category '{category}' "
                f"from the last {days} days..."
            )
            papers = fetcher.search_papers(
                category=category,
                days=days,
                max_results=max_results
            )

        if not papers:
            logger.warning("No papers found matching the search criteria.")
            return 0

        logger.info(f"Found {len(papers)} papers to process")

        successful_reports = []
        failed_papers = []

        click.echo(f"\n{'='*60}")
        click.echo(f"Processing {len(papers)} papers...")
        click.echo(f"{'='*60}\n")

        for idx, paper in enumerate(papers, 1):
            progress_pct = (idx / len(papers)) * 100
            click.echo(
                f"[{idx}/{len(papers)}] ({progress_pct:.0f}%) "
                f"Processing: {paper.title[:60]}..."
            )

            result = process_paper(
                paper=paper,
                fetcher=fetcher,
                extractor=extractor,
                llm_client=llm_client,
                report_generator=report_generator,
                error_handler=error_handler,
                pdf_dir=str(pdf_dir)
            )

            if result:
                successful_reports.append(result)
                click.echo(f"  Report generated: {Path(result['report_path']).name}")
            else:
                failed_papers.append(paper)
                click.echo(f"  Failed to process paper")

            click.echo()

        if successful_reports:
            logger.info("Generating index file...")
            search_params = {
                'category': category,
                'days': days,
                'max_results': max_results
            }
            index_path = report_generator.generate_index(
                successful_reports,
                search_params
            )
            logger.info(f"Index file generated: {index_path}")

        workflow_time = time.time() - workflow_start_time
        success_count = len(successful_reports)
        failure_count = len(failed_papers)

        click.echo(f"\n{'='*60}")
        click.echo("Execution Summary")
        click.echo(f"{'='*60}")
        click.echo(f"Successfully processed: {success_count} papers")
        click.echo(f"Failed: {failure_count} papers")
        click.echo(f"Total time: {workflow_time:.2f}s ({workflow_time/60:.1f} minutes)")
        click.echo(f"Output directory: {output_directory}")
        if successful_reports:
            click.echo(f"Index file: {Path(output_directory) / 'index.md'}")
        click.echo(f"{'='*60}\n")

        logger.info(
            f"Workflow completed - Success: {success_count}, "
            f"Failed: {failure_count}, Time: {workflow_time:.2f}s"
        )

        if failure_count > 0 and success_count == 0:
            return 1
        elif failure_count > 0:
            return 2
        else:
            return 0
    
    except KeyboardInterrupt:
        logger.warning("Workflow interrupted by user")
        click.echo("\n\nWorkflow interrupted by user.")
        return 130  # Standard exit code for SIGINT
    
    except Exception as e:
        logger.error(f"Fatal error in workflow: {e}", exc_info=True)
        click.echo(f"\n\nFatal error: {e}", err=True)
        return 1


@click.command()
@click.option('--category', default='cs.AI', help='arXiv分类 (如: cs.AI, cs.LG, cs.CV)', show_default=True)
@click.option('--days', default=7, type=int, help='搜索最近几天的论文', show_default=True)
@click.option('--max-results', default=5, type=int, help='最大处理论文数量', show_default=True)
@click.option('--output-dir', default='./reports', help='报告输出目录', show_default=True)
@click.option('--config', default='config.yaml', help='配置文件路径', show_default=True)
@click.option('--log-level', default='INFO', type=click.Choice(['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'], case_sensitive=False), help='日志级别', show_default=True)
@click.option('--classic', is_flag=True, help='启用经典论文搜索模式')
@click.option('--years-back', default=3, type=int, help='经典论文搜索回溯年数', show_default=True)
@click.option('--keywords', default=None, type=str, help='关键词 (逗号分隔)', show_default=False)
def cli(category, days, max_results, output_dir, config, log_level, classic, years_back, keywords):
    """论文追踪分析器 - 自动化学术论文分析工具。"""
    global logger

    logger = setup_logging(log_level=log_level)

    keyword_list = None
    if keywords:
        keyword_list = [kw.strip() for kw in keywords.split(',')]

    click.echo("\n" + "="*60)
    click.echo("Paper Tracker Analyzer v1.0")
    click.echo("="*60)
    click.echo(f"\nConfiguration:")
    click.echo(f"  Category: {category}")
    if classic:
        click.echo(f"  Mode: Classic Paper Search")
        click.echo(f"  Time range: Last {years_back} years")
        if keyword_list:
            click.echo(f"  Keywords: {', '.join(keyword_list)}")
    else:
        click.echo(f"  Mode: Recent Paper Search")
        click.echo(f"  Time range: Last {days} days")
    click.echo(f"  Max results: {max_results}")
    click.echo(f"  Output directory: {output_dir}")
    click.echo(f"  Config file: {config}")
    click.echo(f"  Log level: {log_level}")
    click.echo()

    exit_code = main_workflow(
        category=category,
        days=days,
        max_results=max_results,
        output_dir=output_dir,
        config_path=config,
        classic_mode=classic,
        years_back=years_back,
        keywords=keyword_list
    )

    sys.exit(exit_code)


if __name__ == '__main__':
    cli()
