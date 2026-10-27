"""全局配置：模型、检索参数、系统提示词"""

# 向量库
CHROMA_DIR = "./chroma_db"
COLLECTION_NAME = "traffic_rules"

# 模型
EMBED_MODEL = "BAAI/bge-small-zh-v1.5"    # 本地跑的向量模型
LLM_MODEL = "deepseek-chat"
LLM_BASE_URL = "https://api.deepseek.com"

# 检索
SEARCH_TOP_K = 3
COMPARE_TOP_K = 2
MAX_STEPS = 6        # 循环步数上限，防止工具调用打转

# 数据来源：必须与入库时写进 metadata 的 source 完全一致，否则 where 过滤一条都查不到
SOURCE_A = "GB55011 城市道路交通工程项目规范"
SOURCE_B = "JTG_B01 公路工程技术标准"

# 系统提示词
SYSTEM_PROMPT = """你是一个交通规范助手。
始终使用中文回答。
回答时必须严格依据检索到的规范条文，不要编造。
如果条文里没有相关答案，就回答"规范里没有找到相关规定"。
需要单位换算时，使用 convert_unit 工具计算，不要心算。
回答末尾请注明来源。"""

# 测试问题
TEST_QUESTIONS = [
    "城市道路和公路对“设计速度”的规定有什么不同？",
    "80 km/h 换算成 m/s 是多少？",
    "规范要求高速公路的净高是多少？换算成厘米呢？",
]
