# data_loader.py

import os
import pandas as pd
from typing import List, Dict, Any

from utils.preprocessing import preprocess_address_file  # move your function here


def load_addresses(config) -> List[Dict[str, Any]]:
    """
    Load addresses from checkpoint if it exists, otherwise from raw CSV.

    Returns:
        List[dict]: to_be_checked
    """

    # -------------------------
    # 1. Load from checkpoint
    # -------------------------
    if os.path.exists(config.checkpoint_path):
        to_be_checked = pd.read_csv(
            config.checkpoint_path,
            dtype={"PARCEL_ASSESSMENT_ROLL_NUMBER": str}
        ).to_dict(orient="records")

        print(f"Loaded checkpoint with {len(to_be_checked)} addresses to process.")
        return to_be_checked

    # -------------------------
    # 2. Load from raw file
    # -------------------------
    if os.path.exists(config.addresses_path):

        print("No checkpoint found. Preprocessing raw address file...")

        preprocess_address_file(
            config.addresses_path,
            config.processed_addresses_path
        )

        addresses_df = pd.read_csv(
            config.processed_addresses_path,
            dtype={"PARCEL_ASSESSMENT_ROLL_NUMBER": str}
        )

        print(f"Loaded {len(addresses_df)} addresses from processed file.")
        print("Starting fresh run.")

        return addresses_df.to_dict(orient='records')

    # -------------------------
    # 3. Fail early if missing
    # -------------------------
    raise FileNotFoundError(
        f"No addresses file found at {config.addresses_path}"
    )