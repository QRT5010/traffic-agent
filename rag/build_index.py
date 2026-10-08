"""把切好的 chunks 向量化，存进 Chroma 向量库"""
import json
import chromadb
from fastembed import TextEmbedding

# 1. 读入切好的块
with open("docs/chunks.json", "r", encoding="utf-8") as f:
    chunks = json.load(f)
print(f"读取到 {len(chunks)} 块文本")

# 2. 加载向量化模型（和昨天同一个中文模型）
print("正在加载向量化模型...")
embed_model = TextEmbedding(model_name="BAAI/bge-small-zh-v1.5")

# 3. 连接向量库
client = chromadb.PersistentClient(path="./chroma_db")

# 4. 全量重建：先删旧集合，再建新的（保证每次跑都干净，不重复堆积）
try:
    client.delete_collection("traffic_rules")
    print("已删除旧集合")
except Exception:
    pass
collection = client.create_collection(name="traffic_rules")

# 5. 向量化（246 块一起算）
texts = [c["text"] for c in chunks]
print(f"正在向量化 {len(texts)} 块（约 30-60 秒）...")
vectors = list(embed_model.embed(texts))

# 6. 入库：每块存【原文 + 向量 + 来源标记】
collection.add(
    ids=[f"chunk_{i}" for i in range(len(chunks))],
    documents=texts,
    embeddings=[v.tolist() for v in vectors],
    metadatas=[{"source": c["source"]} for c in chunks],
)

print(f"入库完成！库里现有 {collection.count()} 条")
