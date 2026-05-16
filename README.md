# Agentic AI Test Automation Framework

An enterprise-grade, autonomous test automation platform built with LangGraph, Claude (Anthropic), FAISS, and Playwright. It accepts plain-English or JSON test cases, generates Playwright/pytest scripts via a multi-agent RAG pipeline, self-heals broken locators at runtime, and ships a full observability stack via LangSmith, Allure, and AWS S3.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         INPUT LAYER                             │
│  Plain English  ──→  LLM Formatter (Claude Sonnet)             │
│  Manual JSON    ──→  Pydantic Validator + Structurer            │
└──────────────────────────────┬──────────────────────────────────┘
                               ↓
┌─────────────────────────────────────────────────────────────────┐
│                       RAG PIPELINE                              │
│  FAISS Vector Store ←── sentence-transformers embeddings        │
│  Retrieval Agent    ──→ similar past scripts (context)         │
│  Intent Agent       ──→ action + field + value extraction      │
│  Script Generator   ──→ Playwright Python / pytest scripts     │
└──────────────────────────────┬──────────────────────────────────┘
                               ↓
┌─────────────────────────────────────────────────────────────────┐
│               SELF-HEALING ENGINE  (LangGraph DAG)              │
│                                                                 │
│  failure_analyzer → dom_capture → memory_retriever             │
│       → embedding_locator_healer → validator                   │
│       → memory_updater → logic_healer → report_generator       │
│                                                                 │
│  Confidence threshold: 0.7  |  Vector store: ChromaDB + FAISS  │
└──────────────────────────────┬──────────────────────────────────┘
                               ↓
┌─────────────────────────────────────────────────────────────────┐
│              EXECUTION LAYER  (AWS Free Tier)                   │
│  Docker Container → EC2 t2.micro (750 hrs/month free)          │
│  Jenkins Pipeline → sanity | regression | full | security      │
│  Secrets → AWS SSM Parameter Store (free, never hardcoded)     │
└──────────────────────────────┬──────────────────────────────────┘
                               ↓
┌─────────────────────────────────────────────────────────────────┐
│           REPORTING + OBSERVABILITY LAYER                       │
│  Allure HTML Report → boto3 → AWS S3 (5 GB free)               │
│  LangSmith  → every node traced, latency, state, retries       │
│  RAGAS      → retrieval quality gates (faithfulness, recall)   │
│  DeepEval   → LLM output quality gates (correctness, safety)   │
│  OWASP LLM  → adversarial test suite (LLM01, LLM02, LLM08)    │
└─────────────────────────────────────────────────────────────────┘
```

---

## Test Suites

| Suite | Tests | What it covers |
|---|---|---|
| Unit | 12 | Isolated node testing, LLM mocking |
| Security | 7 | OWASP LLM01/LLM02/LLM08 adversarial inputs |
| Regression | 8 | Golden output gates — run after every prompt change |
| Evaluation | 9 | RAGAS faithfulness + DeepEval correctness/safety |
| Async | 4 | pytest-asyncio async node tests |
| Integration | 3 | Full LangGraph graph end-to-end |
| UI | 4 | Playwright Python + Allure + network interception |
| API | 4 | pytest + httpx async + Allure |

**Total: 51 tests**

---

## Quick Start

### Prerequisites

- Python 3.10+
- Docker (for containerised runs)
- Allure CLI (`npm install -g allure-commandline` or `brew install allure`)

### 1. Clone and set up environment

```bash
git clone <repo-url>
cd langgraph-project

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
playwright install chromium
```

### 2. Configure secrets (never hardcode keys)

```bash
cp .env.example .env
# Open .env and fill in your keys
```

```env
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=ls__your_key_here
LANGCHAIN_PROJECT=langgraph-healing-engine
ANTHROPIC_API_KEY=sk-ant-your_key_here
```

> If `ANTHROPIC_API_KEY` is not set, the system falls back to local Ollama automatically.
> If `LANGCHAIN_TRACING_V2=false`, tests run without sending traces to LangSmith.

### 3. Run tests

```bash
# Fast CI suite — unit + security + regression + evaluation (no browser, no API cost)
LANGCHAIN_TRACING_V2=false pytest tests/unit tests/security tests/regression tests/evaluation -v

