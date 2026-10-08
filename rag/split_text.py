"""把 OCR 出来的规范文本切分成小块（chunk），为入库做准备"""
import json


def chunk_text(text, chunk_size=300, overlap=60):
    """把长文本切成小块

    chunk_size: 每块大约多少字（累积到这个长度就切一刀）
    overlap:    相邻两块重叠多少字（防止关键信息正好落在切口上）
    """
    # 1. 按行拆开，去掉空行（OCR 文本是一行一行的）
    lines = [line.strip() for line in text.split("\n") if line.strip()]

    chunks = []          # 存放切好的块
    current = ""         # 当前正在累积的块

    for line in lines:
        current += line + "\n"

        # 2. 累积够长了，就切一刀
        if len(current) >= chunk_size:
            chunks.append(current.strip())
            # 3. 保留末尾 overlap 个字，作为下一块的开头（重叠区）
            current = current[-overlap:]

    # 4. 最后剩的部分别漏掉
    if current.strip():
        chunks.append(current.strip())

    return chunks


# ==================== 主流程 ====================
if __name__ == "__main__":
    # 两份规范文本
    files = [
        ("GB55011 城市道路交通工程项目规范", "docs/GB55011.txt"),
        ("JTG_B01 公路工程技术标准", "docs/JTG_B01.txt"),
    ]

    all_chunks = []
    for source, path in files:
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()
        pieces = chunk_text(text)
        print(f"{source}")
        print(f"  原文 {len(text)} 字  →  切成 {len(pieces)} 块")
        for p in pieces:
            # 每块都带上"来源"，以后回答时可以注明"出自哪份规范"
            all_chunks.append({"source": source, "text": p})

    # 存成 json 文件，下一步入库直接用
    with open("docs/chunks.json", "w", encoding="utf-8") as f:
        json.dump(all_chunks, f, ensure_ascii=False, indent=2)

    # 打印统计信息，检查切分质量
    lengths = [len(c["text"]) for c in all_chunks]
    print("-" * 50)
    print(f"总块数：{len(all_chunks)}")
    print(f"平均每块：{sum(lengths) // len(lengths)} 字")
    print(f"最长：{max(lengths)} 字 | 最短：{min(lengths)} 字")
    print("-" * 50)
    print("【前 3 块示例（看看长什么样）】")
    for c in all_chunks[:3]:
        print(f"--- 来源：{c['source']} ---")
        print(c["text"][:150])
        print()
