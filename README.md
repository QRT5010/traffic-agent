# Traffic Rules Agent

> An LLM agent that answers questions **strictly grounded in Chinese traffic engineering codes** — it searches the codes itself and always cites its sources.

[中文版](README.zh-CN.md)

## What it does

- **Ask the codes**: "How is the highway right-of-way (公路用地范围) defined?" → the agent retrieves the relevant clauses and answers with citations.
- **Compare two codes**: "What's the difference between urban roads and highways regarding design speed?" → side-by-side clause comparison (GB 55011 vs JTG B01).
- **Unit conversion**: numeric values are converted by a deterministic tool (e.g., 5.00 m → 500 cm), never by mental math.
- **No hallucination**: if the codes don't cover the question, it explicitly says so instead of making something up.

## Demo

![demo](docs/assets/demo.gif)

## Architecture

```
                ┌──────────────────┐
   You ────────▶│  app.py          │  Gradio chat UI
                │  (or main.py)    │  streaming + tool logs + citations
                └────────┬─────────┘
                         │
                ┌────────▼─────────┐        ┌───────────────┐
                │  agent/agent.py  │◀──────▶│  DeepSeek API │
                │  ReAct loop      │        └───────────────┘
                └────────┬─────────┘
                         │ tool calls
        ┌────────────────┼─────────────────┐
        ▼                ▼                 ▼
  search_rules    compare_rules     convert_unit        (tools/)
        │                │
        └────────┬───────┘
                 ▼
       Chroma vector DB  ──  651 chunks  ←  bge-small-zh-v1.5 (local)
```

**Data pipeline** (`rag/`): scanned PDFs → OCR (`pdf_to_text.py`) → noise cleaning + structure-aware chunking (`split_text.py`) → embeddings + index (`build_index.py`).

## The evaluation story: retrieval 95% → 100%

RAG quality lives or dies by retrieval, so retrieval was **measured**, not guessed. A 20-question eval set (`docs/eval_set.json`) pairs each question with expected answer keywords; `eval.py` reports how often the top-3 retrieved chunks actually contain the answer (runs fully locally, no API key needed).

| Stage | Retrieval hit rate |
|---|---|
| Baseline (fixed-size 300-char chunks, 60-char overlap) | **19 / 20 (95%)** |
| After a diagnostic pass + improving the chunking strategy | **20 / 20 (100%)** |

The failing question's answer chunk was *semantically diluted*: its first ~40% was text from the previous section plus OCR watermark fragments (it ranked **184 / 246**). The fix (`rag/split_text.py`):

- clean OCR noise (watermark fragments, page numbers),
- split **cleanly at clause (`3.1.1`) and sub-item (`1 ...`) boundaries** — no overlap tail is carried across structural boundaries,
- keep overlap **only** where the length cap forces a cut.

The previously failing chunk now ranks **#1**. Reproduce with `python eval.py`.

## Quick start

```bash
git clone https://github.com/QRT5010/traffic-agent.git
cd traffic-agent

python -m venv .venv
source .venv/Scripts/activate        # Windows (Git Bash); macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env                 # then put your DeepSeek API key in .env

# Build the vector index (run from the project root; first run downloads ~100 MB embedding model)
python rag/build_index.py            # chunks.json is included; run rag/split_text.py first to regenerate it

# Reproduce the retrieval evaluation (local only, no API key needed)
python eval.py

# Launch the web UI → http://127.0.0.1:7860
python app.py
```

> In mainland China, prefix with `HF_ENDPOINT=https://hf-mirror.com` to speed up the embedding model download.

## Project layout

```
traffic-agent/
├── config.py            # all tunable parameters (models, retrieval params, prompt)
├── main.py              # CLI entry
├── app.py               # Gradio web UI (streaming + tool logs + citations)
├── eval.py              # retrieval evaluation (20 questions → hit rate)
├── agent/agent.py       # ReAct loop + tool routing
├── tools/               # search_rules / compare_rules / convert_unit
├── rag/                 # data pipeline: pdf_to_text → split_text → build_index (+ search_test)
└── docs/                # OCR text, chunk data, eval set (source PDFs excluded)
```

## Data

| Code | Source |
|---|---|
| 《城市道路交通工程项目规范》GB 55011-2021 | Ministry of Housing and Urban-Rural Development (public) |
| 《公路工程技术标准》JTG B01-2014 | Ministry of Transport (public) |

The original files are **scanned PDFs**; they were converted to text with RapidOCR (150 dpi). The PDFs themselves are not redistributed in this repo — the extracted text lives under `docs/`.

## Tech stack

Python 3.11 · DeepSeek API (OpenAI SDK) · ChromaDB · fastembed (`BAAI/bge-small-zh-v1.5`) · RapidOCR · Gradio

## License

MIT