# UI tests (needs playwright install chromium)
pytest tests/ui -v

# API tests
pytest tests/api -v

# Full suite with Allure report
pytest tests/ -v --alluredir=allure-results
allure generate allure-results --clean -o allure-report
allure open allure-report
```

### 4. Run via Docker

```bash
# Build image
docker build -t langgraph-agent-tests .

# Run unit + security + regression
docker run --rm \
  -e LANGCHAIN_TRACING_V2=false \
  -v $(pwd)/allure-results:/app/allure-results \
  langgraph-agent-tests

# Run specific suite via docker-compose
docker-compose run unit-tests
docker-compose run ui-tests
docker-compose run evaluation-tests
```

---

## Self-Healing Engine

The healing engine is a LangGraph `StateGraph` with 8 nodes:

```
failure_analyzer
    ↓ always
dom_capture
    ↓ always
memory_retriever
    ↓ always
embedding_locator_healer   ← cosine similarity via FAISS/sentence-transformers
    ↓ always
validator
    ↓ conditional (validation_success = True)
memory_updater ──→ logic_healer ──→ report_generator
    ↓ conditional (validation_success = False)
report_generator
```

### How to trigger the healing engine manually

```python
from dotenv import load_dotenv
load_dotenv()

from core.healing_engine import HealingEngine
from unittest.mock import MagicMock, patch
import numpy as np

driver = MagicMock()
driver.page_source = '<html><body><input id="username"/></body></html>'
driver.save_screenshot.return_value = None
driver.find_element.return_value = MagicMock()

with patch('agents.memory_retriever.store') as ms, \
     patch('agents.memory_updater.vector_store') as vs, \
     patch('agents.memory_updater.locator_store') as ls, \
     patch('agents.memory_updater.source_updater') as su, \
     patch('agents.embedding_locator_healer.engine') as eng:

    eng.embed.return_value = np.array([1.0, 0.0, 0.0])
    eng.similarity.return_value = 0.85
    ms.search.return_value = {'documents': [], 'metadatas': []}

    engine = HealingEngine()
    report = engine.heal(
        driver=driver,
        failed_locator=('id', 'user_name_wrong'),
        failed_action='type',
        error_message='NoSuchElementException',
        stack_trace='',
        test_file='test_login.py'
    )
    print(report)
```

Then open `smith.langchain.com` to see the full node-by-node trace.

---

## Jenkins Pipeline

The `Jenkinsfile` defines a multi-suite pipeline with suite selection at trigger time:

| Suite parameter | What runs |
|---|---|
| `sanity` | Unit + API tests |
| `regression` | Unit + UI + API tests |
| `security` | Unit + adversarial OWASP tests |
| `evaluation` | RAGAS + DeepEval quality gates |
| `full` | Everything |

Pipeline stages in order:
1. Checkout → Build Docker image → Unit tests → UI tests → API tests → Security tests → RAG Evaluation → Generate Allure report → Upload to S3

---

## AWS Setup (Free Tier)

All AWS services used are within the free tier:

| Service | Usage | Free tier |
|---|---|---|
| EC2 t2.micro | Run Jenkins + Docker | 750 hrs/month free |
| S3 | Store Allure reports | 5 GB free |
| SSM Parameter Store | Store secrets | Free (standard params) |

> **Why SSM Parameter Store and not Secrets Manager?**
> SSM Standard parameters are free. Secrets Manager costs $0.40/secret/month. For this use case, SSM is sufficient and zero cost.

### Store secrets in SSM (run once on your AWS account)

```bash
aws ssm put-parameter \
  --name "/langgraph/anthropic-api-key" \
  --value "sk-ant-your-key" \
  --type SecureString \
  --region us-east-1

aws ssm put-parameter \
  --name "/langgraph/langsmith-api-key" \
  --value "ls__your-key" \
  --type SecureString \
  --region us-east-1
```

### Upload Allure report to S3 manually

```bash
python analytics/s3_uploader.py \
  --bucket your-bucket-name \
  --report-dir allure-report \
  --build-id 1 \
  --region us-east-1
