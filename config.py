"""项目配置中心：所有可调参数集中在这里"""

# ---------- 路径 ----------
CHROMA_DIR = "./chroma_db"           # 向量库目录
COLLECTION_NAME = "traffic_rules"    # 集合名

# ---------- 模型 ----------
EMBED_MODEL = "BAAI/bge-small-zh-v1.5"    # 向量化模型（本地）
LLM_MODEL = "deepseek-chat"               # 对话模型
LLM_BASE_URL = "https://api.deepseek.com"

# ---------- 检索参数 ----------
SEARCH_TOP_K = 3      # 单库检索条数
COMPARE_TOP_K = 2     # 对比时每份规范各检索条数
MAX_STEPS = 6         # Agent 循环步数上限（护栏，防死循环）

# ---------- 数据来源（必须与入库时 metadata 里的 source 完全一致） ----------
SOURCE_A = "GB55011 城市道路交通工程项目规范"
SOURCE_B = "JTG_B01 公路工程技术标准"

# ---------- 系统提示词 ----------
SYSTEM_PROMPT = """你是一个交通规范助手。
回答时必须严格依据检索到的规范条文，不要编造。
如果条文里没有相关答案，就回答"规范里没有找到相关规定"。
需要单位换算时，使用 convert_unit 工具计算，不要心算。
回答末尾请注明来源。"""

# ---------- 测试问题 ----------
TEST_QUESTIONS = [
    "城市道路和公路对“设计速度”的规定有什么不同？",
    "80 km/h 换算成 m/s 是多少？",
    "规范要求高速公路的净高是多少？换算成厘米呢？",
]
