"""向量库连接：加载向量化模型 + 连接 Chroma 数据库

被 tools 层引用（import 本模块时会自动完成加载）
注意：所有命令都要在【项目根目录】运行，不要单独运行本文件
"""
from fastembed import TextEmbedding
import chromadb

from config import EMBED_MODEL, CHROMA_DIR, COLLECTION_NAME

print("加载向量化模型...", flush=True)
embed_model = TextEmbedding(model_name=EMBED_MODEL)

client_db = chromadb.PersistentClient(path=CHROMA_DIR)
collection = client_db.get_collection(name=COLLECTION_NAME)
