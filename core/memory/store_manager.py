import json
import os
import time
from pathlib import Path
from typing import Dict, Any, Optional
import contextlib
from .memory_manager import file_lock

class DomainStore:
    """
    Generic store for domain data with file locking.
    """
    def __init__(self, filename: str):
        self.path = Path(__file__).parent / filename
        if not self.path.exists():
            self._save({})

    def _load(self) -> Dict[str, Any]:
        if not self.path.exists():
            return {}
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return {}

    def _save(self, data: Dict[str, Any]) -> None:
        with open(self.path, "a+", encoding="utf-8") as f:
            with file_lock(f):
                f.seek(0)
                f.truncate()
                json.dump(data, f, indent=2, ensure_ascii=False)
                f.flush()
                os.fsync(f.fileno())

    def get_all(self) -> Dict[str, Any]:
        return self._load()

    def get_by_id(self, item_id: str) -> Optional[Dict[str, Any]]:
        data = self._load()
        return data.get(item_id)

    def save_item(self, item_id: str, item_data: Dict[str, Any]) -> None:
        data = self._load()
        data[item_id] = item_data
        self._save(data)

    def search(self, criteria: Dict[str, Any]) -> list:
        data = self._load()
        results = []
        for item in data.values():
            match = True
            for key, value in criteria.items():
                if item.get(key) != value:
                    match = False
                    break
            if match:
                results.append(item)
        return results
