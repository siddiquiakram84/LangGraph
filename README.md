# LangGraph Project

A lightweight Python-based framework for automated UI testing, healing, and analysis. This repository contains modules for agents, analytics, embedding, a healing engine, and automation helpers used to generate, execute, and maintain UI tests.

This README provides a quick reference for setting up the project, running tests, and understanding the main components.

## Quick Start

Prerequisites
- Python 3.8+ (recommended 3.10)
- pip
- (Optional) virtualenv or venv

Setup

1. Create and activate a virtual environment (recommended):

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run the main entry (example):

```bash
python main.py
```

Note: Specific subprojects (like `automation-project`) may have their own requirements and test configuration. Check `automation-project/README.md` inside that folder if present.

## Running Tests

This repository uses pytest. Run tests from the project root:

```bash
pytest -q
```

You can run tests for specific modules, for example:

```bash
pytest auto_generator -q
pytest core -q
```

## Project Layout (high level)

- `auto_generator/` – utilities and LLM-driven code generators (intent extraction, code generation, page planning, LLM client wrappers).
- `agents/` – autonomous agents that perform tasks like memory retrieval/updating, validation, reporting, and DOM capture.
- `core/` – main healing engine and language-graph builder/state management.
- `framework/` – driver abstraction, smart driver, and test/config helpers.
- `embedding/` – embedding engine and related utilities.
- `automation-project/` – an example/test automation project that shows how to integrate generated tests and run suites.
- `healing_reports/`, `healing_memory/` – persisted healing reports and locator memory used by the healing engine.
- `main.py` – a simple entry point used for quick runs or demos.

## Common Commands

- Run the entry script: `python main.py`
- Run all tests: `pytest`
- Linting (if configured): `flake8` or `pylint` (not included by default)

## Contributing

- Open issues for bugs or feature requests.
- For changes:
  1. Create a feature branch.
  2. Add tests for new behavior.
  3. Submit a pull request with a clear description.

## Troubleshooting

- If a dependency fails to install, ensure you are using a supported Python version and upgrade pip: `pip install --upgrade pip`.
- If tests fail unexpectedly, run the failing test with `-k` and `-q` to focus on one scenario, and check `healing_reports/` for saved snapshots.

## License & Contact

Copyright (c) 2026 [Akram Siddiqui] (Individual Contractor)

This project is provided under the MIT License. The full license text is included in the `LICENSE` file at the repository root.

Contact
- Maintainer: [Akram Siddiqui]
- Email: siddiquiakram84@gmail.com

