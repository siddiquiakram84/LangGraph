import json
import os
from ai.auto_generator.intent_extractor import IntentExtractor
from ai.auto_generator.page_planner import PagePlanner

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
json_path = os.path.join(BASE_DIR, "test_inputs", "TC_AMAZON_SEARCH_01.json")

with open(json_path) as f:
    test_case = json.load(f)

extractor = IntentExtractor()
structured_steps = extractor.extract_from_test_case(test_case)

planner = PagePlanner()
blueprint = planner.plan(test_case, structured_steps)

print("\n=== PAGE BLUEPRINT ===\n")
print(blueprint)
