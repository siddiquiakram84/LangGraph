from sentence_transformers import SentenceTransformer
import numpy as np


class EmbeddingEngine:

    def __init__(self):

        self.model = SentenceTransformer("all-MiniLM-L6-v2")

    def embed(self, text):

        return self.model.encode(text)

    def similarity(self, v1, v2):

        return float(
            np.dot(v1, v2)
            /
            (np.linalg.norm(v1) * np.linalg.norm(v2))
        )
