"""split-text: 将长文本按语义拆分为较小片段的工具"""

__version__ = "0.1.0"

from .splitter import TextSplitter, SplitResult

__all__ = ["TextSplitter", "SplitResult", "__version__"]