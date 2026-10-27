"""把 docs/chunks.json 向量化后写入 Chroma（每次全量重建）"""
import json
import chromadb
from fastembed import TextEmbedding

with open("docs/chunks.json", "r", encoding="utf-8") as f:
    chunks = json.load(f)
print(f"读取到 {len(chunks)} 块文本")

print("正在加载向量化模型...")
embed_model = TextEmbedding(model_name="BAAI/bge-small-zh-v1.5")

client = chromadb.PersistentClient(path="./chroma_db")

# 先删旧集合再新建，保证每次跑都是一份干净的数据，不重复堆积
try:
    client.delete_collection("traffic_rules")
    print("已删除旧集合")
except Exception:
    pass
collection = client.create_collection(name="traffic_rules")

texts = [c["text"] for c in chunks]
print(f"正在向量化 {len(texts)} 块（约 30-60 秒）...")
vectors = list(embed_model.embed(texts))

# 每块存原文 + 向量 + 来源标记（来源用于 compare_rules 的 where 过滤）
collection.add(
    ids=[f"chunk_{i}" for i in range(len(chunks))],
    documents=texts,
    embeddings=[v.tolist() for v in vectors],
    metadatas=[{"source": c["source"]} for c in chunks],
)

print(f"入库完成！库里现有 {collection.count()} 条")
