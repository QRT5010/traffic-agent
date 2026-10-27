"""把 OCR 出来的规范文本切分成小块（chunk），为入库做准备

v3 · 结构感知切分（D6 评测实验后定稿，命中率 19/20 → 20/20）：
1. 清噪声：去掉 OCR 水印碎片（"浏览专用"等）和页码行
2. 结构边界切分：遇到"条文行"（如 3.1.1）或"子项行"（如 1高速公路为…）
   → 从这里开新块；且结构边界【不带走上一块的尾巴】——保证每块干净地从条文/子项开始
3. 只有被"长度强制切开"的位置（攒够 300 字），才保留 60 字重叠

为什么这样改：v1 里"公路分为…五个技术等级"所在的块，
前面混着上一节 100 多字 + 水印碎片，语义被稀释，检索排到 184/246 名。
改完后同一条文排第 1 名。
"""
import json
import re

# ---------- 噪声识别 ----------
# 三个水印的文字：浏览专用 / 住房城乡建设部信息公开 / 交通运输部信息公开
# OCR 会把斜着的水印切成各种碎片，但碎片只可能由这些字组成：
_WM_CHARS = set("浏览专用住房城乡建设部信息公交通运输开Xx×么")
# 碎片必须含"高信号字"，否则可能误伤正文（比如单独的"城市""建设"不该删）：
_WM_MARKERS = set("浏览Xx×住房交通运输")
# 页码行：形如 "-72—" "一58一" "-51"（至少含一个杠/横）
_PAGE_RE = re.compile(r"^[-—一]?\s*\d{1,3}\s*[-—一]?$")

# ---------- 结构边界 ----------
_CLAUSE_RE = re.compile(r"^\d+\.\d+\.\d+")             # 条文行：3.1.1…
_SUBITEM_RE = re.compile(r"^\d{1,2}[\u4e00-\u9fff]")    # 子项行：1高速公路为…（数字+中文，防误伤 2016年/15000辆 这类）


def is_noise(s):
    """判断一行（已 strip）是不是 OCR 噪声"""
    if not s:
        return True
    # 页码
    if any(c in "-—一" for c in s) and _PAGE_RE.match(s):
        return True
    # 水印碎片：整行只由水印字组成、含高信号字、且很短
    if len(s) <= 14 and any(c in _WM_MARKERS for c in s) \
            and all(c in _WM_CHARS or c in " \u3000" for c in s):
        return True
    return False


def clean_lines(text):
    """把 OCR 文本按行清洗：去掉空行 + 噪声行，返回干净的行列表"""
    result = []
    for line in text.split("\n"):
        s = line.strip()
        if s and not is_noise(s):
            result.append(s)
    return result


def chunk_text(lines, chunk_size=300, overlap=60):
    """把行列表切成小块

    chunk_size: 每块到达多少字就强制切（强制切处保留 overlap 字重叠）
    overlap:    强制切割处的重叠字数
    """
    chunks = []
    current = ""

    for line in lines:
        # 结构边界：条文行 / 子项行 → 干净地开新块（不带走尾巴）
        if _CLAUSE_RE.match(line) or _SUBITEM_RE.match(line):
            if current.strip():
                chunks.append(current.strip())
            current = ""

        current += line + "\n"

        # 长度强制切：攒够字数，切一刀并保留重叠
        if len(current) >= chunk_size:
            chunks.append(current.strip())
            current = current[-overlap:]

    # 最后剩的部分别漏掉
    if current.strip():
        chunks.append(current.strip())

    return chunks


# ==================== 主流程 ====================
if __name__ == "__main__":
    files = [
        ("GB55011 城市道路交通工程项目规范", "docs/GB55011.txt"),
        ("JTG_B01 公路工程技术标准", "docs/JTG_B01.txt"),
    ]

    all_chunks = []
    for source, path in files:
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()

        raw_lines = [l.strip() for l in text.split("\n") if l.strip()]
        lines = clean_lines(text)
        pieces = chunk_text(lines)

        print(f"{source}")
        print(f"  清洗：{len(raw_lines)} 行 → {len(lines)} 行（删噪声 {len(raw_lines) - len(lines)} 行）")
        print(f"  切分：切成 {len(pieces)} 块")
        for p in pieces:
            all_chunks.append({"source": source, "text": p})

    with open("docs/chunks.json", "w", encoding="utf-8") as f:
        json.dump(all_chunks, f, ensure_ascii=False, indent=2)

    lengths = [len(c["text"]) for c in all_chunks]
    print("-" * 50)
    print("切分策略：结构边界切分（条文行 / 子项行 处干净切）")
    print(f"总块数：{len(all_chunks)}（v1 为 246）")
    print(f"平均每块：{sum(lengths) // len(lengths)} 字")
    print(f"最长：{max(lengths)} 字 | 最短：{min(lengths)} 字")
