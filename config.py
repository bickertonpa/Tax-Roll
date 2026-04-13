# config.py
from dataclasses import dataclass
from pathlib import Path

@dataclass
class Config:
    base_dir: Path
    addresses_path: Path
    processed_addresses_path: Path
    output_path: Path
    checkpoint_path: Path
    batch_size: int = 50

    @classmethod
    def from_ward(cls, ward: str):
        base = Path(".")

        safe_ward = ward.replace(" ", "_")

        return cls(
            base_dir=base,
            addresses_path=base / f"Addresses/Raw/Addresses_{ward}.csv",
            processed_addresses_path=base / f"Addresses/Processed/Addresses_{ward}.csv",
            output_path=base / f"Output/json/{safe_ward}.json",
            checkpoint_path=base / f"Checkpoint/{safe_ward}_to_be_checked.csv",
        )
