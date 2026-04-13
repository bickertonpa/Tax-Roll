# processors/parcel_processor.py

import pandas as pd

from utils.selenium_utils import wait_and_click, wait_and_send_keys, wait_for_results
from utils.parsing import extract_tax_data
from utils.logger import log_result


class ParcelProcessor:
    def __init__(self, driver, batch_manager, address_processor, config):
        """
        Args:
            driver: Selenium WebDriver
            batch_manager: BatchManager instance
            address_processor: AddressProcessor instance
            config: Config object
        """
        self.driver = driver
        self.batch_manager = batch_manager
        self.address_processor = address_processor
        self.config = config

        self.base_url = "https://propertytaxes-taxesfoncieres.ottawa.ca/en?t=taxassessmentlookup"

    # -------------------------
    # Public API
    # -------------------------

    def process_group(self, group, roll_number, to_be_checked):
        """
        Process a group of addresses sharing a parcel roll number.

        Strategy:
            1. Try parcel roll number lookup
            2. If success → apply to entire group
            3. If fail → fallback to individual address processing
        """

        if not group or len(group) == 0:
            return

        parcel_roll_number = roll_number

        # -------------------------
        # Attempt parcel lookup
        # -------------------------
        if parcel_roll_number and not pd.isna(parcel_roll_number):
            try:
                success, data = self._process_parcel_lookup(parcel_roll_number, group)

                if success:
                    address_count = len(group)

                    log_result(
                        level="OK",
                        method="parcel",
                        Roll=parcel_roll_number,
                        Count=address_count
                    )

                    data["PARCEL_ASSESSMENT_ROLL_NUMBER"] = parcel_roll_number
                    data["LOOKUP_METHOD"] = "PARCEL"
                    data["ADDRESSES_IN_PARCEL"] = address_count
                    self.batch_manager.add(data)

                    return  # Done with group

            except Exception as e:
                #print(f"Parcel lookup failed for {parcel_roll_number}: {e}")
                log_result(
                    level="ERR",
                    method="parcel",
                    message=str(e),
                    Roll=parcel_roll_number
                )

        # -------------------------
        # Fallback to address-level processing
        # -------------------------

        for address in group:
            result = self.address_processor.process(
                address,
                parcel_roll_number
            )

            if result:
                self.batch_manager.add(result)

    # -------------------------
    # Internal methods
    # -------------------------

    def _process_parcel_lookup(self, parcel_roll_number, group):
        """
        Perform lookup using parcel roll number.

        Returns:
            (success: bool, data: dict)
        """

        self.driver.get(self.base_url)

        # Select roll number search
        wait_and_click(self.driver, '//*[@id="taxWidgetOption-taxassessmentlookup"]')
        wait_and_click(self.driver, '//*[@id="taxAssessmentSearchOption-rollnumber"]')

        # Input roll number
        wait_and_send_keys(self.driver, '//*[@id="propertyRollNumber"]', parcel_roll_number)

        # Submit
        wait_and_click(self.driver, '//*[@id="assessmentTermOfService"]')
        wait_and_click(self.driver, '//*[@id="submit-button"]')

        # Wait for results
        if not wait_for_results(self.driver):
            return False, None

        # -------------------------
        # Check for error message FIRST
        # -------------------------
        from selenium.webdriver.common.by import By

        error_elements = self.driver.find_elements(By.ID, "assessment-search-result-message")

        if error_elements:
            error_message = error_elements[0].text.strip()

            if error_message:
                address_count = len(group)
                log_result(
                    level="ERR",
                    method="parcel",
                    Roll=parcel_roll_number,
                    message=error_message,
                    Count=address_count
                    )
                return False, None

        # -------------------------
        # Now safe to extract data
        # -------------------------
        try:
            data = extract_tax_data(self.driver)

            if not data:
                return False, None

            return True, data

        except Exception as e:
            print(f"Error extracting parcel data: {e}")
            return False, None