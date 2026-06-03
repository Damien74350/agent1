import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


@dataclass
class CaloConfig:
    anthropic_api_key: str = field(
        default_factory=lambda: os.environ.get("ANTHROPIC_API_KEY", "")
    )
    model: str = field(default_factory=lambda: os.environ.get("CALO_MODEL", "claude-sonnet-4-6"))
    effort: str = field(default_factory=lambda: os.environ.get("CALO_EFFORT", "medium"))
    max_tokens: int = field(default_factory=lambda: int(os.environ.get("CALO_MAX_TOKENS", "8000")))

    data_dir: Path = field(
        default_factory=lambda: Path(os.environ.get("CALO_DATA_DIR", "./data")).resolve()
    )
    photos_dir: Path = field(
        default_factory=lambda: Path(os.environ.get("CALO_PHOTOS_DIR", "./photos")).resolve()
    )
    photo_encryption_key: str = field(
        default_factory=lambda: os.environ.get("CALO_PHOTO_ENCRYPTION_KEY", "")
    )

    twilio_account_sid: str = field(
        default_factory=lambda: os.environ.get("TWILIO_ACCOUNT_SID", "")
    )
    twilio_auth_token: str = field(
        default_factory=lambda: os.environ.get("TWILIO_AUTH_TOKEN", "")
    )
    twilio_whatsapp_from: str = field(
        default_factory=lambda: os.environ.get("TWILIO_WHATSAPP_FROM", "")
    )
    twilio_sms_from: str = field(
        default_factory=lambda: os.environ.get("CALO_TWILIO_SMS_FROM", "")
    )

    public_url: str = field(default_factory=lambda: os.environ.get("CALO_PUBLIC_URL", ""))
    admin_number: str = field(default_factory=lambda: os.environ.get("CALO_ADMIN_NUMBER", ""))

    airtable_pat: str = field(default_factory=lambda: os.environ.get("AIRTABLE_PAT", ""))

    # Voice features (optional). If absent → text-only mode, no degradation.
    openai_api_key: str = field(
        default_factory=lambda: os.environ.get("OPENAI_API_KEY", "")
    )
    elevenlabs_api_key: str = field(
        default_factory=lambda: os.environ.get("ELEVENLABS_API_KEY", "")
    )
    elevenlabs_voice_id: str = field(
        default_factory=lambda: os.environ.get(
            "ELEVENLABS_VOICE_ID", "EXAVITQu4vr4xnSDxMaL"  # "Charlotte" default
        )
    )

    def __post_init__(self) -> None:
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.photos_dir.mkdir(parents=True, exist_ok=True)

    @property
    def db_path(self) -> Path:
        return self.data_dir / "calo.db"

    def require_anthropic(self) -> None:
        if not self.anthropic_api_key:
            raise RuntimeError("ANTHROPIC_API_KEY missing.")

    def require_twilio(self) -> None:
        missing = [
            name
            for name, val in [
                ("TWILIO_ACCOUNT_SID", self.twilio_account_sid),
                ("TWILIO_AUTH_TOKEN", self.twilio_auth_token),
                ("TWILIO_WHATSAPP_FROM", self.twilio_whatsapp_from),
            ]
            if not val
        ]
        if missing:
            raise RuntimeError(f"Missing Twilio env vars: {', '.join(missing)}")

    def require_airtable(self) -> None:
        if not self.airtable_pat:
            raise RuntimeError(
                "AIRTABLE_PAT missing. Create a personal access token at "
                "https://airtable.com/create/tokens with scopes "
                "data.records:read, data.records:write, schema.bases:read."
            )

    def require_encryption_key(self) -> None:
        if not self.photo_encryption_key:
            raise RuntimeError(
                "CALO_PHOTO_ENCRYPTION_KEY missing. Generate one with:\n"
                '  python -c "from cryptography.fernet import Fernet; '
                'print(Fernet.generate_key().decode())"'
            )
