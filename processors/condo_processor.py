# processors/condo_processor.py

import pandas as pd
from selenium.webdriver.common.by import By
from utils.logger import log_result

from utils.selenium_utils import wait_and_click, wait_and_send_keys, wait_for_results
from utils.parsing import extract_tax_data, normalize_road_name


class CondoProcessor:
    def __init__(self, driver, batch_manager):
        """
        Args:
            driver: Selenium WebDriver
            batch_manager: BatchManager instance
        """
        self.driver = driver
        self.batch_manager = batch_manager

        self.base_url = "https://propertytaxes-taxesfoncieres.ottawa.ca/en?t=taxassessmentlookup"

    # -------------------------
    # Public API
    # -------------------------

    def process(self, address: dict, parcel_roll_number: str = None):
        """
        Discover and process condo units for a given base address.

        Returns:
            List[dict]: all valid condo unit records
        """

        street_number = str(address.get("ADDRNUM", ""))
        street_name = normalize_road_name(address.get("FULL_ROADN"))
        qualifier = self._safe_str(address.get("QUALIFIER"))

        condo_results = []  

        empty_floor_count = 0
        floor = 1  # represents 100-level

        # -------------------------
        # Floor loop
        # -------------------------
        while empty_floor_count < 2:

            print(f"Checking floor {floor}")

            base_unit = floor * 100
            unit_offset = 0

            consecutive_failures = 0
            floor_had_valid_unit = False

            # -------------------------
            # Unit loop
            # -------------------------
            while consecutive_failures < 2:

                unit_number = base_unit + unit_offset
                unit_str = str(unit_number)

                try:
                    self._load_search_page()
                    self._fill_form(street_number, street_name, unit_str, qualifier)
                    self._submit()

                    if not wait_for_results(self.driver):
                        consecutive_failures += 1
                        unit_offset += 1
                        continue

                    # -------------------------
                    # Check for error
                    # -------------------------
                    error_elements = self.driver.find_elements(By.ID, "assessment-search-result-message")

                    if error_elements:
                        error_message = error_elements[0].text.strip()

                        if error_message:
                            consecutive_failures += 1
                            unit_offset += 1
                            log_result(
                                level="ERR",
                                method="condo",
                                message=error_message,
                                Unit= unit_str,
                                Addr=address.get("FULL_ADDRE")
                            )
                            continue

                    # -------------------------
                    # Valid unit found
                    # -------------------------
                    data = {
                        "street_number": street_number,
                        "street_name": street_name,
                        "unit": unit_str,
                        "qualifier": qualifier,
                        "PARCEL_ASSESSMENT_ROLL_NUMBER": parcel_roll_number,
                        "LOOKUP_METHOD": "CONDO"
                    }

                    log_result(
                        level="OK",
                        method="condo",
                        Unit=data.get("unit"),
                        Addr=address.get("FULL_ADDRE")
                    )


                    data.update(extract_tax_data(self.driver))
                    

                    condo_results.append(data)
                    self.batch_manager.add(data)

                    #print(f"Valid condo unit found: {unit_str}")

                    floor_had_valid_unit = True
                    consecutive_failures = 0
                    unit_offset += 1

                except Exception as e:
                    print(f"Error checking unit {unit_str}: {e}")
                    consecutive_failures += 1
                    unit_offset += 1

            # -------------------------
            # Floor completion logic
            # -------------------------
            if not floor_had_valid_unit:
                empty_floor_count += 1
                print(f"Empty floor detected: {floor}")
            else:
                empty_floor_count = 0

            floor += 1

        print(f"** Finished condo processing for {address.get('FULL_ADDRE')}**")

        return condo_results

    # -------------------------
    # Internal helpers
    # -------------------------

    def _load_search_page(self):
        self.driver.get(self.base_url)

        wait_and_click(self.driver, '//*[@id="taxWidgetOption-taxassessmentlookup"]')
        wait_and_click(self.driver, '//*[@id="taxAssessmentSearchOption-address"]')

    def _fill_form(self, street_number, street_name, unit, qualifier):
        wait_and_send_keys(self.driver, '//*[@id="propertyStreetNumber"]', street_number)
        wait_and_send_keys(self.driver, '//*[@id="propertyStreetName"]', street_name)
        wait_and_send_keys(self.driver, '//*[@id="propertyUnit"]', unit)

        if qualifier:
            wait_and_send_keys(self.driver, '//*[@id="propertyQualifier"]', qualifier)

    def _submit(self):
        wait_and_click(self.driver, '//*[@id="assessmentTermOfService"]')
        wait_and_click(self.driver, '//*[@id="submit-button"]')

    def _safe_str(self, value):
        return str(value) if pd.notna(value) else ""