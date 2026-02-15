from datetime import datetime, timezone
from pathlib import Path
import json


class AuditLogger:
    def __init__(self, audit_file: str = "app/data/audit.log") -> None:
        self.audit_path = Path(audit_file)
        self.audit_path.parent.mkdir(parents=True, exist_ok=True)

    def log(self, user_id: str, action: str, details: dict) -> None:
        event = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "user_id": user_id,
            "action": action,
            "details": details,
        }
        with self.audit_path.open("a", encoding="utf-8") as fp:
            fp.write(json.dumps(event) + "\n")


audit_logger = AuditLogger()
