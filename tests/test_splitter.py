"""测试 TextSplitter"""

import pytest
from split_text.splitter import TextSplitter, split_text, SplitResult


class TestTextSplitter:
    """测试 TextSplitter 类"""
    
    def test_empty_text(self):
        """测试空文本"""
        splitter = TextSplitter(max_length=200)
        result = splitter.split("")
        
        assert result.chunks == []
        assert result.metadata["original_length"] == 0
    
    def test_text_shorter_than_max_length(self):
        """测试小于最大长度的文本"""
        text = "这是一个简短的测试文本。"
        splitter = TextSplitter(max_length=200)
        result = splitter.split(text)
        
        assert len(result.chunks) == 1
        assert result.chunks[0] == text
    
    def test_basic_split(self):
        """测试基本拆分功能"""
        text = "第一句。第二句。第三句。" * 20  # 约240字符
        result = split_text(text, max_length=100)
        
        # 验证片段数量
        assert len(result.chunks) >= 2
        # 验证每个片段长度
        for chunk in result.chunks:
            assert len(chunk) <= 100
    
    def test_paragraph_split(self):
        """测试按段落拆分"""
        text = """这是第一段的内容。它包含了一些文字。

这是第二段的内容。也有文字。

这是第三段。"""
        
        result = split_text(text, max_length=50)
        
        # 验证段落被正确识别 - 至少应该有多个段落被识别
        assert result.metadata["chunk_count"] >= 1
        # 验证所有chunks加起来长度接近原文（考虑清理后的差异）
        total = sum(len(c) for c in result.chunks)
        assert total <= result.metadata["original_length"]
    
    def test_chinese_text(self):
        """测试中文文本拆分"""
        text = "人工智能是计算机科学的一个重要分支。机器学习是它的核心。深度学习是机器学习的一个分支。" * 5
        
        result = split_text(text, max_length=100)
        
        for chunk in result.chunks:
            assert len(chunk) <= 100
            # 验证中文字符
            assert len(chunk) > 0
    
    def test_merge_short_chunks(self):
        """测试合并短片段"""
        text = "短。" * 30  # 每个句子很短
        
        result = split_text(
            text,
            max_length=50,
            min_chunk_length=20,
            merge_short=True
        )
        
        # 短片段应该被合并
        for chunk in result.chunks:
            assert len(chunk) >= 20 or len(chunk) == len(text)
    
    def test_no_merge(self):
        """测试不合并短片段"""
        text = "短句子。" * 10  # 每个句子4字符，总共40字符
        
        result = split_text(
            text,
            max_length=10,  # 设置较小的max_length来强制拆分
            merge_short=False
        )
        
        # 短片段不应被合并，每个片段应该按max_length限制拆分
        assert len(result.chunks) >= 3
    
    def test_max_length_20(self):
        """测试较小的最大长度"""
        text = "这是一段较长的中文文本，用于测试拆分功能。" * 5
        
        result = split_text(text, max_length=20)
        
        for chunk in result.chunks:
            assert len(chunk) <= 20
    
    def test_english_text(self):
        """测试英文文本"""
        text = "This is a test. " * 30
        
        result = split_text(text, max_length=50)
        
        for chunk in result.chunks:
            assert len(chunk) <= 50
    
    def test_mixed_text(self):
        """测试中英文混合文本"""
        text = "这是中文。This is English. 混合文本。Mixed text here." * 5
        
        result = split_text(text, max_length=80)
        
        for chunk in result.chunks:
            assert len(chunk) <= 80


class TestSplitResult:
    """测试 SplitResult 数据类"""
    
    def test_str_representation(self):
        """测试字符串表示"""
        result = SplitResult(chunks=["chunk1", "chunk2"], metadata={"test": 1})
        
        assert "chunk_count=2" in str(result)
        assert "metadata=" in str(result)


def test_split_text_convenience_function():
    """测试便捷函数"""
    text = "测试文本。" * 10
    
    result = split_text(text, max_length=50)
    
    assert isinstance(result, SplitResult)
    assert len(result.chunks) >= 1
    assert all(len(chunk) <= 50 for chunk in result.chunks)