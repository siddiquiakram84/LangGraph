"""
main.py  —  Agentic AI Test Automation Pipeline
================================================
Watches input_manual_test_case/ for any file in JSON / CSV / Excel / text format.
Runs a 10-step pipeline per file:

  Step  1  Parse input file  (JSON / CSV / .xlsx / .txt)
  Step  2  IntentExtractor   (Claude / Ollama / local)
  Step  3  FAISSScriptStore  — RAG context retrieval
  Step  4  PagePlanner       — blueprint
  Step  5  CodeGenerator     — write 7-layer POM files to automation-project/
  Step  6  AIValidator       — 11 metrics (RAGAS-proxy + DeepEval + tracing)
  Step  7  Gate              — if validation fails → PipelineReporter + exit
  Step  8  TestExecutor      — subprocess pytest from automation-project/
  Step  9  Auto-heal gate    — executor retries once on locator failures
  Step 10  PipelineReporter  — JSON + console report, store script in FAISS

Usage:
  python main.py                                     # scan input_manual_test_case/
  python main.py --input path/to/file.json           # run single file (any format)
  python main.py --input path/to/file.csv
  python main.py --input path/to/file.xlsx
  python main.py --input path/to/file.txt
  python main.py --list-inputs                       # list all discovered files
"""
import argparse
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

INPUT_ROOT = Path("input_manual_test_case")


def run_pipeline(file_path: str) -> None:
    from ai.auto_generator.input_parser      import InputParser
    from ai.auto_generator.intent_extractor  import IntentExtractor
    from ai.auto_generator.page_planner      import PagePlanner
    from ai.auto_generator.code_generator    import CodeGenerator
    from ai.auto_generator.ai_validator      import AIValidator
    from ai.auto_generator.test_executor     import TestExecutor
    from ai.auto_generator.pipeline_reporter import PipelineReporter
    from ai.auto_heal.memory.faiss_store     import FAISSScriptStore

    path = Path(file_path)
    print(f"\n{'='*64}")
    print(f"  AI Pipeline — {path.name}  [{path.suffix.upper()}]")
    print(f"{'='*64}\n")

    # ── Step 1: Parse input (any supported format) ────────────────────────────
    print(f"[1/10] Parsing input: {file_path}")
    test_case = InputParser.parse(path)
    print(f"       ID: {test_case['test_case_id']} | {len(test_case['steps'])} steps | "
          f"module: {test_case['module']}")

    # ── Step 2: Extract structured intent via LLM ─────────────────────────────
    print("\n[2/10] Extracting intent with LLM...")
    extractor        = IntentExtractor()
    structured_steps = extractor.extract_from_test_case(test_case)
    for i, step in enumerate(structured_steps, 1):
        print(f"       Step {i}: {step}")

    # ── Step 3: RAG — retrieve similar scripts from FAISS ────────────────────
    print("\n[3/10] Retrieving RAG context from FAISS...")
    store = FAISSScriptStore()
    query = test_case.get("module", "") + " " + " ".join(
        s.get("tc_msg_action", "") for s in test_case["steps"]
    )
    rag_context = store.search(query, top_k=3)
    if rag_context:
        print(f"       {len(rag_context)} similar scripts — "
              f"top score={rag_context[0]['similarity_score']:.2f}")
    else:
        print("       No prior scripts — generating from scratch")

    # ── Step 4: Plan page object structure ────────────────────────────────────
    print("\n[4/10] Planning page structure...")
    blueprint = PagePlanner().plan(test_case, structured_steps)
    print(f"       Page: {blueprint['page_name']} | "
          f"Methods: {[m['method_name'] for m in blueprint['methods']]}")

    # ── Step 5: Generate 7-layer-compliant Playwright POM files ──────────────
    print("\n[5/10] Generating 7-layer Playwright POM files...")
    generated = CodeGenerator(blueprint, rag_context=rag_context).generate()
    for kind, fpath in generated.items():
        print(f"       {kind:8s}: {fpath}")

    reporter = PipelineReporter(test_case, generated)

    # ── Step 6: AI Validation Gate ────────────────────────────────────────────
    print("\n[6/10] Running AI Validation Gate (11 metrics)...")
    validator  = AIValidator(
        blueprint    = blueprint,
        generated    = generated,
        rag_context  = rag_context,
        stages_done  = 5,
        total_stages = 10,
    )
    validation = validator.validate()
    print(f"       {validation.summary}")

    # ── Step 7: Gate — abort if AI validation fails ───────────────────────────
    if not validation.overall_pass:
        print("\n[7/10] GATE: AI validation failed — generating failure report...")
        report_path = reporter.report(validation, execution=None)
        print(f"\n  Report: {report_path}")
        sys.exit(2)

    print("\n[7/10] GATE: AI validation passed — proceeding to execution")

    # ── Step 8 + 9: Execute (with auto-heal on locator failures) ─────────────
    print("\n[8/10] Executing generated test via pytest...")
    executor = TestExecutor(
        test_path    = generated["test"],
        locator_path = generated["locator"],
        project_root = "automation-project",
    )
    execution = executor.run()

    if execution.healed:
        print("[9/10] Auto-heal applied — test re-executed with patched locators")
    else:
        print("[9/10] No locator heal needed")

    status = "PASS" if execution.passed else "FAIL"
    print(f"       Execution: {status} (attempts={execution.attempts})")

    # ── Step 10: Final report + store in FAISS ────────────────────────────────
    print("\n[10/10] Writing pipeline report...")
    report_path = reporter.report(validation, execution)
    print(f"        Report: {report_path}")

    if execution.passed:
        with open(generated["test"]) as f:
            script_src = f.read()
        store.add(
            test_description=f"{test_case['module']} — {test_case['test_case_id']}",
            script=script_src,
            script_type="ui",
        )
        print(f"        Stored in FAISS. Total scripts: {store.count()}")


def run_all(directory: Path = INPUT_ROOT) -> None:
    from ai.auto_generator.input_parser import InputParser
    files = InputParser.scan_directory(directory)
    if not files:
        print(f"No input files found in {directory}/")
        return
    print(f"Found {len(files)} input file(s) in {directory}/")
    for f in files:
        print(f"  {f.relative_to(directory)}")
    print()
    for f in files:
        try:
            run_pipeline(str(f))
        except Exception as e:
            print(f"\n[ERROR] Failed to process {f.name}: {e}\n")


def list_inputs(directory: Path = INPUT_ROOT) -> None:
    from ai.auto_generator.input_parser import InputParser
    files = InputParser.scan_directory(directory)
    if not files:
        print(f"No input files found under {directory}/")
        return
    print(f"\nDiscovered {len(files)} manual test case(s):\n")
    for f in files:
        rel = f.relative_to(Path("."))
        print(f"  [{f.suffix.upper()[1:]:5}]  {rel}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="AI Agentic Test Automation Pipeline — processes manual test cases"
    )
    parser.add_argument(
        "--input",
        help="Path to a single input file (.json, .csv, .xlsx, .txt). "
             "If omitted, all files under input_manual_test_case/ are processed.",
    )
    parser.add_argument(
        "--list-inputs",
        action="store_true",
        help="List all discovered input files without running the pipeline.",
    )
    args = parser.parse_args()

    if args.list_inputs:
        list_inputs()
    elif args.input:
        if not os.path.exists(args.input):
            print(f"File not found: {args.input}")
            sys.exit(1)
        run_pipeline(args.input)
    else:
        run_all()
