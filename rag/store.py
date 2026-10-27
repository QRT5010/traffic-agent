"""向量库连接：加载向量化模型 + 打开 Chroma 集合

import 本模块就等于完成加载，所以所有命令必须在项目根目录执行（路径是相对的）。
"""
from fastembed import TextEmbedding
import chromadb

from config import EMBED_MODEL, CHROMA_DIR, COLLECTION_NAME

print("加载向量化模型...", flush=True)
embed_model = TextEmbedding(model_name=EMBED_MODEL)

client_db = chromadb.PersistentClient(path=CHROMA_DIR)
collection = client_db.get_collection(name=COLLECTION_NAME)
