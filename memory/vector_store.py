"""
memory/vector_store.py

ChromaDB persistent vector memory store.
Compatible with ChromaDB >= 1.0
"""

import chromadb


class VectorStore:

    def __init__(self):

        self.client = chromadb.Client(

            settings=chromadb.config.Settings(

                persist_directory="./healing_memory"
            )
        )

        self.collection = self.client.get_or_create_collection(

            name="locator_memory"
        )

    def add(self, failed_locator, healed_locator, dom_snapshot):

        """
        Store healing event in vector memory.
        """

        self.collection.add(

            documents=[dom_snapshot],

            metadatas=[{

                "failed_locator": str(failed_locator),

                "healed_locator": str(healed_locator)

            }],

            ids=[str(hash(dom_snapshot))]
        )

        # DO NOT call persist()
        # ChromaDB v1.x persists automatically

    def search(self, dom_snapshot):

        return self.collection.query(

            query_texts=[dom_snapshot],

            n_results=3
        )
