"""检索层评测：20 道题，统计 top-3 结果里出现答案关键词的比例

用法（在项目根目录，纯本地运行，不消耗 API）：
    python eval.py
"""
import json

from tools.search_tools import search_rules


def normalize(text):
    """去掉换行和空格：OCR 会在行尾断词，不洗掉就匹配不上关键词"""
    text = text.replace("\n", "")
    text = text.replace(" ", "")
    return text


def is_hit(text, keywords):
    """text 里是否出现任一关键词（两边都先标准化）"""
    text = normalize(text)
    for keyword in keywords:
        if normalize(keyword) in text:      # 关键词自身也可能带空格
            return True
    return False


def eval_retrieval(eval_set):
    """逐题检索 top-3 并判定命中，打印每题结果，返回总命中率"""
    hit_count = 0
    for item in eval_set:
        retrieved = search_rules(item["question"])
        hit = is_hit(retrieved, item["keywords"])
        hit_count += int(hit)
        mark = "✅" if hit else "❌"
        print(f"{mark} [{item['id']:2d}] {item['question']}")
    rate = hit_count / len(eval_set) * 100
    print("-" * 50)
    print(f"检索命中率：{hit_count}/{len(eval_set)} = {rate:.1f}%")
    return rate


if __name__ == "__main__":
    with open("docs/eval_set.json", encoding="utf-8") as f:
        eval_set = json.load(f)
    print("=" * 50)
    print("检索层评测（20 题）")
    print("=" * 50)
    eval_retrieval(eval_set)
