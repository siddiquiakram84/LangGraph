import os
from dotenv import load_dotenv
from langsmith import traceable
from ai.core.langgraph_builder import build_healing_graph

load_dotenv()


class HealingEngine:

    def __init__(self):
        self.graph = build_healing_graph()
        self.project = os.getenv("LANGCHAIN_PROJECT", "langgraph-healing-engine")

    @traceable(name="healing-engine-run")
    def heal(self, **kwargs):
        state = dict(kwargs)
        state["success"] = False
        final_state = self.graph.invoke(
            state,
            config={"run_name": "heal", "tags": ["healing", "langgraph"]},
        )
        return final_state["report"]
