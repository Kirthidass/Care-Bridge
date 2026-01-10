import json
import os
from typing import List, Optional, Dict
from datetime import datetime
from app.core.config import settings

# A simple file-based database to avoid external dependencies like Postgres/Mongo for this demo.
# It saves all report metadata into a single 'db.json' file in the data folder.

DB_PATH = os.path.join("data", "db.json")

class JsonDatabase:
    def __init__(self):
        self.db_path = DB_PATH
        if not os.path.exists(self.db_path):
            self._save_db([])

    def _load_db(self) -> List[Dict]:
        try:
            with open(self.db_path, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return []

    def _save_db(self, data: List[Dict]):
        with open(self.db_path, "w") as f:
            json.dump(data, f, indent=2)

    def save_report(self, report_id: str, filename: str, report_type: str, parsed_data: dict):
        db = self._load_db()
        record = {
            "id": report_id,
            "filename": filename,
            "upload_date": datetime.now().isoformat(),
            "type": report_type, # 'lab' or 'radiology'
            "parsed_data": parsed_data
        }
        db.append(record)
        self._save_db(db)
        return record

    def get_report(self, report_id: str) -> Optional[Dict]:
        db = self._load_db()
        for record in db:
            if record["id"] == report_id:
                return record
        return None

    def list_reports(self) -> List[Dict]:
        return self._load_db()

# Singleton instance
db = JsonDatabase()
