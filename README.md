# traffic-agent

> 交通规范智能问答 Agent —— 一个会"自己查规范"的 RAG Agent

基于向量检索（ChromaDB）+ 大模型（DeepSeek）的交通规范问答系统。
给它一个规范问题，它会**自主检索相关条文**，并**带来源**作答。

## 能做什么

- **查条文**：问"公路用地范围怎么规定"，自动检索规范条文并作答
- **规范对比**：问"城市道路和公路的设计速度有什么不同"，对比两份规范
- **单位换算**：规范里的数值自动换算（如 5.00 m → 500 cm）
- **不编造**：条文里没有答案时，明确回答"没有找到相关规定"（防幻觉）

## 项目结构

```
traffic-agent/
├── config.py            # 配置中心（模型、检索参数、提示词）
├── main.py              # 程序入口
├── agent/
│   └── agent.py         # Agent 核心（工具注册 + ReAct 主循环）
├── tools/
│   ├── search_tools.py  #   工具：查条文 / 规范对比
│   └── unit_tools.py    #   工具：单位换算
├── rag/
│   ├── store.py         #   向量库连接
│   ├── pdf_to_text.py   #   ① PDF → OCR → 文字
│   ├── split_text.py    #   ② 文字 → 切分
│   ├── build_index.py   #   ③ 切分 → 向量入库
│   └── search_test.py   #   ④ 检索测试
└── docs/                # 规范文本数据（OCR 提取）
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置 API Key

```bash
cp .env.example .env
# 编辑 .env，填入你的 DeepSeek API Key
```

### 3. 构建向量库（首次运行需要）

```bash
python rag/split_text.py    # 切分文本（生成 docs/chunks.json）
python rag/build_index.py   # 向量化入库（生成本地向量库 chroma_db/）
```

### 4. 运行 Agent

```bash
python main.py
```

## 数据来源

| 规范 | 来源 |
|---|---|
| 《城市道路交通工程项目规范》GB55011-2021 | 住房和城乡建设部官网公开 |
| 《公路工程技术标准》JTG B01-2014 | 交通运输部官网公开 |

> 原始文件为扫描版 PDF，通过 `rag/pdf_to_text.py`（OCR）转为文字后切分入库。

## 技术栈

ChromaDB · fastembed (bge-small-zh-v1.5) · DeepSeek API · rapidocr (OCR)

## License

MIT
