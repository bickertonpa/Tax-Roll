# utils/preprocessing.py

import csv
import pandas as pd
from decimal import Decimal


def convert_scientific_to_full_form_with_leading_zero(sci_str):
    if sci_str == '' or pd.isnull(sci_str):
        sci_str = '614000000000000000'

    decimal_value = Decimal(sci_str)
    full_form = '0' + format(decimal_value, 'f')
    full_form = full_form.rstrip('0').rstrip('.') if '.' in full_form else full_form
    return full_form


def preprocess_address_file(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as infile, \
         open(output_file, 'w', encoding='utf-8', newline='') as outfile:

        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames

        if 'PARCEL_ASSESSMENT_ROLL_NUMBER' not in fieldnames:
            raise ValueError("Missing PARCEL_ASSESSMENT_ROLL_NUMBER")

        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()

        for row in reader:
            row['PARCEL_ASSESSMENT_ROLL_NUMBER'] = (
                convert_scientific_to_full_form_with_leading_zero(
                    row['PARCEL_ASSESSMENT_ROLL_NUMBER']
                )
            )
            writer.writerow(row)

    print(f"Processed file saved to {output_file}")