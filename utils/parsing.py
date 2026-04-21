# utils/parsing.py

from selenium.webdriver.common.by import By
import utils.table_extract as tb


# -------------------------
# Extract Tax Data
# -------------------------

def extract_tax_data(driver):
    """
    Extracts tax and assessment data from the results page.

    Returns:
        dict: extracted data
    """

    tax_data = {}

    try:
        # -------------------------
        # Current year tables
        # -------------------------
        year1_assessment_table = driver.find_element(By.ID, "year1-assessment")
        year1_tax_table = driver.find_element(By.ID, "year1-tax-info")

        year1_year = tb.extract_table_year(year1_tax_table)

        full_address, roll_number = tb.extract_address_informatin(driver)

        current_assessment_data = tb.extract_table_data(year1_assessment_table)
        current_tax_data = tb.extract_table_data(year1_tax_table)

        # Address metadata
        tax_data["EXTRACTED_ASSESSMENT_ROLL_NUMBER"] = roll_number
        tax_data["EXTRACTED_ADDRESS_SUMMARY"] = full_address

        # Current year data
        tax_data.update({f"{year1_year} - {k}": v for k, v in current_assessment_data.items()})
        tax_data.update({f"{year1_year} - {k}": v for k, v in current_tax_data.items()})

    except Exception as e:
        print(f"Error extracting current year data: {e}")
        return {}

    # -------------------------
    # Previous year (optional)
    # -------------------------
    try:
        year2_assessment_table = driver.find_element(By.ID, "year2-assessment")
        year2_tax_table = driver.find_element(By.ID, "year2-tax-info")

        year2_year = tb.extract_table_year(year2_tax_table)

        previous_assessment_data = tb.extract_table_data(year2_assessment_table)
        previous_tax_data = tb.extract_table_data(year2_tax_table)

        tax_data.update({f"{year2_year} - {k}": v for k, v in previous_assessment_data.items()})
        tax_data.update({f"{year2_year} - {k}": v for k, v in previous_tax_data.items()})

    except Exception:
        # No previous year available → normal case
        pass

    # -------------------------
    # Error message (if present)
    # -------------------------
    try:
        error_elements = driver.find_elements(By.ID, "assessment-search-result-message")

        if error_elements:
            error_message = error_elements[0].text.strip()
            if error_message:
                tax_data["Error Message"] = error_message

    except Exception:
        pass

    return tax_data


# -------------------------
# Normalize Road Name
# -------------------------

def normalize_road_name(road_name):
    """
    Removes trailing period from directional abbreviations (N., S., E., W.)

    Args:
        road_name (str)

    Returns:
        str
    """
    if road_name and isinstance(road_name, str):
        road_name = road_name.strip()

        if road_name.endswith(('N.', 'S.', 'E.', 'W.')):
            road_name = road_name[:-1]

    return road_name