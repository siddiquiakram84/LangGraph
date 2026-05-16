# Agentic AI Test Automation Framework

> **Senior Software Engineer · Agentic AI Engineer & Tester**
> Built with LangGraph · Playwright · Claude (Anthropic) · FAISS · LangSmith

An enterprise-grade autonomous test automation platform that accepts manual test cases in any format, generates production-ready Playwright scripts via a multi-agent RAG pipeline, validates them with 11 AI metrics before execution, self-heals broken locators at runtime, and ships a full observability stack.

---

## Repository Structure

```
langgraph-project/
├── ai/                          # All AI components
│   ├── auto_generator/          # 10-step agentic generation pipeline
│   ├── auto_heal/               # LangGraph self-healing engine (8 nodes)
│   ├── tests/                   # 54 AI test cases
│   ├── demos/                   # Runnable demos for each component
│   └── memory/                  # FAISS runtime state (gitignored)
│
├── automation-project/          # 7-Layer Playwright + API framework
│   ├── config/                  # Layer 1 — Settings
│   ├── core/                    # Layer 2 — DriverFactory, WaitHelper
│   ├── utils/                   # Layer 3 — Logger, AllureHelper, ScreenshotHelper
│   ├── services/                # Layer 4 — ApiClient, GitHubApiService, JSONPlaceholderService
│   ├── pages/                   # Layer 5 — BasePage, LoginPage, DynamicControlsPage
│   ├── tests/                   # Layer 6 — UI + API test suites
│   ├── data/                    # Test data (JSON files per suite)
│   └── locators/                # Locator classes (generated/ by pipeline)
│
├── input_manual_test_case/      # Drop test cases here — any format
│   ├── ui/json/                 # UI tests in JSON format
│   ├── ui/excel/                # UI tests in CSV/Excel format
│   ├── ui/text/                 # UI tests in plain text format
│   ├── api/json/                # API tests in JSON format
│   ├── api/excel/               # API tests in CSV/Excel format
│   └── api/text/                # API tests in plain text format
│
├── report/                      # All reports (gitignored — generated)
│   ├── allure/html/             # Allure HTML report
│   ├── allure/results/          # Allure raw results
│   ├── analytics/               # Dashboard + pipeline reports
│   ├── playwright/              # Screenshots, videos, PDFs
│   └── healing/                 # Self-healing event reports
│
├── main.py                      # Pipeline entry point
├── Dockerfile                   # Containerised test execution
├── docker-compose.yml           # Multi-suite isolated runs
├── Jenkinsfile                  # Multi-suite CI/CD pipeline
├── requirements.txt
└── .env.example                 # Copy to .env — never commit .env
```

---

## Architecture

```
┌──────────────────────────────────────────────────────────────────────┐
│                        INPUT LAYER                                   │
│  input_manual_test_case/ui/json/    ──→  JSON parser                │
│  input_manual_test_case/ui/excel/   ──→  CSV / openpyxl parser      │
│  input_manual_test_case/ui/text/    ──→  Structured text parser     │
│  input_manual_test_case/api/*/      ──→  Same, generates API tests  │
└────────────────────────────┬─────────────────────────────────────────┘
                             ↓
┌──────────────────────────────────────────────────────────────────────┐
│                     AI GENERATION PIPELINE  (main.py)               │
│                                                                      │
│  Step 1  InputParser       → normalise any format → standard dict   │
│  Step 2  IntentExtractor   → Claude Sonnet / Ollama / LocalLLM      │
│  Step 3  FAISSScriptStore  → RAG: retrieve top-3 similar scripts    │
│  Step 4  PagePlanner       → blueprint: page, methods, locators     │
│  Step 5  CodeGenerator     → 7-layer POM files → automation-project │
│  ─────── AI VALIDATION GATE ──────────────────────────────────────  │
│  Step 6  AIValidator       → 11 metrics (RAGAS-proxy + DeepEval)    │
│  Step 7  Gate              → FAIL → PipelineReporter → exit         │
│  ─────── EXECUTION ────────────────────────────────────────────────  │
│  Step 8  TestExecutor      → subprocess pytest automation-project/  │
│  Step 9  Auto-heal gate    → patch #TODO_ locators → retry once     │
│  Step 10 PipelineReporter  → JSON report + FAISS store              │
└────────────────────────────┬─────────────────────────────────────────┘
                             ↓
┌──────────────────────────────────────────────────────────────────────┐
│              SELF-HEALING ENGINE  (LangGraph StateGraph)             │
│                                                                      │
│  failure_analyzer  →  dom_capture  →  memory_retriever              │
│       →  embedding_locator_healer  →  validator                     │
│       →  [confidence ≥ 0.7] memory_updater → logic_healer           │
│       →  [confidence < 0.7] report_generator → manual review        │
│                                                                      │
│  Vector stores: ChromaDB (healing events) + FAISS (scripts)         │
│  Embeddings:    sentence-transformers all-MiniLM-L6-v2 (384-dim)    │
│  AST patching:  source_updater.py → locator file updated in-place   │
└────────────────────────────┬─────────────────────────────────────────┘
                             ↓
┌──────────────────────────────────────────────────────────────────────┐
│                 REPORTING + OBSERVABILITY                             │
│  Allure HTML    → report/allure/html/index.html                     │
│  Dashboard      → report/analytics/dashboard.html  (Chart.js)       │
│  LangSmith      → every node traced, latency, state, retries        │
│  RAGAS proxy    → retrieval quality gates (faithfulness, recall)    │
│  DeepEval       → structural output validation                       │
│  OWASP LLM      → adversarial suite (LLM01, LLM02, LLM08)          │
└──────────────────────────────────────────────────────────────────────┘
```

