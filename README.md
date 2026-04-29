<div align="center">

# 👶 Mumzworld AI Customer Copilot

### Intelligent Gift Finder + Customer Support Triage
#### Bilingual · English + Arabic · RAG · Agent Architecture · Structured Output

[![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![Groq](https://img.shields.io/badge/LLM-Llama%203.3%2070B%20via%20Groq-F55036?style=flat-square)](https://console.groq.com)
[![ChromaDB](https://img.shields.io/badge/Vector%20DB-ChromaDB-orange?style=flat-square)](https://trychroma.com)
[![Streamlit](https://img.shields.io/badge/UI-Streamlit-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)](https://streamlit.io)
[![License: MIT](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)

> **Track A — AI Engineering Intern Assignment**
> A production-style agentic AI prototype for Mumzworld that routes customer queries, finds gifts via semantic search, triages support requests, and responds natively in both English and Arabic.

---

[Quick Start](#-quick-start) · [Architecture](#-architecture) · [Evaluation](#-evaluation) · [Tradeoffs](#-tradeoffs) · [Tooling](#-tooling)

</div>

---

## ✨ What it does

A customer types a natural-language query. The system:

| Step | What happens |
|------|-------------|
| **1. Route** | Llama 3.3 70B classifies the query as `gift_finder` or `support` with a confidence score |
| **2. Retrieve** | ChromaDB finds the top-5 semantically matching products from a 100-product catalogue |
| **3. Reason** | The LLM ranks results, injects personalised reasons, and checks budget constraints |
| **4. Validate** | Pydantic v2 schemas enforce output structure — malformed JSON is caught, never silently passed |
| **5. Respond** | Returns bilingual output: warm English + native Gulf Arabic (not a translation) |
| **6. Escalate** | Refunds, complaints, and low-confidence responses auto-flag for a human agent |

---

## 🏗 Architecture

```
                        ┌──────────────────────────────┐
                        │         User Query            │
                        └──────────────┬───────────────┘
                                       │
                        ┌──────────────▼───────────────┐
                        │    Router (Llama 3.3 70B)     │
                        │  → gift_finder | support       │
                        │  → confidence: float (0–1)     │
                        └──────┬───────────────┬────────┘
                               │               │
               ┌───────────────▼──┐     ┌──────▼──────────────┐
               │   Gift Finder    │     │   Support Tool       │
               │                  │     │                      │
               │ 1. Extract       │     │ 1. Classify intent   │
               │    constraints   │     │    (order/refund/    │
               │    (budget, age) │     │     complaint/other) │
               │ 2. ChromaDB      │     │ 2. Set urgency       │
               │    semantic      │     │ 3. Escalate if       │
               │    search        │     │    refund/complaint  │
               │ 3. LLM ranks +   │     │    or conf < 0.6     │
               │    reasons       │     │                      │
               └──────────────────┘     └──────────────────────┘
                               │               │
                        ┌──────▼───────────────▼────────┐
                        │    Pydantic Schema Validation   │
                        │    GiftFinderOutput | SupportOutput │
                        └──────────────┬────────────────┘
                                       │
                        ┌──────────────▼───────────────┐
                        │  FinalResponse                 │
                        │  · route: str                  │
                        │  · output: dict (validated)    │
                        │  · response_en: str            │
                        │  · response_ar: str            │
                        └──────────────────────────────┘
```

**Data layer:**

```
products.json (source of truth)
    └── SQLite (mumzworld.db)          ← canonical product store
    └── ChromaDB (data/chroma/)        ← local vector index, cosine similarity
         Embeddings: all-MiniLM-L6-v2 (local, CPU, ~50ms/query)
```

---

## 🚀 Quick Start

> From clone to first output in under 5 minutes.

### Prerequisites
- Python 3.11+
- A free [Groq API key](https://console.groq.com) (no credit card required)

### 1 · Clone
```bash
git clone <repo-url>
cd Mumzworld
```

### 2 · Create virtual environment
```bash
python3.11 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
```

### 3 · Install dependencies
```bash
pip install -r requirements.txt
```

### 4 · Configure environment
```bash
cp .env.example .env
# Edit .env and add your Groq key:
# GROQ_API_KEY=gsk_your_key_here
```

### 5 · Seed database + vector index
```bash
python scripts/seed_db.py
```

Expected output:
```
Seeded 100 products into data/mumzworld.db
✅ ChromaDB ready (100 products indexed).
✅ All done!
   SQLite  → data/mumzworld.db  (100 products)
   ChromaDB → data/chroma/       (100 vectors)
```

### 6 · Launch the UI
```bash
streamlit run ui/streamlit_app.py
```

Open **http://localhost:8501** and try:
- `Gift for a newborn girl under 150 AED`
- `أريد هدية لطفل عمره سنة`
- `I want a refund for my damaged stroller`
- `What is the weather today?` ← out-of-scope

### 7 · Run evaluation suite
```bash
python scripts/eval.py
```

---

## 📁 Directory Structure

```
Mumzworld/
├── app/
│   ├── core/
│   │   └── llm_client.py        # Groq client · Llama 3.3 70B
│   ├── db/
│   │   ├── database.py          # SQLite product store + seed loader
│   │   └── retrieval.py         # ChromaDB semantic search + keyword fallback
│   ├── models/
│   │   └── schemas.py           # Pydantic v2 schemas for all outputs
│   ├── tools/
│   │   ├── router.py            # LLM-based query classifier
│   │   ├── gift_finder.py       # RAG pipeline: retrieve → reason → respond
│   │   └── support.py           # Support triage + escalation logic
│   └── main.py                  # AgenticSystem orchestrator
├── scripts/
│   ├── seed_db.py               # Load products → SQLite + ChromaDB
│   └── eval.py                  # 12-case evaluation suite (4-dimension rubric)
├── ui/
│   └── streamlit_app.py         # Production Streamlit frontend
├── data/
│   └── products.json            # 100-product Mumzworld catalogue
├── .env.example                 # Environment template
├── .gitignore
├── requirements.txt
└── README.md
```

---

## 📊 Evaluation

### Rubric

Every test case is graded on four dimensions:

| Dimension | Description |
|-----------|-------------|
| **Route** (`R`) | Router assigned the correct tool (`gift_finder` or `support`) |
| **Response** (`Rsp`) | Both English and Arabic responses are non-empty |
| **Escalation** (`Esc`) | Refund/complaint intents always set `needs_human = True` |
| **Uncertainty** (`Unc`) | Out-of-scope queries return `confidence < 0.8` |

### Test Cases

| # | Query | Expected | Type | R | Rsp | Esc | Unc |
|---|-------|----------|------|---|-----|-----|-----|
| 1 | I want a gift for a newborn baby girl | gift_finder | EN easy | ✅ | ✅ | — | — |
| 2 | Lego toys for a 2 year old boy | gift_finder | EN easy | ✅ | ✅ | — | — |
| 3 | Budget friendly diapers for 6 month old | gift_finder | EN budget | ✅ | ✅ | — | — |
| 4 | Recommendations for a first time mom under 300 AED | gift_finder | EN budget | ✅ | ✅ | — | — |
| 5 | أريد شراء هدية لطفل عمره سنتين | gift_finder | AR easy | ✅ | ✅ | — | — |
| 6 | هدية للأم الجديدة بميزانية 200 درهم | gift_finder | AR budget | ✅ | ✅ | — | — |
| 7 | Where is my order #12345? | support | EN order | ✅ | ✅ | — | — |
| 8 | I want a refund for my damaged stroller | support | EN refund | ✅ | ✅ | ✅ | — |
| 9 | My delivery is late and I am very angry | support | EN complaint | ✅ | ✅ | ✅ | — |
| 10 | هل يمكنني استرجاع المنتج؟ | support | AR refund | ✅ | ✅ | ✅ | — |
| 11 | What is the weather in Dubai today? | support | Out-of-scope | ✅ | ✅ | — | ✅ |
| 12 | Hello | support | Adversarial | ✅ | ✅ | — | ✅ |

> Run `python scripts/eval.py` to regenerate scores. Results are saved to `data/eval_results_<timestamp>.json`.

### Known Failure Modes

- **Arabic quality** is not auto-graded — would require a judge LLM, intentionally cut for scope
- **Out-of-scope gift queries** (e.g. "recommend me a laptop") may still route to `gift_finder` with low confidence rather than refusing
- **Groq rate limits** (30 req/min free tier) may cause the full eval suite to slow down slightly

---

## ⚖️ Tradeoffs

### Why Gift Finder + Support Triage?

These map to Mumzworld's two highest-volume customer touchpoints. The combination forces the system to solve non-trivial AI engineering across all required dimensions: agent routing, RAG, structured output with validation, multilingual generation, and escalation safety — all in a single scoped prototype.

### What I chose not to build

| Rejected | Why |
|---------|-----|
| Fine-tuning | Out of scope for ~5 hours; RAG gives ~90% of the value at zero training cost |
| Voice input | Interesting but requires Whisper integration, doubling the scope |
| PostgreSQL | SQLite is identical for 100–2500 products; Postgres adds ops overhead with no query benefit at this scale |
| Separate routing vs. reasoning models | Adds complexity and makes provenance harder to explain; one model does both cleanly |

### Model: Llama 3.3 70B via Groq

- **Why Groq over OpenRouter?** Groq provides 30 req/min free vs. ~5 req/min on OpenRouter's free tier — 6× more headroom for evals and demos
- **Why Llama 3.3 70B?** Strongest free model available: 128k context, strong instruction following, decent Arabic. Alternatives (Qwen, Mistral) were rate-limited during development
- **Trade-off:** A dedicated Arabic model (e.g. Jais-30B, AceGPT) would produce higher-quality Gulf Arabic. Accepted this cut for simplicity

### Vector DB: ChromaDB (local) vs. Pinecone (cloud)

- **ChromaDB** runs entirely on disk — no API key, no latency, no cost, no cloud dependency
- **Trade-off:** Does not scale past ~500k vectors on a single machine. Pinecone would be the production choice beyond prototype scale

### Embeddings: all-MiniLM-L6-v2

- 384-dimensional, runs on CPU in <50ms per query with no API calls
- **Trade-off:** Larger multilingual models (e.g. `multilingual-e5-large`) produce better Arabic embeddings. Accepted for speed and zero-dependency operation

### Uncertainty Handling

- All outputs carry `confidence: float (0–1)` from the LLM prompt
- Hard-coded safety rule: `refund` and `complaint` intents always set `needs_human = True` regardless of confidence — this is a business rule, not a model judgement
- `confidence < 0.6` also triggers escalation

### What I would build next

1. Arabic-first embedding model for better semantic matching in Arabic queries
2. Live order lookup tool (connect to Mumzworld Order API for real-time order status)
3. Streaming responses (Groq supports streaming — would make the UI feel instant)
4. LLM-as-judge eval to auto-grade Arabic naturalness
5. Scale dataset to 2500 products using the existing seed pipeline

---

## 🛠 Tooling

### Stack

| Tool | Role |
|------|------|
| **Groq API** | LLM inference — Llama 3.3 70B Versatile (128k context) |
| **ChromaDB** | Local persistent vector index, cosine similarity |
| **sentence-transformers** | Local embedding generation (all-MiniLM-L6-v2, CPU) |
| **Pydantic v2** | Schema validation and enforcement on all structured outputs |
| **Streamlit** | Production UI with custom dark theme |
| **SQLite** | Canonical product store, zero-config |
| **Antigravity (Google DeepMind)** | AI coding assistant — pair programming |

### How Antigravity was used

| Phase | Usage |
|-------|-------|
| **Architecture** | Initial system design, directory structure, module separation |
| **Code generation** | All files generated via agent loops with explicit reasoning before edits |
| **Debugging** | Identified stale model imports after LLM provider switch; fixed ChromaDB watcher noise in Streamlit |
| **Refactoring** | Cleaned up `QWEN_MODEL`/`DEEPSEEK_MODEL` aliases after Groq migration without being asked |
| **Eval design** | 4-dimension rubric design and test case selection |

### What worked

- Agent-driven generation significantly accelerated RAG pipeline setup
- The agent proactively identified misleading comments after a model change (comments said "DeepSeek R1" while Groq was running)
- Streamlit config fix (file watcher → `none`) was diagnosed and applied without manual debugging

### What didn't work

- OpenRouter free-tier models (Qwen, Llama) were all rate-limited during development — required switching to Groq mid-session
- First ChromaDB sync was slow due to embedding model downloading weights cold on first run

### Where I stepped in

- Corrected OpenRouter model IDs (agent initially used `qwen-2.5-72b-instruct:free` which returned 404)
- Made the final decision to use a single model for all tasks instead of separate routing/reasoning models
- Wrote the eval rubric dimensions and adversarial test cases

### Key prompts / system messages

The gift finder prompt explicitly instructs:
```
response_ar must read naturally in Gulf Arabic — NOT a literal translation
```

The support tool hard-codes:
```python
if result.get("intent") in ["refund", "complaint"]:
    result["needs_human"] = True   # Business rule — not model-dependent
```

---

## 📄 License

MIT — see [LICENSE](LICENSE)

---

<div align="center">
Built for the Mumzworld AI Engineering Intern Assignment · April 2026
</div>
