"""
main.py  —  Agentic AI Test Automation Pipeline
================================================
Full pipeline:
  JSON test case
      → IntentExtractor  (Claude / Ollama)
      → FAISSScriptStore (RAG context retrieval)
      → PagePlanner
      → CodeGenerator    (Playwright Python POM)
      → FileWriter       (writes to src/ and test/)

Usage:
  python main.py
  python main.py --input ai/auto_generator/test_inputs/TC_AMAZON_SEARCH_01.json
  python main.py --list-inputs
"""
import argparse
import json
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


def run_pipeline(json_path: str) -> None:
    from ai.auto_generator.intent_extractor import IntentExtractor
    from ai.auto_generator.page_planner import PagePlanner
    from ai.auto_generator.code_generator import CodeGenerator
    from ai.auto_heal.memory.faiss_store import FAISSScriptStore

    print(f"\n{'='*60}")
    print("  Agentic AI Auto-Gen Pipeline")
    print(f"  Input: {json_path}")
    print(f"{'='*60}\n")

    # Step 1: Load test case
    with open(json_path) as f:
        test_case = json.load(f)
    print(f"[1/5] Loaded: {test_case['test_case_id']} | {len(test_case['steps'])} steps")

    # Step 2: Extract structured intent via LLM (Claude or Ollama)
    print("\n[2/5] Extracting intent with LLM...")
    extractor = IntentExtractor()
    structured_steps = extractor.extract_from_test_case(test_case)
    for i, step in enumerate(structured_steps, 1):
        print(f"      Step {i}: {step}")

    # Step 3: RAG — retrieve similar scripts from FAISS
    print("\n[3/5] Retrieving RAG context from FAISS...")
    store = FAISSScriptStore()
    query = test_case.get("module", "") + " " + " ".join(
        s.get("tc_msg_action", "") for s in test_case["steps"]
    )
    rag_context = store.search(query, top_k=3)
    if rag_context:
        print(f"      {len(rag_context)} similar scripts found — "
              f"top score={rag_context[0]['similarity_score']:.2f}")
    else:
        print("      No prior scripts — generating from scratch")

    # Step 4: Plan page object structure
    print("\n[4/5] Planning page structure...")
    blueprint = PagePlanner().plan(test_case, structured_steps)
    print(f"      Page: {blueprint['page_name']} | "
          f"Methods: {[m['method_name'] for m in blueprint['methods']]}")

    # Step 5: Generate Playwright Python files
    print("\n[5/5] Generating Playwright Python POM files...")
    written = CodeGenerator(blueprint, rag_context=rag_context).generate()

    print(f"\n{'='*60}  Generation Complete")
    for kind, path in written.items():
        print(f"  {kind:8s}: {path}")

    # Store generated script back to FAISS for future RAG retrieval
    with open(written["test"]) as f:
        generated_script = f.read()
    store.add(
        test_description=f"{test_case['module']} — {test_case['test_case_id']}",
        script=generated_script,
        script_type="ui",
    )
    print(f"\n  Stored in FAISS. Total scripts: {store.count()}\n")


def list_inputs() -> None:
    inputs_dir = Path("ai/auto_generator/test_inputs")
    for f in sorted(inputs_dir.glob("*.json")):
        tc = json.loads(f.read_text())
        print(f"  {f.name}  —  {tc.get('test_case_id')} ({tc.get('module')})")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="ai/auto_generator/test_inputs/TC_AMAZON_SEARCH_01.json")
    parser.add_argument("--list-inputs", action="store_true")
    args = parser.parse_args()

    if args.list_inputs:
        list_inputs()
    elif os.path.exists(args.input):
        run_pipeline(args.input)
    else:
        print(f"File not found: {args.input}")
        sys.exit(1)
