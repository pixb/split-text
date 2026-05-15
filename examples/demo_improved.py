"""对比：原始拆分 vs 按子句优先拆分"""

import re
import jieba
from split_text.splitter import split_text


def improved_split(text, max_length=200):
    """改进版：长句优先按子句拆分，再按词边界"""
    chunks = []
    paragraphs = re.split(r'\n\s*\n', text.strip())

    for para in paragraphs:
        para = re.sub(r'[ \t]+', ' ', para).strip()
        if not para:
            continue

        if len(para) <= max_length:
            chunks.append(para)
            continue

        # 按句子拆分
        sentences = re.split(r'(?<=[。！？\.!?；;])', para)
        sentences = [s.strip() for s in sentences if s.strip()]

        buf = ""
        for sent in sentences:
            if len(sent) > max_length:
                if buf:
                    chunks.append(buf)
                # 长句子：先按子句拆分
                subs = _split_by_clause(sent, max_length)
                chunks.extend(subs)
                buf = ""
            elif len(buf) + len(sent) + 1 <= max_length:
                buf = (buf + " " + sent) if buf else sent
            else:
                chunks.append(buf)
                buf = sent

        if buf:
            chunks.append(buf)

    return chunks


_CLAUSE_BOUNDARY = re.compile(r'([，、；：,;:])')


def _split_by_clause(text, max_length):
    """将超长句子先按子句（逗号、分号等）拆分，再按词拆分"""
    parts = re.split(_CLAUSE_BOUNDARY, text)
    clauses = []
    for i in range(0, len(parts) - 1, 2):
        clause = parts[i]
        if i + 1 < len(parts):
            clause += parts[i + 1]
        if clause.strip():
            clauses.append(clause)
    if parts[-1].strip():
        clauses.append(parts[-1])
    if not clauses:
        clauses = [text]

    result = []
    buf = ""
    for clause in clauses:
        if len(buf) + len(clause) + 1 <= max_length:
            buf = (buf + " " + clause) if buf else clause
        elif len(clause) <= max_length:
            if buf:
                result.append(buf)
            buf = clause
        else:
            if buf:
                result.append(buf)
            result.extend(_split_by_word(clause, max_length))
            buf = ""
    if buf:
        result.append(buf)
    return result


def _split_by_word(text, max_length):
    """最终按词拆分"""
    words = list(jieba.cut(text))
    chunks = []
    buf = ""
    for word in words:
        word = word.strip()
        if not word:
            continue
        candidate = (buf + " " + word) if buf else word
        if len(candidate) <= max_length:
            buf = candidate
        else:
            if buf:
                chunks.append(buf)
            if len(word) > max_length:
                for i in range(0, len(word), max_length):
                    chunks.append(word[i:i + max_length])
                buf = ""
            else:
                buf = word
    if buf:
        chunks.append(buf)
    return chunks


text = """各位朋友：
回到台北来已经二十多天，在这短短的时间里，我收到无数过去与我通信的读者、我教过的学生、以及许许多多新朋友的来信与电话。我也在台北街头看见自己的新书，挤在一大堆花花绿绿的书刊里，向我扮着顽皮的鬼脸。

我多么希望每一封信都细细地回答你们。因为我知道，每一个写信给我的人，在提笔时，也费了番心思和时间来表示对我的关怀。

离开家国那么久了，台北的亲情友情，整整地占据了我。我尽力愿意把我自己的时间，分给每一个关怀我的朋友。可惜的是，我一天也只能捉住二十四小时。"""

print("=" * 60)
print("max_length = 60")
print("=" * 60)

orig = split_text(text, max_length=60)
improved = improved_split(text, max_length=60)

print(f"\n原版 split_text:  {orig.metadata['chunk_count']} 个片段")
for i, c in enumerate(orig.chunks, 1):
    trunc = " ❌ 句子被截断" if not c.rstrip().endswith(("。", "？", "！", "》", "」")) and c.strip() else ""
    print(f"  [{i}] ({len(c):2d}字符) {c}{trunc}")

print(f"\n改进版(子句优先): {len(improved)} 个片段")
for i, c in enumerate(improved, 1):
    trunc = " ❌ 句子被截断" if not c.rstrip().endswith(("。", "？", "！", "》", "」")) and c.strip() else ""
    print(f"  [{i}] ({len(c):2d}字符) {c}{trunc}")
