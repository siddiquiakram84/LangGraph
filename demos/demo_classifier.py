print("Script is running...")

import json
import os
from ai.auto_generator.action_classifier import ActionClassifier

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
json_path = os.path.join(BASE_DIR, "test_inputs", "TC_AMAZON_SEARCH_01.json")

with open(json_path) as f:
    data = json.load(f)

classifier = ActionClassifier()

print("\n=== Classified Actions ===\n")

for step in data["steps"]:
    structured = classifier.classify(step)
    print(structured)
