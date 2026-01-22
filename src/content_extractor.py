# 内容提取模块 - 从PDF文件提取文本内容

import logging
import re
from pathlib import Path
from typing import Dict, Optional

import pdfplumber

logger = logging.getLogger(__name__)


class ContentExtractor:
    """从学术论文PDF中提取和处理文本内容。

    def __init__(self, max_pages: int = 50):
        self.max_pages = max_pages
        logger.info(f"ContentExtractor initialized with max_pages={max_pages}")

    def extract_text_from_pdf(self, pdf_path: str) -> str:
        pdf_file = Path(pdf_path)

        if not pdf_file.exists():
            error_msg = f"PDF file not found: {pdf_path}"
            logger.error(error_msg)
            raise FileNotFoundError(error_msg)

        try:
            with pdfplumber.open(pdf_path) as pdf:
                total_pages = len(pdf.pages)
                logger.info(f"Processing PDF with {total_pages} pages: {pdf_path}")

                # 确定提取哪些页面
                if total_pages <= self.max_pages:
                    # 对较小的PDF提取所有页面
                    pages_to_extract = range(total_pages)
                    logger.debug(f"正在提取所有{total_pages}页")
                else:
                    # 对于大PDF，只提取前10页和后5页
                    pages_to_extract = list(range(10)) + list(range(total_pages - 5, total_pages))
                    logger.warning(
                        f"PDF有{total_pages}页（>{self.max_pages}页）。"
                        f"仅提取前10页和后5页。"
                    )

                # 从选定页面提取文本
                extracted_text = []
                for page_num in pages_to_extract:
                    try:
                        page = pdf.pages[page_num]
                        text = page.extract_text()

                        if text:
                            # 清理提取的文本
                            cleaned_text = self._clean_text(text)
                            extracted_text.append(cleaned_text)
                            logger.debug(
                                f"从第{page_num + 1}页提取了{len(cleaned_text)}个字符"
                            )
                        else:
                            logger.warning(f"从第{page_num + 1}页未提取到文本")

                    except Exception as e:
                        logger.warning(f"从第{page_num + 1}页提取文本失败: {e}")
                        continue

                # 合并所有提取的文本
                full_text = "\n\n".join(extracted_text)

                if not full_text.strip():
                    error_msg = f"无法从PDF提取文本: {pdf_path}"
                    logger.error(error_msg)
                    raise Exception(error_msg)

                logger.info(
                    f"成功提取了{len(full_text)}个字符 "
                    f"来自{len(extracted_text)}页"
                )
                return full_text

        except FileNotFoundError:
            raise
        except Exception as e:
            error_msg = f"从PDF {pdf_path}提取文本失败: {e}"
            logger.error(error_msg)
            raise Exception(error_msg) from e

    def _clean_text(self, text: str) -> str:
        if not text:
            return ""

        # 将多个空格替换为单个空格
        text = re.sub(r" +", " ", text)

        # 修复换行符处的连字符单词（例如 "exam-\nple" -> "example"）
        text = re.sub(r"(\w+)-\n(\w+)", r"\1\2", text)

        # 修复破碎的句子（换行符后的小写字母表示继续）
        text = re.sub(r"([a-z,])\n([a-z])", r"\1 \2", text)

        # 将多个换行符标准化为双换行符（段落分隔）
        text = re.sub(r"\n{3,}", "\n\n", text)

        # 移除每行前后的空白字符
        lines = [line.strip() for line in text.split("\n")]
        text = "\n".join(lines)

        return text.strip()

    def extract_sections(self, text: str) -> Dict[str, str]:
        if not text:
            logger.warning("提供的文本为空，无法提取章节")
            return {"abstract": "", "introduction": "", "conclusion": ""}

        logger.info("尝试从论文文本中提取关键章节")
        sections = {"abstract": "", "introduction": "", "conclusion": ""}

        # 定义章节标题的模式（不区分大小写）
        section_patterns = {
            "abstract": [
                r"\n\s*abstract\s*\n",
                r"\n\s*summary\s*\n",
            ],
            "introduction": [
                r"\n\s*1\.?\s+introduction\s*\n",
                r"\n\s*introduction\s*\n",
                r"\n\s*1\.?\s+背景\s*\n",  # 中文：背景
            ],
            "conclusion": [
                r"\n\s*\d+\.?\s+conclusion[s]?\s*\n",
                r"\n\s*conclusion[s]?\s*\n",
                r"\n\s*\d+\.?\s+discussion\s*\n",
                r"\n\s*discussion\s*\n",
                r"\n\s*\d+\.?\s+总结\s*\n",  # 中文：结论
            ],
        }

        # 提取每个章节
        for section_name, patterns in section_patterns.items():
            section_text = self._extract_section_by_patterns(text, patterns)
            sections[section_name] = section_text

            if section_text:
                logger.debug(f"已提取{section_name}: {len(section_text)}个字符")
            else:
                logger.debug(f"无法识别{section_name}章节")

        return sections

    def _extract_section_by_patterns(
        self, text: str, patterns: list, max_length: int = 5000
    ) -> str:
        text_lower = text.lower()

        # 尝试每个模式
        for pattern in patterns:
            match = re.search(pattern, text_lower, re.IGNORECASE)
            if match:
                start_pos = match.end()

                # 找到此章节的结束位置（下一个章节标题或文本结尾）
                # 查找常见的章节标记
                next_section_pattern = r"\n\s*\d+\.?\s+[A-Z]"
                next_match = re.search(
                    next_section_pattern, text[start_pos : start_pos + max_length * 2]
                )

                if next_match:
                    end_pos = start_pos + next_match.start()
                else:
                    end_pos = start_pos + max_length

                # 提取并清理章节文本
                section_text = text[start_pos:end_pos].strip()

                # 限制最大长度
                if len(section_text) > max_length:
                    section_text = section_text[:max_length] + "..."

                return section_text

        return ""
