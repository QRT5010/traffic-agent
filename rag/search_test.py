"""检索冒烟测试：问 5 个问题，打印 top-3 命中内容"""
import chromadb
from fastembed import TextEmbedding

embed_model = TextEmbedding(model_name="BAAI/bge-small-zh-v1.5")
client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_collection(name="traffic_rules")

QUESTIONS = [
    "城市道路分为哪几个等级？",
    "公路分为哪几个技术等级？",
    "公路用地范围是怎么规定的？",
    "城市道路的设计速度是怎么规定的？",
    "爬坡车道应该设置在什么位置？",
]

for q in QUESTIONS:
    print("=" * 60)
    print(f"问题：{q}")

    q_vec = list(embed_model.embed([q]))[0].tolist()

    result = collection.query(query_embeddings=[q_vec], n_results=3)

    for i in range(len(result["documents"][0])):
        doc = result["documents"][0][i]
        source = result["metadatas"][0][i]["source"]
        dist = result["distances"][0][i]
        print(f"\n  [命中 {i+1}] 距离 {dist:.4f} | 来源：{source}")
        print(f"  {doc[:150]}...")
    print()
