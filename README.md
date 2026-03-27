# split-text

> 将长文本按语义拆分为较小片段的工具

## 项目介绍

`split-text` 是一个 Python 工具，用于将长文本按语义拆分为指定大小的片段。它特别适用于需要处理大量中文文本的场景，例如：

- **RAG 文档处理**：将长文档拆分为适合 LLM 处理的 chunks
- **数据预处理**：将大文本拆分为便于存储和检索的小片段
- **文本分析**：将文档拆分为可管理的处理单元

### 核心特性

- **语义感知拆分**：优先按段落和句子拆分，保持语义完整性
- **中文支持**：基于 jieba 分词进行中文文本处理
- **灵活配置**：支持自定义最大长度、最小片段长度、合并策略等
- **多种接口**：提供 API 和 CLI 两种使用方式

## 技术选型

### 核心技术

| 技术 | 版本 | 说明 |
|------|------|------|
| Python | >= 3.10 | 项目运行环境 |
| jieba | >= 0.42 | 中文分词库，用于拆分超长句子 |
| click | >= 8.1 | CLI 框架，提供命令行接口 |

### 设计模式

- **模块化设计**：核心拆分逻辑与 CLI 分离
- **面向对象**：使用 `TextSplitter` 类封装拆分逻辑
- **数据类**：使用 `SplitResult` 封装返回结果

## 项目结构

```
split-text/
├── src/
│   └── split_text/
│       ├── __init__.py          # 包入口
│       ├── splitter.py          # 核心拆分逻辑
│       └── cli.py               # 命令行接口
├── tests/
│   └── test_splitter.py         # 单元测试
├── examples/
│   └── demo.py                  # 用例示例
├── pyproject.toml              # 项目配置
└── README.md                    # 项目文档
```

## 功能设计

### 1. 核心拆分算法

```
输入文本
    ↓
按段落拆分 (双换行符分隔)
    ↓
对每个段落:
    ├─ 如果 ≤ max_length → 直接返回
    └─ 如果 > max_length → 按句子拆分
        ↓
        按句子结束标记 (。！？) 拆分
        ↓
        合并句子为片段:
        ├─ 当前片段 + 新句子 ≤ max_length → 合并
        └─ 否则 → 保存当前片段，开始新片段
    ↓
超长句子处理:
    ├─ 纯英文 → 按空格拆分
    └─ 中文 → 使用 jieba 分词后合并
    ↓
合并短片段 (可选)
    ↓
输出结果
```

### 2. API 接口

#### Python API

```python
from split_text import split_text, TextSplitter

# 便捷函数
result = split_text(text, max_length=200)

# 或使用类
splitter = TextSplitter(max_length=200, min_chunk_length=50)
result = splitter.split(text)

# 访问结果
for chunk in result.chunks:
    print(chunk)

print(f"片段数量: {result.metadata['chunk_count']}")
```

#### CLI 接口

```bash
# 拆分文本
echo "你的文本" | split-text split -l 200

# 拆分文件
split-text file input.txt -l 200

# 预览拆分结果
split-text preview "你的文本" -l 100
```

### 3. 配置参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `max_length` | 200 | 单个片段的最大字符数 |
| `min_chunk_length` | 50 | 合并短片段的最小长度阈值 |
| `merge_short` | True | 是否合并过短的片段 |

## 使用方法

### 安装

```bash
# 使用 uv (推荐)
uv sync

# 或安装到全局
uv pip install -e .
```

### Python 使用

```python
from split_text import split_text

text = """人工智能（Artificial Intelligence，简称AI）是计算机科学的一个分支，
它试图理解智能的本质，并生产出一种新的能以人类智能相似的方式做出反应的智能机器。

机器学习是人工智能的核心，是使计算机具有智能的根本途径。"""

result = split_text(text, max_length=100)
print(f"拆分为 {result.metadata['chunk_count']} 个片段")
for i, chunk in enumerate(result.chunks, 1):
    print(f"[{i}] {chunk}")
```

### 命令行使用

```bash
# 从 stdin 读取
echo "这是测试文本。" | split-text split -l 50

# 拆分文件
split-text file article.txt -o output/

# 预览效果
split-text preview "你的文本" -l 100

# 查看帮助
split-text --help
split-text split --help
```

## 开发计划

### Phase 1: 核心功能 (v0.1.0) ✅

- [x] 基础文本拆分算法
- [x] 段落级别拆分
- [x] 句子级别拆分
- [x] 中文分词支持 (jieba)
- [x] 短片段合并
- [x] CLI 工具

### Phase 2: 增强功能 (v0.2.0)

- [ ] 添加更多拆分策略：
  - [ ] 按字数平均拆分
  - [ ] 按关键词拆分
  - [ ] 保留标题层级
- [ ] 支持 JSON/YAML 格式输入输出
- [ ] 添加进度条显示

### Phase 3: 优化与扩展 (v0.3.0)

- [ ] 性能优化：支持批量处理
- [ ] 添加 Web API 接口
- [ ] 流式处理支持
- [ ] 插件系统

### 未来规划

- 集成向量化功能，直接输出 embeddings
- 支持多种输出格式（JSON、CSV、SQL）
- 可视化拆分预览工具

## 许可证

MIT License