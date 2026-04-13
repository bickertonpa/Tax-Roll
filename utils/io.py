# utils/io.py

import json
import os
import pandas as pd


def save_to_json(data, output_path, to_be_checked, checkpoint_path):
    """
    Save batch data to JSON and update checkpoint file.

    Args:
        data (list[dict])
        output_path (Path or str)
        to_be_checked (list[dict])
        checkpoint_path (Path or str)
    """

    # -------------------------
    # Normalize roll numbers
    # -------------------------
    processed_roll_numbers = {
        str(d.get("PARCEL_ASSESSMENT_ROLL_NUMBER")).zfill(15)
        for d in data
        if d.get("PARCEL_ASSESSMENT_ROLL_NUMBER")
    }

    # -------------------------
    # Remove processed entries
    # -------------------------
    to_be_checked[:] = [
        addr for addr in to_be_checked
        if str(addr.get("PARCEL_ASSESSMENT_ROLL_NUMBER")).zfill(15)
        not in processed_roll_numbers
    ]

    # -------------------------
    # Load existing JSON
    # -------------------------
    if os.path.exists(output_path):
        try:
            with open(output_path, "r", encoding="utf-8") as f:
                existing_data = json.load(f)
        except json.JSONDecodeError:
            existing_data = []
    else:
        existing_data = []

    # -------------------------
    # Append and save
    # -------------------------
    existing_data.extend(data)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(existing_data, f, indent=4, ensure_ascii=False)

    print(f"Saved {len(data)} records to {output_path}")

    # -------------------------
    # Save checkpoint
    # -------------------------
    pd.DataFrame(to_be_checked).to_csv(checkpoint_path, index=False)

    print(f"Checkpoint updated: {len(to_be_checked)} remaining")