"""检索类工具：查条文 / 规范对比"""
from rag.store import embed_model, collection
from config import SOURCE_A, SOURCE_B, SEARCH_TOP_K, COMPARE_TOP_K


def search_rules(query, top_k=SEARCH_TOP_K):
    """检索规范条文，返回拼好的 top_k 段文本（带来源标记）"""
    q_vec = list(embed_model.embed([query]))[0].tolist()
    result = collection.query(query_embeddings=[q_vec], n_results=top_k)

    hits = []
    for i in range(len(result["documents"][0])):
        doc = result["documents"][0][i]
        source = result["metadatas"][0][i]["source"]
        hits.append(f"【来源：{source}】\n{doc}")

    return "\n\n---\n\n".join(hits)


def compare_rules(topic, top_k=COMPARE_TOP_K):
    """两份规范分别检索同一主题，拼成对照文本"""
    q_vec = list(embed_model.embed([topic]))[0].tolist()

    parts = []
    for src in (SOURCE_A, SOURCE_B):
        result = collection.query(
            query_embeddings=[q_vec],
            n_results=top_k,
            where={"source": src},          # 只在单份规范内检索
        )
        lines = [f"===== {src} 的相关条文 ====="]
        for d in result["documents"][0]:
            lines.append(d)
        parts.append("\n".join(lines))

    return "\n\n".join(parts)