---

## Test Suites — 78 Tests, 100% Pass Rate

### AI Framework Tests — `ai/tests/` (54 tests)

| Suite | File | Tests | Covers |
|---|---|---|---|
| Unit | `test_failure_analyzer.py` | 8 | Failure classification — locator / timeout / assertion |
| Unit | `test_embedding_locator_healer.py` | 4 | Cosine similarity, confidence threshold, empty DOM |
| Unit | `test_async_report_generator.py` | 4 | Async report schema, success/fail fields |
| Unit | `test_validator.py` | 4 | Healed locator validation, strategy selection |
| Security | `test_adversarial.py` | 7 | OWASP LLM01 prompt injection, LLM02 output, LLM08 agency |
| Regression | `test_golden_outputs.py` | 10 | Golden output gates — detect any LLM/prompt degradation |
| Integration | `test_healing_graph.py` | 3 | Full LangGraph graph: heal → validate → memory update |
| Evaluation | `test_ragas_evaluation.py` | 4 | Faithfulness, context relevance, answer quality |
| Evaluation | `test_deepeval_evaluation.py` | 5 | Output structure, dangerous content, schema correctness |
| **Total** | | **54** | **Unit → Integration → Security → Evaluation** |

### Automation Framework Tests — `automation-project/tests/` (24 tests)

| Suite | File | Tests | Target |
|---|---|---|---|
| UI — Login Flow | `test_login_flow.py` | 5 | the-internet.herokuapp.com/login — valid + 3 invalid + logout |
| UI — Dynamic Controls | `test_dynamic_controls.py` | 4 | Checkbox add/remove, input enable/disable (AJAX) |
| API — GitHub Service | `test_github_service.py` | 7 | User profile schema, repos, 404, search, rate limit |
| API — JSONPlaceholder | `test_jsonplaceholder_service.py` | 8 | GET list/id, POST, PUT, DELETE, comments |
| **Total** | | **24** | **2 UI + 2 API — all 7 layers demonstrated** |

**Grand Total: 78 tests · 100% pass rate**

---

## Quick Start

### Prerequisites

```bash
Python 3.10+
Node.js (for Allure CLI)
npm install -g allure-commandline
```

### 1. Clone and set up

```bash
git clone <repo-url>
cd langgraph-project

python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
playwright install chromium
```

### 2. Configure secrets

```bash
cp .env.example .env
```

```env
# LangSmith observability (optional — tests run without it)
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=ls__your_key_here
LANGCHAIN_PROJECT=langgraph-healing-engine

# LLM for script generation (optional — falls back to Ollama then local)
ANTHROPIC_API_KEY=sk-ant-your_key_here

# Browser settings
BROWSER=chromium
HEADLESS=true
PYTHONDONTWRITEBYTECODE=1
```

