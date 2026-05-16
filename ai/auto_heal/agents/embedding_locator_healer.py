from bs4 import BeautifulSoup
from langsmith import traceable
from ai.auto_heal.embedding.embedding_engine import EmbeddingEngine

engine = EmbeddingEngine()

CONFIDENCE_THRESHOLD = 0.7


@traceable(name="embedding-locator-healer")
def embedding_locator_healer(state):

    dom = state["dom_snapshot"]

    failed_locator = state["failed_locator"]

    soup = BeautifulSoup(dom, "html.parser")

    failed_vec = engine.embed(failed_locator[1])

    best_score = 0
    best_locator = None
    candidates = []

    for element in soup.find_all(True):

        for attr in ("id", "name", "placeholder", "aria-label"):

            val = element.get(attr)

            if not val:
                continue

            candidates.append((attr, val))

            vec = engine.embed(val)

            score = engine.similarity(failed_vec, vec)

            if score > best_score:

                best_score = score
                best_locator = (attr, val)

    if best_locator and best_score >= CONFIDENCE_THRESHOLD:

        return {

            "candidate_locators": candidates,

            "healed_locator": best_locator,

            "confidence_score": best_score,

            "success": True
        }

    return {

        "candidate_locators": candidates,

        "healed_locator": None,

        "confidence_score": best_score,

        "success": False
    }
