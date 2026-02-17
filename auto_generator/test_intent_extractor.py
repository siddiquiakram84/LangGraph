import json
import os
from auto_generator.intent_extractor import IntentExtractor

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
json_path = os.path.join(BASE_DIR, "test_inputs", "TC_AMAZON_SEARCH_01.json")

with open(json_path) as f:
    test_case = json.load(f)

extractor = IntentExtractor()

print("\n=== Extracted Structured Steps ===\n")

structured_steps = extractor.extract_from_test_case(test_case)

for step in structured_steps:
    print(step)