> **No API key?** The system auto-falls back: `Claude → Ollama → LocalClassifier`. All 78 tests run with zero API cost.

### 3. Run all tests

```bash
# AI framework tests (54 tests, no browser needed)
venv/bin/python3 -m pytest ai/tests/ -v

# Automation framework tests (24 tests — UI + API)
python3 -m pytest automation-project/tests/ -v

# With Allure report
python3 -m pytest automation-project/tests/ \
  --alluredir=report/allure/results -v
allure generate report/allure/results \
  --output report/allure/html --clean
allure open report/allure/html
```

### 4. Run the AI generation pipeline

```bash
# Process all files in input_manual_test_case/ (any format)
python3 main.py

# Run a single file
python3 main.py --input input_manual_test_case/ui/json/TC_LOGIN_FLOW_01.json
python3 main.py --input input_manual_test_case/ui/excel/TC_DYNAMIC_CONTROLS_02.csv
python3 main.py --input input_manual_test_case/ui/text/TC_CHECKOUT_FLOW_03.txt

# List all discovered input files
python3 main.py --list-inputs
```

### 5. Run via Docker

```bash
docker build -t langgraph-agent-tests .

docker run --rm \
  -e LANGCHAIN_TRACING_V2=false \
  -v $(pwd)/report:/app/report \
  langgraph-agent-tests

# Multi-suite via docker-compose
docker-compose run unit-tests
docker-compose run ui-tests
docker-compose run evaluation-tests
```

---

## 7-Layer Framework Architecture

Every test in `automation-project/` follows the same dependency chain:

| Layer | Directory | Responsibility |
|---|---|---|
| **L1 Config** | `config/settings.py` | All URLs, timeouts, report paths from env. No `os.getenv()` in tests. |
| **L2 Core** | `core/driver_factory.py` | Playwright browser/context/page lifecycle. Session-scoped fixtures via conftest. |
| **L3 Utils** | `utils/` | `get_logger`, `AllureHelper`, `ScreenshotHelper`, `PDFHelper` |
| **L4 Service** | `services/` | `ApiClient` (HTTP) → `GitHubApiService`, `JSONPlaceholderService`. Tests never construct URLs. |
| **L5 Page Object** | `pages/` | `BasePage` → `LoginPage`, `DynamicControlsPage`, `HomePage`. Locators defined as class constants, never in test files. |
| **L6 Test** | `tests/` | Class-based, `@allure.suite/feature/story/severity`, data loaded from `data/`. |
| **L7 Reporting** | `report/` + `conftest.py` | Auto-screenshot + page source on failure. Per-test JSON summary. Allure HTML + analytics dashboard. |

### BasePage contract

```python
# Tests call this — they never call page.locator() directly
class LoginPage(BasePage):
    USERNAME_INPUT = "#username"

    @allure.step("Login with username='{username}'")
    def login(self, username: str, password: str) -> "LoginPage":
        self.fill(self.USERNAME_INPUT, username, "Username")  # BasePage.fill()
        self.fill(self.PASSWORD_INPUT, password, "Password")
        self.click(self.LOGIN_BUTTON, "Login button")         # BasePage.click()
        return self
```

---

## AI Validation Gate — 11 Metrics

Run before every generated test is executed. If fewer than 70% pass, the pipeline stops.

| # | Metric | Category | Threshold | What it checks |
|---|---|---|---|---|
| 1 | Semantic Similarity | RAGAS | ≥ 0.55 | Cosine similarity between intent steps and generated page code |
| 2 | Faithfulness | RAGAS | ≥ 0.75 | All blueprint methods are present in the generated page |
| 3 | Hallucination Detection | RAGAS | ≤ 0.30 | Extra methods not derived from steps |
| 4 | Grounding Validation | RAGAS | ≥ 0.45 | Locator vocabulary overlaps with RAG-retrieved context |
| 5 | Retrieval Relevance | RAGAS | ≥ 0.25 | Top FAISS similarity score for retrieved script |
| 6 | Context Propagation | DeepEval | ≥ 0.75 | `allure.step()` blocks in test file match method count |
| 7 | Probabilistic Consistency | DeepEval | ≤ 0.15 | Std-dev of method-name similarities (naming coherence) |
| 8 | Non-Determinism Tolerance | DeepEval | ≤ 0.20 | Fraction of locators still at `#TODO_` placeholder |
| 9 | Threshold Pass Rate | Orchestration | ≥ 0.70 | % of metrics 1–8 that passed |
| 10 | Agent Orchestration | Orchestration | ≥ 0.80 | Pipeline stages completed ratio |
| 11 | Observability/Tracing | Observability | ≥ 0.50 | LangSmith env vars configured |

