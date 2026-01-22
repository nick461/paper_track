# 论文追踪分析器

自动化学术论文搜索、下载和分析工具。

## 功能

- 按分类和时间范围搜索arXiv论文
- 自动下载PDF并提取文本
- 使用LLM生成专业阅读报告
- 支持经典论文搜索（基于引用数或关键词）
- 生成结构化Markdown报告

## 安装

```bash
# 安装依赖
pip install -r requirements.txt

# 复制配置文件
cp config.yaml config.yaml
```

在 `config.yaml` 中配置LLM API密钥。

## 使用

### 基本用法

```bash
# 搜索最近7天的AI论文
python main.py --category cs.AI --days 7 --max-results 5

# 搜索经典机器学习论文
python main.py --category cs.LG --classic --years-back 3 --max-results 5

# 使用关键词搜索
python main.py --category cs.NE --classic --keywords "brain network,connectome"
```

### 参数说明

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--category` | arXiv分类 | `cs.AI` |
| `--days` | 搜索最近N天的论文 | `7` |
| `--max-results` | 最大处理论文数 | `5` |
| `--classic` | 启用经典论文搜索模式 | `False` |
| `--years-back` | 经典论文回溯年数 | `3` |
| `--keywords` | 关键词（逗号分隔） | `None` |
| `--output-dir` | 报告输出目录 | `./reports` |

### arXiv分类

常见分类：
- `cs.AI` - 人工智能
- `cs.LG` - 机器学习
- `cs.CV` - 计算机视觉
- `cs.CL` - 计算语言学
- `cs.NE` - 神经网络

完整分类列表见 `ARXIV_CATEGORIES.md`。

## 配置

`config.yaml` 主要配置项：

```yaml
llm:
  api_endpoint: "https://api.siliconflow.cn/v1/chat/completions"
  api_key: "your-api-key"
  model: "Pro/zai-org/GLM-4.7"
  max_tokens: 20000
  temperature: 0.3

search:
  default_category: "cs.AI"
  default_days: 7
  default_max_results: 3
  classic:
    use_scholar_api: false  # Semantic Scholar API有严格限流，默认关闭
    min_citations: 10       # 最小引用数
```

## 输出

- PDF文件：`reports/pdfs/`
- 阅读报告：`reports/*.md`
- 索引文件：`reports/index.md`
- 日志文件：`logs/paper_tracker_*.log`

## 注意事项

- Semantic Scholar API有严格请求限制，如遇429错误请将 `use_scholar_api` 设为 `false`
- 默认使用相关性排序，不依赖引用数据
- 大型PDF只提取前10页和后5页
- LLM分析可能需要较长时间，请耐心等待

## 开发

```bash
# 运行测试
pytest

# 代码格式化
black src/ tests/

# 类型检查
mypy src/
```

## 项目结构

```
paper_track/
├── main.py                 # 主入口
├── config.yaml             # 配置文件
├── requirements.txt        # 依赖
└── src/
    ├── models.py           # 数据模型
    ├── config_manager.py   # 配置管理
    ├── paper_fetcher.py    # 论文搜索
    ├── content_extractor.py # PDF提取
    ├── llm_client.py       # LLM调用
    ├── report_generator.py # 报告生成
    ├── scholar_client.py   # 引用数据
    ├── error_handler.py    # 错误处理
    └── logging_config.py   # 日志配置
```
