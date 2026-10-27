"""评测脚本：跑 20 组评测题，输出检索命中率

用法（在项目根目录）：
    python eval.py
"""
import json

from tools.search_tools import search_rules


# ==================== 下面两个函数留给你写 ====================

def normalize(text):
    """文本标准化：去掉换行和空格（对付 OCR 换行把词切断）

    提示：用 replace() 把 "\n"（换行）和 " "（空格）替换成空字符串 ""
    例如："a\nb c" → "abc"
    """
    # TODO: 在这里写你的代码（最后要 return 处理后的文本）
    text = text.replace("\n", "")
    text = text.replace(" ", "")
    return text


def is_hit(text, keywords):
    """判断 text 里是否包含任一关键词（标准化后比较）

    提示：
    1. 先把 text 标准化（调用上面的 normalize）
    2. 遍历 keywords，只要有一个"在"标准化后的 text 里，就 return True
    3. 全都没找到，就 return False
    """
    # TODO: 在这里写你的代码
    text = normalize(text)
    for keyword in keywords:
        if normalize(keyword) in text:      # ← 每轮只洗"当前这个词"
            return True
            
    return False


# ==================== 下面是现成的流程代码（不用改） ====================

def eval_retrieval(eval_set):
    """检索层评测：每题检索 top-3，检查命中的内容里有没有关键词"""
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
