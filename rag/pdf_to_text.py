"""扫描版 PDF 转文字：逐页渲染成图（150 dpi）→ OCR → 拼接输出 txt

用法（页码从 1 开始数）：
    python rag/pdf_to_text.py <PDF路径> <起始页> <结束页> <输出txt路径>

示例：
    python rag/pdf_to_text.py "docs/xx规范.pdf" 1 34 "docs/xx规范.txt"
"""
import sys
import time
import pymupdf
from rapidocr_onnxruntime import RapidOCR


def pdf_to_text(pdf_path, start_page, end_page, out_path):
    doc = pymupdf.open(pdf_path)
    total = len(doc)
    if end_page > total:
        end_page = total

    print(f"文件：{pdf_path}")
    print(f"共 {total} 页，本次处理第 {start_page}-{end_page} 页（{end_page - start_page + 1} 页）")
    print("-" * 50)

    ocr = RapidOCR()
    all_pages = []
    t0 = time.time()
    count = end_page - start_page + 1

    for i in range(start_page - 1, end_page):
        pix = doc[i].get_pixmap(dpi=150)
        result, _ = ocr(pix.tobytes("png"))
        page_text = "\n".join([line[1] for line in result]) if result else ""
        all_pages.append(page_text)

        done = i - start_page + 2
        if done % 5 == 0 or done == count:
            elapsed = time.time() - t0
            speed = elapsed / done
            remain = (count - done) * speed
            print(f"  进度 {done}/{count} 页 | 已用 {elapsed:.0f}s | 预计剩余 {remain:.0f}s")

    text = "\n\n".join(all_pages)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(text)
    print("-" * 50)
    print(f"完成！输出到 {out_path}")
    print(f"共提取 {len(text)} 个字符，总耗时 {time.time() - t0:.0f}s")


if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("用法：python pdf_to_text.py <PDF路径> <起始页> <结束页> <输出txt路径>")
        sys.exit(1)
    pdf_to_text(sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), sys.argv[4])
