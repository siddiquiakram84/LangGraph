from auto_generator.page_planner import PagePlanner
from auto_generator.code_generator import CodeGenerator

structured_steps = [
    {"action_type": "enter_text", "field_name": "search_box", "value": "iphone 15"},
    {"action_type": "click", "field_name": "search button"},
    {"action_type": "click", "field_name": "first_product"},
    {"action_type": "click", "field_name": "add to cart button"},
]

planner = PagePlanner()

# Since your planner method is `plan`
blueprint = planner.plan(
    {"module": "amazon_search"},
    structured_steps
)

print("\n=== BLUEPRINT ===\n")
print(blueprint)

generator = CodeGenerator(blueprint)
generator.generate()

print("\nCode generation completed.")
