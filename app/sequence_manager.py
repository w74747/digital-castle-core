import json
import os
from datetime import datetime

SEQUENCE_FILE = "data/sequences.json"


class SequenceManager:

    def __init__(self, storage_path: str = SEQUENCE_FILE):
        self.storage_path = storage_path
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
        if not os.path.exists(self.storage_path):
            self._save_state({"INV": 0, "PROP": 0})

    def _load_state(self) -> dict:
        try:
            with open(self.storage_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {"INV": 0, "PROP": 0}

    def _save_state(self, data: dict):
        with open(self.storage_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def generate_next_number(self, doc_type: str = "INV") -> str:
        """توليد رقم تسلسلي غير مكرر مثل: INV-2026-0001"""
        state = self._load_state()
        current_seq = state.get(doc_type, 0) + 1
        state[doc_type] = current_seq
        self._save_state(state)

        current_year = datetime.now().year
        # تنسيق الرقم ليكون من 4 خانات: 0001, 0002...
        return f"{doc_type}-{current_year}-{current_seq:04d}"
