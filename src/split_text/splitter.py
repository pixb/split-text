"""文本拆分核心模块"""

import re
from dataclasses import dataclass
from typing import List
import jieba


@dataclass
class SplitResult:
    """拆分结果"""
    chunks: List[str]
    metadata: dict

    def __str__(self) -> str:
        return f"SplitResult(chunk_count={len(self.chunks)}, metadata={self.metadata})"


class TextSplitter:
    """文本拆分器
    
    将长文本按语义拆分为指定大小的片段，支持中文。
    
    拆分策略：
    1. 首先按段落拆分
    2. 对于超出大小的段落，按句子拆分
    3. 对于仍然超出大小的句子，尝试按子句拆分
    4. 合并过短的片段
    """
    
    def __init__(
        self,
        max_length: int = 200,
        min_chunk_length: int = 50,
        merge_short: bool = True,
    ):
        """
        初始化拆分器
        
        Args:
            max_length: 单个片段的最大字符数
            min_chunk_length: 合并短片段的最小长度阈值
            merge_short: 是否合并过短的片段
        """
        self.max_length = max_length
        self.min_chunk_length = min_chunk_length
        self.merge_short = merge_short
        
        # 句子结束标记
        self.sentence_endings = r'[。！？\.!?；;]'
        # 段落分隔符
        self.paragraph_markers = r'\n\s*\n'
    
    def split(self, text: str) -> SplitResult:
        """
        拆分文本
        
        Args:
            text: 待拆分的文本
            
        Returns:
            SplitResult: 拆分结果
        """
        if not text or not text.strip():
            return SplitResult(chunks=[], metadata={"original_length": 0})
        
        # 清理文本
        text = self._clean_text(text)
        
        # 步骤1: 按段落拆分
        paragraphs = self._split_paragraphs(text)
        
        # 步骤2: 对每个段落进行拆分和合并
        chunks = []
        for para in paragraphs:
            para_chunks = self._split_paragraph(para)
            chunks.extend(para_chunks)
        
        # 步骤3: 合并过短的片段
        if self.merge_short:
            chunks = self._merge_short_chunks(chunks)
        
        metadata = {
            "original_length": len(text),
            "chunk_count": len(chunks),
            "max_length": self.max_length,
        }
        
        return SplitResult(chunks=chunks, metadata=metadata)
    
    def _clean_text(self, text: str) -> str:
        """清理文本"""
        # 移除多余的空白字符，但保留换行
        text = re.sub(r'[ \t]+', ' ', text)
        text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)
        return text.strip()
    
    def _split_paragraphs(self, text: str) -> List[str]:
        """按段落拆分"""
        # 使用正则拆分段落
        paragraphs = re.split(self.paragraph_markers, text)
        # 过滤空段落
        return [p.strip() for p in paragraphs if p.strip()]
    
    def _split_paragraph(self, paragraph: str) -> List[str]:
        """拆分单个段落"""
        # 如果段落已经小于最大长度，直接返回
        if len(paragraph) <= self.max_length:
            return [paragraph]
        
        # 尝试按句子拆分
        sentences = self._split_sentences(paragraph)
        
        # 合并句子成片段
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            # 如果单个句子就超过最大长度，需要进一步拆分
            if len(sentence) > self.max_length:
                # 先保存当前累积的片段
                if current_chunk:
                    chunks.append(current_chunk)
                    current_chunk = ""
                
                # 递归拆分超长句子
                sub_chunks = self._split_long_sentence(sentence)
                chunks.extend(sub_chunks)
                continue
            
            # 尝试将句子加入当前片段
            if len(current_chunk) + len(sentence) + 1 <= self.max_length:
                if current_chunk:
                    current_chunk += " " + sentence
                else:
                    current_chunk = sentence
            else:
                # 当前片段已满，保存并开始新片段
                if current_chunk:
                    chunks.append(current_chunk)
                current_chunk = sentence
        
        # 保存最后一个片段
        if current_chunk:
            chunks.append(current_chunk)
        
        return chunks
    
    def _split_sentences(self, text: str) -> List[str]:
        """按句子拆分"""
        # 使用正则按句子结束标记拆分，保留结束标记
        pattern = f'({self.sentence_endings})'
        parts = re.split(pattern, text)
        
        sentences = []
        for i in range(0, len(parts) - 1, 2):
            sentence = parts[i]
            if i + 1 < len(parts):
                sentence += parts[i + 1]
            if sentence.strip():
                sentences.append(sentence)
        
        # 处理最后一个没有结束标记的部分
        if parts[-1].strip():
            if sentences:
                sentences[-1] += parts[-1]
            else:
                sentences.append(parts[-1])
        
        return sentences
    
    def _split_long_sentence(self, sentence: str) -> List[str]:
        """拆分超长句子
        
        使用jieba进行中文分词，尝试在合适的位置拆分
        """
        # 如果是纯英文，使用空格拆分
        if self._is_english(sentence):
            words = sentence.split()
            return self._merge_by_words(words)
        
        # 中文句子使用jieba分词
        words = list(jieba.cut(sentence))
        return self._merge_by_words(words, use_chinese=True)
    
    def _is_english(self, text: str) -> bool:
        """判断是否为纯英文文本"""
        # 统计中文字符比例
        chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
        return chinese_chars == 0 and len(text) > 0
    
    def _merge_by_words(self, words: List[str], use_chinese: bool = False) -> List[str]:
        """将词列表合并为片段"""
        chunks = []
        current_chunk = ""
        
        for word in words:
            word = word.strip()
            if not word:
                continue
            
            # 计算考虑标点的长度
            test_chunk = current_chunk + (" " if current_chunk else "") + word
            
            if len(test_chunk) <= self.max_length:
                current_chunk = test_chunk
            else:
                if current_chunk:
                    chunks.append(current_chunk)
                
                # 如果单个词就超过最大长度，强制截断
                if len(word) > self.max_length:
                    # 递归截断
                    word_chunks = self._force_split(word)
                    chunks.extend(word_chunks[:-1])
                    current_chunk = word_chunks[-1] if word_chunks else ""
                else:
                    current_chunk = word
        
        if current_chunk:
            chunks.append(current_chunk)
        
        return chunks
    
    def _force_split(self, text: str) -> List[str]:
        """强制拆分超长文本"""
        chunks = []
        for i in range(0, len(text), self.max_length):
            chunk = text[i:i + self.max_length]
            if chunk:
                chunks.append(chunk)
        return chunks
    
    def _merge_short_chunks(self, chunks: List[str]) -> List[str]:
        """合并过短的片段"""
        if not chunks:
            return chunks
        
        merged = [chunks[0]]
        
        for chunk in chunks[1:]:
            # 如果最后一个片段加上当前片段小于最大长度，则合并
            if len(merged[-1]) + len(chunk) + 1 <= self.max_length:
                merged[-1] = merged[-1] + " " + chunk
            # 如果当前片段小于最小长度阈值，也尝试合并
            elif len(chunk) < self.min_chunk_length and len(merged[-1]) + len(chunk) + 1 <= self.max_length:
                merged[-1] = merged[-1] + " " + chunk
            else:
                merged.append(chunk)
        
        return merged


# 便捷函数
def split_text(text: str, max_length: int = 200, **kwargs) -> SplitResult:
    """
    拆分文本的便捷函数
    
    Args:
        text: 待拆分的文本
        max_length: 单个片段的最大字符数
        **kwargs: 其他参数传递给TextSplitter
        
    Returns:
        SplitResult: 拆分结果
    """
    splitter = TextSplitter(max_length=max_length, **kwargs)
    return splitter.split(text)


if __name__ == "__main__":
    # 测试代码
    test_text = """这是一个测试文本。我们希望将它拆分成小于200个字符的片段。
    
这段是另一个段落。它包含更多的内容，用于测试拆分功能。
    
这里是第三段。我们继续添加更多的内容，以确保测试的准确性。这是一段很长的文字，用于测试当段落超过最大长度时的处理情况。"""
    
    result = split_text(test_text, max_length=50)
    print(f"原始长度: {result.metadata['original_length']}")
    print(f"片段数量: {result.metadata['chunk_count']}")
    print("\n拆分结果:")
    for i, chunk in enumerate(result.chunks, 1):
        print(f"[{i}] ({len(chunk)}字符): {chunk}")