```

---

## Security

### This repo is public — are secrets safe?

**Yes.** The project is designed for public repos:

- `.env` is in `.gitignore` — never committed, never in git history
- All code reads keys via `os.getenv()` — no hardcoded values anywhere
- `.env.example` contains only placeholder text — safe to commit
- Production secrets live in AWS SSM Parameter Store, not in code
- Jenkins reads secrets via `credentials()` binding — never printed in logs

### What someone gets if they clone this repo

- All source code — expected for an open-source project
- `.env.example` — placeholder values only
- No API keys, no credentials, no tokens

### OWASP LLM Top 10 controls implemented

| Control | What is implemented |
|---|---|
| LLM01 Prompt Injection | Adversarial test suite with 5 injection payloads |
| LLM02 Insecure Output | Pydantic output validation, dangerous content gate in DeepEval tests |
| LLM08 Excessive Agency | Tool allow-listing, memory_updater blocked on failed healing |

### One rule — never break this

```bash
# NEVER run this
git add .env

# If you accidentally did — rotate your keys immediately
# Then remove from history:
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch .env" HEAD
```

---

## Project Structure

```
langgraph-project/
├── agents/                    # LangGraph node functions (each @traceable)
│   ├── failure_analyzer.py
│   ├── dom_capture.py
│   ├── memory_retriever.py
│   ├── embedding_locator_healer.py
│   ├── validator.py
│   ├── memory_updater.py
│   ├── logic_healer.py
│   ├── report_generator.py
│   └── async_report_generator.py
├── core/
│   ├── langgraph_builder.py   # StateGraph definition with conditional edges
│   ├── healing_engine.py      # Orchestrator with LangSmith tracing
│   └── state.py               # HealingState TypedDict
├── auto_generator/
│   ├── llm_client.py          # AnthropicClient + OllamaClient tiered router
│   ├── intent_extractor.py    # Plain text → structured JSON via LLM
│   ├── page_planner.py        # Structured steps → POM blueprint
│   └── code_generator.py      # Blueprint → Playwright/pytest files
├── memory/
│   ├── vector_store.py        # ChromaDB (healing memory)
│   └── faiss_store.py         # FAISS (script retrieval for auto-gen)
├── embedding/
│   └── embedding_engine.py    # sentence-transformers all-MiniLM-L6-v2
├── analytics/
│   └── s3_uploader.py         # boto3 Allure → S3 + SSM metadata
├── tests/
│   ├── unit/                  # Isolated node tests with LLM mocking
│   ├── security/              # OWASP adversarial tests
│   ├── regression/            # Golden output gates
│   ├── evaluation/            # RAGAS + DeepEval quality gates
│   ├── integration/           # Full graph end-to-end tests
│   ├── ui/                    # Playwright Python + Allure
│   └── api/                   # pytest-asyncio + Allure
├── Dockerfile                 # Containerised test execution
├── docker-compose.yml         # Multi-suite isolated runs
├── Jenkinsfile                # Multi-suite CI/CD pipeline
├── pytest.ini                 # asyncio_mode = auto
└── .env.example               # Template — copy to .env, never commit .env
```

---

## LLM Evaluation Metrics Reference

| Metric | Tool | What it measures | Threshold |
|---|---|---|---|
| Faithfulness | RAGAS | Answer grounded in retrieved context | ≥ 0.75 |
| Context Relevance | RAGAS | Retrieved docs relevant to query | ≥ 0.20 |
| Answer Relevancy | RAGAS | Answer addresses the question | ≥ 0.70 |
| Hallucination | DeepEval | Claims not supported by context | 0.0 (none allowed) |
| Correctness | DeepEval | Output matches expected structure | Schema validated |
| Toxicity | DeepEval | Harmful/dangerous content in output | 0.0 (none allowed) |
| Confidence | Healer | Embedding similarity for locator fix | ≥ 0.70 |

---

## Maintainer

**Akram Siddiqui** — Senior SDET | Agentic AI Test Automation
- Email: siddiquiakram84@gmail.com
- GitHub: github.com/siddiquiakram84
- LinkedIn: linkedin.com/in/akram-siddiqui

License: MIT
