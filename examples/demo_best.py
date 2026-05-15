"""最佳实践：分层回退拆分方案"""

import re
import jieba


def smart_split(text: str, max_length: int = 60):
    """分层回退拆分：段落 → 句子 → 子句 → 词边界

    核心思想：贪心累积完整单位，超过上限时回退到上一个安全断点。
    """

    def _split_para(para: str) -> list[str]:
        """拆分单个段落"""
        if len(para) <= max_length:
            return [para]

        sentences = _split_sentences(para)
        return _merge_units(sentences, _split_sentence)

    def _split_sentences(text: str) -> list[str]:
        pattern = r'(?<=[。！？\.!?；;])'
        parts = re.split(pattern, text)
        return [s.strip() for s in parts if s.strip()]

    def _split_sentence(sent: str) -> list[str]:
        """拆分超长句子 → 子句"""
        if len(sent) <= max_length:
            return [sent]
        clauses = re.split(r'(?<=[，、；：,;:])', sent)
        clauses = [c.strip() for c in clauses if c.strip()]
        if not clauses:
            clauses = [sent]

        result = []
        buf = ""
        for clause in clauses:
            if len(clause) > max_length:
                if buf:
                    result.append(buf)
                    buf = ""
                result.extend(_split_clause_by_word(clause))
            elif len(buf) + len(clause) + 1 <= max_length:
                buf = (buf + clause) if buf else clause
            else:
                if buf:
                    result.append(buf)
                buf = clause
        if buf:
            result.append(buf)
        return result

    def _split_clause_by_word(text: str) -> list[str]:
        """超长子句 → 词边界（jieba）"""
        words = list(jieba.cut(text))
        chunks = []
        buf = ""
        for word in words:
            if not word.strip():
                continue
            candidate = buf + word
            if len(candidate) <= max_length:
                buf = candidate
            else:
                if buf:
                    chunks.append(buf)
                buf = word
        if buf:
            chunks.append(buf)
        return chunks

    def _merge_units(units: list[str], split_fn) -> list[str]:
        """贪心累积完整单位，超限回退"""
        chunks = []
        buf = ""
        for unit in units:
            if len(unit) > max_length:
                if buf:
                    chunks.append(buf)
                    buf = ""
                sub = split_fn(unit)
                chunks.extend(sub)
            elif len(buf) + len(unit) + 1 <= max_length:
                buf = (buf + unit) if buf else unit
            else:
                chunks.append(buf)
                buf = unit
        if buf:
            chunks.append(buf)
        return chunks

    # 主流程
    paragraphs = re.split(r'\n\s*\n', text.strip())
    paragraphs = [re.sub(r'[ \t]+', ' ', p).strip() for p in paragraphs if p.strip()]

    if not paragraphs:
        return []

    result = []
    for para in paragraphs:
        result.extend(_split_para(para))

    return result


text = """各位朋友：
回到台北来已经二十多天，在这短短的时间里，我收到无数过去与我通信的读者、我教过的学生、以及许许多多新朋友的来信与电话。

我也在台北街头看见自己的新书，挤在一大堆花花绿绿的书刊里，向我扮着顽皮的鬼脸。

每当我收到由各方面转来的你们的来信时，我在这一封封诚意的信里，才看出了我自己的形象。

我多么希望每一封信都细细地回答你们。

因为我知道，每一个写信给我的人，在提笔时，也费了番心思和时间来表示对我的关怀。

我怎么能够看见你们诚意的来信，知道你们一定在等着我的回音，而那一封封的信都如石沉大海，没有回声。

请无数写信给我的朋友了解我，三毛不是一个没有感情也没有礼貌的人。

离开家国那么久了，台北的亲情友情，整整地占据了我。

我尽力愿意把我自己的时间，分给每一个关怀我的朋友。

可惜的是，我一天也只能捉住二十四小时。

生活突然的忙碌热闹，使我精神上兴奋而紧张，体力上透支再透支。

而内心的宁静，却已因为这些感人的真情流露起了很大的波澜。

虽然我努力在告诉自己，我要完完全全享受我在祖国的假期，游山玩水，与父母亲闲话家常。

事实上，我每日的生活，已成了时间的奴隶，我日日夜夜地追赶着它，而仿佛永远不能在这件事上得到释放。"""

for size in (40, 60, 100):
    chunks = smart_split(text, max_length=size)
    print("=" * 60)
    print(f"smart_split(max_length={size}) → {len(chunks)} chunks")
    print("=" * 60)
    bad = 0
    for i, c in enumerate(chunks, 1):
        ok = c.rstrip().endswith(("。", "？", "！", "》", "」", "：", "\n"))
        if not ok:
            bad += 1
        flag = "" if ok else " ⚠️"
        print(f"  [{i}] ({len(c):2d}字符) {c[:size + 20]}{flag}")
    print(f"  --- 断在句中: {bad}/{len(chunks)}")
    print()
