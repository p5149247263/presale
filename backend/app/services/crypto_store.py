from __future__ import annotations

from pathlib import Path
import base64

try:
    from cryptography.fernet import Fernet, InvalidToken
except Exception:
    Fernet = None  # type: ignore[assignment]
    InvalidToken = Exception  # type: ignore[assignment]


class EncryptedFileStore:
    def __init__(self, key: str | None, base_path: str = "app/data/storage/docs") -> None:
        self.base = Path(base_path)
        self.base.mkdir(parents=True, exist_ok=True)
        if Fernet is None:
            self.fernet = None
            self._fallback_key = (key or "local-dev-key").encode("utf-8")
            return

        if key:
            raw = key.encode("utf-8")
        else:
            raw = Fernet.generate_key()
        self.fernet = Fernet(raw)

    def save(self, file_name: str, data: bytes) -> str:
        path = self.base / f"{file_name}.enc"
        if self.fernet is None:
            path.write_bytes(base64.b64encode(data))
            return str(path)
        path.write_bytes(self.fernet.encrypt(data))
        return str(path)

    def load(self, file_name: str) -> bytes:
        path = self.base / f"{file_name}.enc"
        encrypted = path.read_bytes()
        if self.fernet is None:
            return base64.b64decode(encrypted)
        try:
            return self.fernet.decrypt(encrypted)
        except InvalidToken as exc:
            raise ValueError("Unable to decrypt file") from exc
