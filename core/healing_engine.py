from core.langgraph_builder import build_healing_graph


class HealingEngine:

    def __init__(self):

        self.graph = build_healing_graph()

    def heal(self, **kwargs):

        state = dict(kwargs)

        state["success"] = False

        final_state = self.graph.invoke(state)

        return final_state["report"]