---

## Self-Healing Engine — LangGraph StateGraph

```
                    HealingState (TypedDict)
                           │
              ┌────────────▼────────────┐
              │     failure_analyzer    │  classify: locator / timeout / assertion
              └────────────┬────────────┘
                           │
              ┌────────────▼────────────┐
              │       dom_capture       │  screenshot + page source
              └────────────┬────────────┘
                           │
              ┌────────────▼────────────┐
              │     memory_retriever    │  ChromaDB: past healing events
              └────────────┬────────────┘
                           │
              ┌────────────▼────────────┐
              │ embedding_locator_healer│  FAISS cosine similarity → candidate locators
              └────────────┬────────────┘
                           │
              ┌────────────▼────────────┐
              │        validator        │  confidence ≥ 0.7?
              └──────┬─────────┬────────┘
                     │         │
              [YES]  │         │  [NO]
                     ▼         ▼
             memory_updater   report_generator
             logic_healer          ↓
             report_generator   manual review
```

### Trigger the healing engine

```python
from ai.auto_heal.core.healing_engine import HealingEngine
from unittest.mock import MagicMock, patch
import numpy as np

driver = MagicMock()
driver.page_source = '<html><input id="username"/></html>'

with patch("ai.auto_heal.agents.embedding_locator_healer.engine") as eng, \
     patch("ai.auto_heal.agents.memory_retriever.store") as store:

    eng.embed.return_value = np.array([1.0, 0.0, 0.0])
    eng.similarity.return_value = 0.85
    store.search.return_value = {"documents": [], "metadatas": []}

    engine = HealingEngine()
    report = engine.heal(
        driver        = driver,
        failed_locator = ("id", "user_name_wrong"),
        failed_action  = "click",
        error_message  = "NoSuchElementException",
        stack_trace    = "",
        test_file      = "test_login.py",
    )
    print(report)
    # → {"success": True, "healed_locator": ("id", "username"), "confidence": 0.85, ...}
```

---

## Input File Formats

Drop any file into `input_manual_test_case/ui/` or `input_manual_test_case/api/` and run `python3 main.py`.

### JSON (`.json`)

```json
{
  "test_case_id": "TC_LOGIN_01",
  "module": "login_page",
  "base_url": "https://the-internet.herokuapp.com/login",
  "steps": [
    {"tc_msg_action": "Enter username tomsmith", "tc_msg_expected": "Field is populated"},
    {"tc_msg_action": "Click login button",      "tc_msg_expected": "Secure area opens"}
  ]
}
```

### CSV / Excel (`.csv` or `.xlsx`)

```
test_case_id,module,base_url,step_action,step_expected
TC_LOGIN_01,login_page,https://...,Enter username tomsmith,Field is populated
TC_LOGIN_01,login_page,https://...,Click login button,Secure area opens
```

### Plain Text (`.txt`)

```
TEST_CASE_ID: TC_LOGIN_01
MODULE: login_page
BASE_URL: https://the-internet.herokuapp.com/login
---
STEP: Enter username tomsmith
EXPECTED: Field is populated
---
STEP: Click login button
EXPECTED: Secure area opens
```

---

## CI/CD

### GitHub Actions (`.github/workflows/`)

```
install → AI tests → Automation tests → Allure report → Upload artifacts
```

### Jenkins (`Jenkinsfile`)

| Suite parameter | What runs |
|---|---|
| `sanity` | Unit + API tests |
| `regression` | Unit + UI + API tests |
| `security` | Unit + OWASP adversarial tests |
| `evaluation` | RAGAS + DeepEval quality gates |
| `full` | All 78 tests |

Stages: `Checkout → Docker Build → Unit → UI → API → Security → Evaluation → Allure Generate → S3 Upload`

---

## Reporting

