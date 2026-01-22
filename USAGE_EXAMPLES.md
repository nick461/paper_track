# Paper Tracker Analyzer 使用示例

本文档提供了 Paper Tracker Analyzer 的详细使用示例，包括最近论文搜索和经典论文搜索两种模式。

## 目录

- [基础用法](#基础用法)
- [最近论文搜索模式](#最近论文搜索模式)
- [经典论文搜索模式](#经典论文搜索模式)
- [如何判断论文是否经典](#如何判断论文是否经典)
- [深度学习相关论文搜索](#深度学习相关论文搜索)
- [脑网络分析相关论文搜索](#脑网络分析相关论文搜索)
- [配置文件说明](#配置文件说明)

---

## 基础用法

### 命令行选项

| 选项            | 说明                                              | 默认值        |
| --------------- | ------------------------------------------------- | ------------- |
| `--category`    | arXiv 分类（如 cs.AI, cs.LG, cs.CV）              | `cs.AI`       |
| `--days`        | 搜索最近几天的论文                                | `7`           |
| `--max-results` | 最多处理几篇论文                                  | `5`           |
| `--output-dir`  | 报告输出目录                                      | `./reports`   |
| `--config`      | 配置文件路径                                      | `config.yaml` |
| `--log-level`   | 日志级别（DEBUG, INFO, WARNING, ERROR, CRITICAL） | `INFO`        |
| `--classic`     | 启用经典论文搜索模式                              | `False`       |
| `--years-back`  | 经典论文搜索的时间范围（年）                      | `3`           |
| `--keywords`    | 经典论文搜索的关键词（逗号分隔）                  | `None`        |

---

## 最近论文搜索模式

### 示例 1：搜索最近 7 天的 AI 论文

```bash
python main.py --category cs.AI --days 7 --max-results 5
```

### 示例 2：搜索最近 3 天的机器学习论文

```bash
python main.py --category cs.LG --days 3 --max-results 3
```

### 示例 3：搜索最近 14 天的计算机视觉论文，自定义输出目录

```bash
python main.py --category cs.CV --days 14 --max-results 10 --output-dir ./cv_reports
```

### 示例 4：搜索最近 5 天的自然语言处理论文，启用调试日志

```bash
python main.py --category cs.CL --days 5 --max-results 5 --log-level DEBUG
```

---

## 经典论文搜索模式

经典论文搜索模式用于查找在过去几年中发表的、具有影响力的论文。由于 arXiv 不直接提供引用数据，该模式使用相关性排序和关键词匹配来识别潜在的经典论文。

### 示例 1：搜索最近 3 年的经典 AI 论文

```bash
python main.py --category cs.AI --classic --years-back 3 --max-results 5
```

### 示例 2：搜索最近 5 年的经典机器学习论文

```bash
python main.py --category cs.LG --classic --years-back 5 --max-results 10
```

### 示例 3：使用关键词搜索经典论文

```bash
python main.py --category cs.LG --classic --years-back 3 --keywords "deep learning,neural network" --max-results 5
```

### 示例 4：搜索最近 2 年的经典计算机视觉论文

```bash
python main.py --category cs.CV --classic --years-back 2 --max-results 8
```

---

## 深度学习相关论文搜索

### 最近论文搜索

#### 示例 1：搜索最近的深度学习论文（机器学习分类）

```bash
python main.py --category cs.LG --days 7 --max-results 5
```

#### 示例 2：搜索最近的神经网络论文

```bash
python main.py --category cs.NE --days 7 --max-results 5
```

#### 示例 3：搜索最近的人工智能论文

```bash
python main.py --category cs.AI --days 7 --max-results 5
```

### 经典论文搜索

#### 示例 1：搜索最近 3 年的经典深度学习论文

```bash
python main.py --category cs.LG --classic --years-back 3 --keywords "deep learning,neural network" --max-results 5
```

#### 示例 2：搜索最近 5 年的经典卷积神经网络论文

```bash
python main.py --category cs.CV --classic --years-back 5 --keywords "CNN,convolutional neural network" --max-results 5
```

#### 示例 3：搜索最近 3 年的经典 Transformer 论文

```bash
python main.py --category cs.LG --classic --years-back 3 --keywords "Transformer,attention mechanism" --max-results 5
```

#### 示例 4：搜索最近 3 年的经典生成对抗网络论文

```bash
python main.py --category cs.CV --classic --years-back 3 --keywords "GAN,generative adversarial network" --max-results 5
```

#### 示例 5：搜索最近 3 年的经典强化学习论文

```bash
python main.py --category cs.AI --classic --years-back 3 --keywords "reinforcement learning,RL" --max-results 5
```

---

## 脑网络分析相关论文搜索

脑网络分析通常涉及神经科学、医学成像和机器学习的交叉领域。以下是一些相关的搜索示例：

### 最近论文搜索

#### 示例 1：搜索最近的神经网络论文（可能与脑网络相关）

```bash
python main.py --category cs.NE --days 7 --max-results 5
```

#### 示例 2：搜索最近的机器学习论文（可能包含脑网络分析方法）

```bash
python main.py --category cs.LG --days 7 --max-results 5
```

### 经典论文搜索

#### 示例 1：搜索最近 3 年的经典脑网络分析论文

```bash
python main.py --category cs.NE --classic --years-back 3 --keywords "brain network,connectome" --max-results 5
```

#### 示例 2：搜索最近 3 年的经典 fMRI 脑网络论文

```bash
python main.py --category cs.NE --classic --years-back 3 --keywords "fMRI,functional MRI,brain connectivity" --max-results 5
```

#### 示例 3：搜索最近 3 年的经典图神经网络在脑网络分析中的应用

```bash
python main.py --category cs.LG --classic --years-back 3 --keywords "graph neural network,GNN,brain network" --max-results 5
```

#### 示例 4：搜索最近 3 年的经典脑网络深度学习论文

```bash
python main.py --category cs.NE --classic --years-back 3 --keywords "deep learning,brain network,neuroimaging" --max_results 5
```

#### 示例 5：搜索最近 3 年的经典脑网络拓扑分析论文

```bash
python main.py --category cs.NE --classic --years-back 3 --keywords "brain topology,network analysis,graph theory" --max_results 5
```

#### 示例 6：搜索最近 3 年的经典脑网络疾病诊断论文

```bash
python main.py --category cs.NE --classic --years-back 3 --keywords "brain disorder,disease diagnosis,neurological disease" --max_results 5
```

#### 示例 7：搜索最近 3 年的经典脑网络动态分析论文

```bash
python main.py --category cs.NE --classic --years-back 3 --keywords "dynamic brain network,temporal connectivity" --max_results 5
```

#### 示例 8：搜索最近 3 年的经典多模态脑网络分析论文

```bash
python main.py --category cs.NE --classic --years-back 3 --keywords "multimodal brain network,fusion,DTI" --max_results 5
```

---

## 如何判断论文是否经典

本系统提供两种方式来判断论文是否经典：

### 方式 1：使用 Semantic Scholar API（基于引用数据）⚠️

**注意**：Semantic Scholar API 有严格的请求频率限制，容易遇到 429 错误。因此默认情况下此功能已禁用。

如果启用此功能，系统会：
1. 查询论文的引用数据
2. 根据引用数判断是否经典

**判断标准**：

论文被认为是"经典"需要同时满足以下两个条件：

1. **总引用数**（`citation_count`）≥ `min_citations`（默认：10）
2. **影响力引用数**（`influentialCitationCount`）≥ `min_influential_citations`（默认：5）

### 什么是影响力引用？

影响力引用（Influential Citation）是指那些被 Semantic Scholar 识别为具有重要学术价值的引用。这些引用通常来自：
- 高影响力期刊或会议
- 被广泛认可的作者
- 具有创新性的研究

### 工作流程

```
1. 从 arXiv 搜索论文
   ↓
2. 获取论文标题
   ↓
3. 调用 Semantic Scholar API 查询引用数据
   ↓
4. 检查是否满足经典标准
   ↓
5. 返回符合条件的经典论文
```

### 配置选项

在 [`config.yaml`](config.yaml) 中可以调整经典论文的判断标准：

```yaml
search:
  classic:
    # 是否使用 Semantic Scholar API
    # true: 使用引用数据（可能遇到 429 错误）
    # false: 仅使用相关性排序（默认，推荐）
    use_scholar_api: false

    # 最小总引用数（仅在使用 Semantic Scholar API 时有效）
    min_citations: 10

    # 最小影响力引用数（仅在使用 Semantic Scholar API 时有效）
    min_influential_citations: 5
```

### 方式 2：使用相关性排序（默认）✅

**推荐使用**：这是默认配置，不会遇到 429 错误。

系统使用以下方法来识别潜在的经典论文：
- 相关性排序（relevance）
- 关键词匹配
- 按最后更新时间排序

虽然不如引用数据准确，但：
- ✅ 速度快，无 API 限制
- ✅ 不会遇到 429 错误
- ✅ 适合大多数使用场景

### 调整建议

根据不同的研究领域和时间范围，可以调整这些阈值：

#### 深度学习领域（高引用）
```yaml
min_citations: 50
min_influential_citations: 20
```

#### 脑网络分析（中等引用）
```yaml
min_citations: 10
min_influential_citations: 5
```

#### 新兴领域（低引用）
```yaml
min_citations: 5
min_influential_citations: 2
```

#### 时间范围较短（如最近 1 年）
```yaml
min_citations: 3
min_influential_citations: 1
```

### 禁用 Semantic Scholar API

如果不想使用 Semantic Scholar API（例如网络受限或 API 不可用），可以禁用它：

```yaml
search:
  classic:
    use_scholar_api: false
```

禁用后，系统将使用以下方法来识别潜在的经典论文：
- 相关性排序（relevance）
- 关键词匹配
- 按最后更新时间排序

**注意**：禁用 Semantic Scholar API 后，判断准确性会降低，建议仅在必要时使用。

### 示例

#### 示例 1：搜索高引用的经典深度学习论文

```bash
# 修改 config.yaml
search:
  classic:
    min_citations: 100
    min_influential_citations: 50

# 运行搜索
python main.py --category cs.LG --classic --years-back 5 --keywords "deep learning" --max-results 5
```

#### 示例 2：搜索中等引用的脑网络分析论文

```bash
# 使用默认配置（min_citations: 10, min_influential_citations: 5）
python main.py --category cs.NE --classic --years-back 3 --keywords "brain network" --max-results 5
```

#### 示例 3：搜索新兴领域的论文（降低阈值）

```bash
# 修改 config.yaml
search:
  classic:
    min_citations: 5
    min_influential_citations: 2

# 运行搜索
python main.py --category cs.AI --classic --years-back 2 --max-results 5
```

### 日志输出

当使用 Semantic Scholar API 时，系统会在日志中输出引用信息：

```
INFO - Searching arXiv for classic papers in category 'cs.LG' from the last 3 years...
INFO - Keywords: deep learning, neural network
INFO - Using Semantic Scholar API for citation filtering (min_citations: 10, min_influential: 5)
DEBUG - Searching Semantic Scholar for: Attention Is All You Need...
DEBUG - Found paper: Attention Is All You Need, citations: 45000
INFO - Classic paper identified: 'Attention Is All You Need...' (citations: 45000, influential: 12000)
INFO - Found 5 classic papers matching criteria
```

### 限制和注意事项

1. **默认模式**：系统默认使用相关性排序（`use_scholar_api: false`），不会遇到 429 错误
2. **API 限制**：Semantic Scholar API 有严格的请求频率限制，大量搜索可能需要较长时间
3. **429 错误（请求频率限制）**：如果启用 API 后遇到 429 错误，可以：
   - 增加 `request_delay` 配置（默认 2.0 秒，可增加到 3.0-5.0 秒）
   - 系统会自动重试（最多 3 次，使用指数退避策略）
   - 或者禁用 API（推荐）
4. **论文匹配**：系统通过标题匹配论文，如果标题不完全匹配，可能无法获取引用数据
5. **新论文**：最近发表的论文可能还没有足够的引用数，即使质量很高
6. **网络依赖**：需要互联网连接才能访问 Semantic Scholar API

### 处理 429 错误

如果遇到大量的 429 错误，有以下几个解决方案：

**方案 1：增加请求延迟（推荐）**

在 [`config.yaml`](config.yaml:53) 中增加请求延迟：

```yaml
search:
  classic:
    request_delay: 3.0  # 增加到 3 秒或更多
```

默认值已设置为 2.0 秒，如果仍然遇到 429 错误，可以尝试：
- `2.0` 秒（默认）
- `3.0` 秒（更保守）
- `5.0` 秒（非常保守，但速度较慢）

**方案 2：禁用 Semantic Scholar API（最快）**

如果不需要精确的引用数据，可以禁用 API：

```yaml
search:
  classic:
    use_scholar_api: false
```

禁用后，系统将使用相关性排序来识别潜在的经典论文。

**方案 3：减少搜索数量**

减少同时处理的论文数量：

```bash
python main.py --category cs.NE --classic --years-back 3 --max-results 3
```

**方案 4：分批搜索**

先搜索少量论文，等待一段时间后再搜索更多：

```bash
# 第一次搜索
python main.py --category cs.NE --classic --years-back 3 --max-results 3

# 等待几分钟或几小时...

# 第二次搜索
python main.py --category cs.NE --classic --years-back 3 --max-results 3
```

---

## 配置文件说明

### config.yaml 配置项

```yaml
# LLM Configuration
llm:
  api_endpoint: "https://api.siliconflow.cn/v1/chat/completions"
  api_key: "your-api-key"
  model: "Pro/zai-org/GLM-4.7"
  max_tokens: 10000
  temperature: 0.3
  max_content_length: -1  # -1 表示无限制

# Search Configuration
search:
  default_category: "cs.AI"
  default_days: 7
  default_max_results: 3

  # Classic Papers Configuration
  classic:
    enabled: false
    years_back: 3
    min_citations: 10
    sort_by: "relevance"

# Output Configuration
output:
  directory: "./reports"

# Logging Configuration
logging:
  level: "INFO"
  file: "./logs/paper_tracker.log"
```

### 关键配置说明

#### LLM 配置
- `max_content_length`: 控制发送给 LLM 的内容长度
  - `-1`: 无限制（推荐用于长论文）
  - 正数: 限制字符数（如 `15000`）

#### 经典论文配置
- `enabled`: 是否启用经典论文搜索（默认 false，通过命令行 `--classic` 覆盖）
- `years_back`: 时间范围（年）
- `sort_by`: 排序方式
  - `relevance`: 相关性排序（默认）
  - `lastUpdatedDate`: 按最后更新时间排序
  - `submittedDate`: 按提交时间排序

---

## 常用搜索组合

### 深度学习领域

```bash
# 最近的深度学习论文
python main.py --category cs.LG --days 7 --max-results 5

# 经典的深度学习论文
python main.py --category cs.LG --classic --years-back 3 --keywords "deep learning" --max-results 5

# 经典的 CNN 论文
python main.py --category cs.CV --classic --years-back 5 --keywords "CNN,convolutional" --max-results 5

# 经典的 Transformer 论文
python main.py --category cs.LG --classic --years-back 3 --keywords "Transformer,attention" --max-results 5
```

### 脑网络分析领域

```bash
# 最近的脑网络论文
python main.py --category cs.NE --days 7 --max-results 5

# 经典的脑网络分析论文
python main.py --category cs.NE --classic --years-back 3 --keywords "brain network,connectome" --max-results 5

# 经典的 fMRI 脑网络论文
python main.py --category cs.NE --classic --years-back 3 --keywords "fMRI,functional connectivity" --max_results 5

# 经典的图神经网络脑网络论文
python main.py --category cs.LG --classic --years-back 3 --keywords "GNN,brain network" --max-results 5
```

---

## 提示和技巧

1. **选择合适的分类**：
   - 深度学习：`cs.LG`（机器学习）、`cs.NE`（神经网络）、`cs.CV`（计算机视觉）
   - 脑网络分析：`cs.NE`（神经网络）、`cs.LG`（机器学习）

2. **关键词选择**：
   - 使用英文关键词，因为 arXiv 主要是英文论文
   - 可以使用同义词，如 "brain network" 和 "connectome"
   - 对于特定方法，可以使用缩写和全称，如 "CNN" 和 "convolutional neural network"

3. **时间范围**：
   - 最近论文：使用 `--days` 参数（如 7 天、14 天）
   - 经典论文：使用 `--years-back` 参数（如 2 年、3 年、5 年）

4. **结果数量**：
   - 初次搜索可以使用较小的 `--max-results`（如 3-5）
   - 确认搜索效果后可以增加结果数量（如 10-20）

5. **日志级别**：
   - 正常使用：`INFO`
   - 调试问题：`DEBUG`
   - 只看错误：`ERROR`

---

## 故障排除

### 问题：找不到论文

**可能原因**：
- 分类不正确
- 时间范围太窄
- 关键词太具体

**解决方案**：
- 检查分类是否正确（参考 `ARXIV_CATEGORIES.md`）
- 增加时间范围（如 `--days 14` 或 `--years-back 5`）
- 使用更通用的关键词

### 问题：LLM API 调用失败

**可能原因**：
- API key 未配置或无效
- 网络连接问题
- API 服务不可用

**解决方案**：
- 检查 `config.yaml` 中的 `api_key`
- 检查网络连接
- 稍后重试

### 问题：内容被截断

**可能原因**：
- `max_content_length` 设置太小

**解决方案**：
- 在 `config.yaml` 中设置 `max_content_length: -1`（无限制）
- 或设置更大的值（如 `30000`）

---

## 更多帮助

- 查看 [ARXIV_CATEGORIES.md](ARXIV_CATEGORIES.md) 了解所有可用的 arXiv 分类
- 查看 [README.md](README.md) 了解项目概述
- 查看 [config.yaml](config.yaml) 了解配置选项
