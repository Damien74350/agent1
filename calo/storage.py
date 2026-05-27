"""Encrypted file storage for sensitive media (meal + body photos)."""

import secrets
from datetime import datetime, timezone
from pathlib import Path

from cryptography.fernet import Fernet


class PhotoStore:
    """Fernet-encrypted blob storage. Files on disk are unreadable without the key."""

    def __init__(self, root: Path, encryption_key: str):
        if not encryption_key:
            raise RuntimeError("PhotoStore requires CALO_PHOTO_ENCRYPTION_KEY.")
        self.root = root
        self.root.mkdir(parents=True, exist_ok=True)
        self._fernet = Fernet(encryption_key.encode())

    def save(self, data: bytes, *, kind: str, user_id: int, ext: str = "jpg") -> str:
        """Encrypt and persist a binary blob. Returns a relative path that can be
        stored in the DB and passed back to `load` later."""
        if kind not in ("meal", "body"):
            raise ValueError(f"unknown photo kind: {kind}")
        ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        token = secrets.token_hex(4)
        rel = f"{kind}/user_{user_id}/{ts}_{token}.{ext}.enc"
        target = self.root / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(self._fernet.encrypt(data))
        return rel

    def load(self, relative_path: str) -> bytes:
        path = self.root / relative_path
        return self._fernet.decrypt(path.read_bytes())

    def delete(self, relative_path: str) -> None:
        path = self.root / relative_path
        if path.exists():
            path.unlink()