| Report | Location | How to open |
|---|---|---|
| Allure HTML | `report/allure/html/index.html` | `allure open report/allure/html` |
| Analytics Dashboard | `report/analytics/dashboard.html` | Open in browser |
| Pipeline Reports | `report/analytics/pipeline_report_*.json` | Generated per run |
| Screenshots | `report/playwright/screenshots/` | Auto-captured on test failure |
| Healing Reports | `report/healing/healing_reports/` | JSON per healing event |

### Dashboard features
- KPI cards: total tests, pass rate, healing events
- Bar chart: tests by suite
- Doughnut chart: pass / fail distribution
- Suite breakdown tables with per-suite status badges
- Auto-heal event timeline
- 7-layer architecture table with report links
- AI pipeline component status (LLM Router, FAISS, ChromaDB, LangSmith)

---

## LLM Evaluation Metrics Reference

| Metric | Tool | Threshold |
|---|---|---|
| Semantic Similarity | RAGAS-proxy (embedding cosine) | ≥ 0.55 |
| Faithfulness | RAGAS-proxy (method coverage) | ≥ 0.75 |
| Hallucination | RAGAS-proxy (extra method ratio) | ≤ 0.30 |
| Grounding | RAGAS-proxy (token overlap) | ≥ 0.45 |
| Retrieval Relevance | FAISS similarity score | ≥ 0.25 |
| Context Propagation | DeepEval-structural | ≥ 0.75 |
| Probabilistic Consistency | DeepEval-structural | ≤ 0.15 |
| Non-Determinism Tolerance | DeepEval-structural | ≤ 0.20 |
| Healing Confidence | EmbeddingEngine cosine | ≥ 0.70 |

---

## Security

```
✅  .env is in .gitignore — never committed
✅  All keys via os.getenv() — no hardcoded values anywhere
✅  .env.example has placeholder text only — safe to commit
✅  Production secrets → AWS SSM Parameter Store (free tier)
✅  OWASP LLM Top 10 adversarial test suite (7 tests)
✅  PYTHONDONTWRITEBYTECODE=1 — no .pyc files committed
```

### OWASP LLM coverage

| Control | What is tested |
|---|---|
| LLM01 Prompt Injection | 5 injection payloads in error messages — healer must ignore them |
| LLM02 Insecure Output | Dangerous content gate, schema validation in DeepEval tests |
| LLM08 Excessive Agency | `memory_updater` blocked when healing fails — no writes on bad confidence |

### Never do this

```bash
git add .env          # NEVER — rotate keys immediately if you did
```

---

## AWS Setup (Free Tier)

| Service | Usage | Free tier |
|---|---|---|
| EC2 t2.micro | Jenkins + Docker | 750 hrs/month |
| S3 | Allure report storage | 5 GB |
| SSM Parameter Store | Secrets — API keys | Free (standard) |

```bash
# Store secrets once
aws ssm put-parameter \
  --name "/langgraph/anthropic-api-key" \
  --value "sk-ant-your-key" \
  --type SecureString --region us-east-1

# Upload Allure to S3
python3 report/analytics/s3_uploader.py \
  --bucket your-bucket --report-dir report/allure/html \
  --build-id 1 --region us-east-1
```

---

## Tech Stack

| Category | Technology |
|---|---|
| AI / Agents | LangGraph · LangChain · Claude Sonnet (Anthropic) · Ollama |
| Embeddings | sentence-transformers `all-MiniLM-L6-v2` (384-dim) |
| Vector Stores | FAISS (script retrieval) · ChromaDB (healing memory) |
| Test Framework | pytest · pytest-asyncio · Playwright Python |
| Evaluation | RAGAS-proxy · DeepEval structural · LangSmith `@traceable` |
| Reporting | Allure · Chart.js dashboard · ScreenshotHelper |
| CI/CD | GitHub Actions · Jenkins · Docker · docker-compose |
| Cloud | AWS SSM Parameter Store · S3 · EC2 |
| Language | Python 3.10+ |

---

## Maintainer

**Akram Siddiqui** — Senior SDET · Agentic AI Engineer & Tester

- Email: [siddiquiakram84@gmail.com](mailto:siddiquiakram84@gmail.com)
- LinkedIn: [linkedin.com/in/akram-siddiqui](https://linkedin.com/in/akram-siddiqui)
- GitHub: [github.com/siddiquiakram84](https://github.com/siddiquiakram84)

---

*License: MIT*
