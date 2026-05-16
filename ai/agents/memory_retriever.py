from langsmith import traceable
from ai.memory.vector_store import VectorStore


store = VectorStore()


@traceable(name="memory-retriever")
def memory_retriever(state):

    dom = state["dom_snapshot"]

    results = store.search(dom)

    return {

        "memory_results": results
    }
