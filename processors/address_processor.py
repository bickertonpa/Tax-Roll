# processors/address_processor.py

import pandas as pd
from selenium.webdriver.common.by import By

from utils.logger import log_result
from utils.selenium_utils import wait_and_click, wait_and_send_keys, wait_for_results
from utils.parsing import extract_tax_data, normalize_road_name


class AddressProcessor:
    def __init__(self, driver, batch_manager, condo_processor=None):
        """
        Args:
            driver: Selenium WebDriver
            batch_manager: BatchManager instance
            condo_processor: CondoProcessor (optional, for fallback)
        """
        self.driver = driver
        self.batch_manager = batch_manager
        self.condo_processor = condo_processor

        self.base_url = "https://propertytaxes-taxesfoncieres.ottawa.ca/en?t=taxassessmentlookup"

    # -------------------------
    # Public API
    # -------------------------

    def process(self, address: dict, parcel_roll_number: str = None):
        """
        Process a single address.

        Returns:
            dict or None
        """

        street_number = str(address.get("ADDRNUM", ""))
        street_name = normalize_road_name(address.get("FULL_ROADN"))
        unit = self._safe_unit(address.get("UNIT"))
        qualifier = self._safe_str(address.get("QUALIFIER"))

        try:
            self._load_search_page()
            self._fill_address_form(street_number, street_name, unit, qualifier)
            self._submit()

            if not wait_for_results(self.driver):
                print(f"Timeout waiting for results: {address.get('FULL_ADDRE')}")
                return None

            # -------------------------
            # Check for error message
            # -------------------------
            error_elements = self.driver.find_elements(By.ID, "assessment-search-result-message")

            if error_elements:
                error_message = error_elements[0].text.strip()
                log_result(
                    level="ERR",
                    method="address",
                    message=error_message,
                    Addr=address.get('FULL_ADDRE')
                    )

                # Condo detection (same logic as your original script)
                if "multiple properties" in error_message.lower():
                    print(f"**Condo detected: {address.get('FULL_ADDRE')}**")

                    if self.condo_processor:
                        condo_results = self.condo_processor.process(
                            address,
                            parcel_roll_number
                        )

                    return None

                return {
                    "street_number": street_number,
                    "street_name": street_name,
                    "unit": unit,
                    "qualifier": qualifier,
                    "PARCEL_ASSESSMENT_ROLL_NUMBER": parcel_roll_number,
                    "error message": error_message,
                    "LOOKUP_METHOD": "ADDRESS"
                }

            # -------------------------
            # Valid result
            # -------------------------
            data = {
                "street_number": street_number,
                "street_name": street_name,
                "unit": unit,
                "qualifier": qualifier,
                "PARCEL_ASSESSMENT_ROLL_NUMBER": parcel_roll_number,
                "LOOKUP_METHOD": "ADDRESS"
            }
            log_result(
                level="OK",
                method="address",
                Addr=address.get("FULL_ADDRE")
            )

            data.update(extract_tax_data(self.driver))

            return data

        except Exception as e:
            #print(f"Error processing address {address.get('FULL_ADDRE')}: {e}")
            log_result(
                level="ERR",
                method="address",
                message=str(e),
                Addr=address.get('FULL_ADDRE')
                )
            return None

    # -------------------------
    # Internal helpers
    # -------------------------

    def _load_search_page(self):
        self.driver.get(self.base_url)

        wait_and_click(self.driver, '//*[@id="taxWidgetOption-taxassessmentlookup"]')
        wait_and_click(self.driver, '//*[@id="taxAssessmentSearchOption-address"]')

    def _fill_address_form(self, street_number, street_name, unit, qualifier):
        wait_and_send_keys(self.driver, '//*[@id="propertyStreetNumber"]', street_number)
        wait_and_send_keys(self.driver, '//*[@id="propertyStreetName"]', street_name)
        wait_and_send_keys(self.driver, '//*[@id="propertyUnit"]', unit)

        if qualifier:
            wait_and_send_keys(self.driver, '//*[@id="propertyQualifier"]', qualifier)

    def _submit(self):
        wait_and_click(self.driver, '//*[@id="assessmentTermOfService"]')
        wait_and_click(self.driver, '//*[@id="submit-button"]')

    def _safe_unit(self, unit):
        if pd.notna(unit):
            try:
                return str(int(unit))
            except:
                return str(unit)
        return ""

    def _safe_str(self, value):
        return str(value) if pd.notna(value) else ""