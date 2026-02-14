from memory.vector_store import VectorStore
from memory.locator_store import LocatorStore
from updater.source_updater import SourceUpdater



vector_store = VectorStore()
locator_store = LocatorStore()
source_updater = SourceUpdater()


def memory_updater(state):

    if not state.get("success"):
        return state

    vector_store.add(

        state["failed_locator"],

        state["healed_locator"],

        state["dom_snapshot"]
    )

    locator_store.save(

        state["failed_locator"],

        state["healed_locator"]
    )

    source_updater.update(

        state["test_file"],

        state["failed_locator"],

        state["healed_locator"]
    )

    return state
