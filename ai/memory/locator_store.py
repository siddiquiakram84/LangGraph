"""
memory/locator_store.py

Persistent JSON-based locator memory store.

Stores healed locators for reuse and learning.
"""

import json
import os
from typing import List, Dict


class LocatorStore:

    def __init__(self, file_path: str = "healing_memory/locator_memory.json"):

        self.file_path = file_path

        os.makedirs("healing_memory", exist_ok=True)

        if not os.path.exists(self.file_path):

            with open(self.file_path, "w") as f:

                json.dump([], f)

    def save(
        self,
        failed_locator: tuple,
        healed_locator: tuple
    ) -> None:

        data = self._load()

        record = {

            "failed_locator": list(failed_locator),

            "healed_locator": list(healed_locator)
        }

        data.append(record)

        self._write(data)

    def get_all(self) -> List[Dict]:

        return self._load()

    def _load(self) -> List[Dict]:

        with open(self.file_path, "r") as f:

            return json.load(f)

    def _write(self, data: List[Dict]) -> None:

        with open(self.file_path, "w") as f:

            json.dump(data, f, indent=4)
