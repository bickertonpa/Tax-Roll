# config.py
from dataclasses import dataclass
from pathlib import Path

@dataclass
class Config:
    base_dir: Path
    addresses_path: Path
    processed_addresses_path: Path

    output_path: Path | None = None
    checkpoint_path: Path | None = None
    log_path: Path | None = None

    batch_size: int = 50

    @classmethod
    def from_ward(cls, ward: str):
        base = Path(".")
        safe_ward = ward.replace(" ", "_")

        return cls(
            base_dir=base,
            addresses_path=base / f"Addresses/Raw/Addresses_{ward}.csv",
            processed_addresses_path=base / f"Addresses/Processed/Addresses_{ward}.csv",
        )