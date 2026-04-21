# utils/grouping.py

import pandas as pd


def group_addresses_by_parcel(data):
    """
    Groups address records by PARCEL_ASSESSMENT_ROLL_NUMBER.

    Accepts either:
        - list of dicts
        - pandas DataFrame

    Returns:
        dict:
            {
                roll_number: [list of address dicts],
                ...
            }

    Notes:
        - Preserves None/NaN roll numbers as a valid group
        - Ensures consistent string formatting where possible
    """

    # -------------------------
    # Normalize input
    # -------------------------
    if isinstance(data, list):
        df = pd.DataFrame(data)
    elif isinstance(data, pd.DataFrame):
        df = data.copy()
    else:
        raise ValueError(
            "Input must be a list of dictionaries or a pandas DataFrame."
        )

    # -------------------------
    # Ensure column exists
    # -------------------------
    if "PARCEL_ASSESSMENT_ROLL_NUMBER" not in df.columns:
        raise ValueError(
            "Missing required column: PARCEL_ASSESSMENT_ROLL_NUMBER"
        )

    # -------------------------
    # Normalize roll numbers
    # -------------------------
    df["PARCEL_ASSESSMENT_ROLL_NUMBER"] = (
        df["PARCEL_ASSESSMENT_ROLL_NUMBER"]
        .astype(str)
        .replace("nan", None)
    )

    # -------------------------
    # Group data
    # -------------------------
    grouped = (
        df.groupby("PARCEL_ASSESSMENT_ROLL_NUMBER", dropna=False)
        .apply(lambda x: x.to_dict(orient="records"))
    )

    grouped_dict = grouped.to_dict()

    print(f"Number of parcels: {len(grouped_dict)}")

    return grouped_dict