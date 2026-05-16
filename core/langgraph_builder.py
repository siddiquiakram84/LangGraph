from langgraph.graph import StateGraph, END

from core.state import HealingState

from agents.failure_analyzer import failure_analyzer
from agents.dom_capture import dom_capture
from agents.memory_retriever import memory_retriever
from agents.embedding_locator_healer import embedding_locator_healer
from agents.validator import validator
from agents.memory_updater import memory_updater
from agents.logic_healer import logic_healer
from agents.report_generator import report_generator


def build_healing_graph():

    graph = StateGraph(HealingState)

    graph.add_node("failure_analyzer", failure_analyzer)
    graph.add_node("dom_capture", dom_capture)
    graph.add_node("memory_retriever", memory_retriever)
    graph.add_node("embedding_locator_healer", embedding_locator_healer)
    graph.add_node("validator", validator)
    graph.add_node("memory_updater", memory_updater)
    graph.add_node("logic_healer", logic_healer)
    graph.add_node("report_generator", report_generator)

    graph.set_entry_point("failure_analyzer")

    graph.add_edge("failure_analyzer", "dom_capture")
    graph.add_edge("dom_capture", "memory_retriever")
    graph.add_edge("memory_retriever", "embedding_locator_healer")
    graph.add_edge("embedding_locator_healer", "validator")

    def route_after_validation(state):
        if state.get("validation_success"):
            return "memory_updater"
        return "report_generator"

    graph.add_conditional_edges(
        "validator",
        route_after_validation,
        {
            "memory_updater": "memory_updater",
            "report_generator": "report_generator",
        },
    )

    graph.add_edge("memory_updater", "logic_healer")
    graph.add_edge("logic_healer", "report_generator")

    graph.add_edge("report_generator", END)

    return graph.compile()
