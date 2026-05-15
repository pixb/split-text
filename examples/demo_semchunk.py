"""对比：semchunk vs jieba 词边界保护拆分"""

import re
import jieba
import semchunk


def word_aware_split(text: str, max_length: int) -> list[str]:
    """改进版：优先在子句边界断开，再用 jieba 词边界保护"""
    def find_break(s: str, limit: int) -> int:
        if len(s) <= limit:
            return len(s)
        # 优先级 1：句末
        for m in re.finditer(r'[。！？]', s[:limit]):
            pass
        last = None
        for m in re.finditer(r'[。！？]', s[:limit]):
            last = m.end()
        if last:
            return last
        # 优先级 2：子句边界（，、；：——）
        for m in re.finditer(r'[，、；：,]', s[:limit]):
            last = m.end()
        if last:
            return last
        # 优先级 3：jieba 词边界
        pos = 0
        for w in jieba.cut(s):
            nxt = pos + len(w)
            if nxt > limit:
                return pos
            pos = nxt
        return limit

    chunks = []
    rest = text
    while rest:
        at = find_break(rest, max_length)
        if at == 0:
            at = max_length
        chunks.append(rest[:at])
        rest = rest[at:]
    return chunks


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

chunk_size = 60

# ---- semchunk ----
chunker = semchunk.chunkerify(len, chunk_size=chunk_size)
sem_chunks = chunker(text)

print("=" * 60)
print(f"semchunk（chunk_size={chunk_size}）→ {len(sem_chunks)} chunks")
print("=" * 60)
for i, c in enumerate(sem_chunks, 1):
    disp = c.replace("\n", "").strip()
    cut = " ⚠️ 断在句中" if not disp.endswith(("。","？","！","，","、","；")) else ""
    print(f"  [{i}] ({len(c):2d}字符) {disp}{cut}")

# ---- 改进版 ----
wd_chunks = word_aware_split(text, chunk_size)
print()
print("=" * 60)
print(f"jieba 词边界保护（chunk_size={chunk_size}）→ {len(wd_chunks)} chunks")
print("=" * 60)
for i, c in enumerate(wd_chunks, 1):
    disp = c.replace("\n", "").strip()
    cut = " ⚠️ 断在句中" if not disp.endswith(("。","？","！","，","、","；")) else ""
    print(f"  [{i}] ({len(c):2d}字符) {disp}{cut}")
