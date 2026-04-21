# scraper.py

import pandas as pd
from processors.condo_processor import CondoProcessor
from processors.address_processor import AddressProcessor
from processors.parcel_processor import ParcelProcessor
from utils.batch_manager import BatchManager
from utils.grouping import group_addresses_by_parcel
from utils.io import save_to_json


class TaxScraper:
    def __init__(self, driver, config):
        self.driver = driver
        self.config = config

        self.batch_manager = None
        self.parcel_processor = None

    def run(self, to_be_checked):
        print("Starting scraper...")

        # -------------------------
        # Setup components
        # -------------------------
        
        self.batch_manager = BatchManager(
            config=self.config,
            to_be_checked=to_be_checked,
            save_func=save_to_json
        )

        
        self.condo_processor = CondoProcessor(
            driver=self.driver,
            batch_manager=self.batch_manager
        )

        self.address_processor = AddressProcessor(
            driver=self.driver,
            batch_manager=self.batch_manager,
            condo_processor=self.condo_processor
        )

        self.parcel_processor = ParcelProcessor(
            driver=self.driver,
            batch_manager=self.batch_manager,
            address_processor=self.address_processor,  # ← FIX
            config=self.config
        )


        # -------------------------
        # Group addresses
        # -------------------------
        grouped_addresses = group_addresses_by_parcel(to_be_checked)

        # -------------------------
        # Main loop (your original logic)
        # -------------------------
        for roll_number, group in grouped_addresses.items():

            if group and len(group) > 0:
                self.parcel_processor.process_group(
                    group=group,
                    roll_number=roll_number,
                    to_be_checked=to_be_checked
                )

        # -------------------------
        # Final flush
        # -------------------------
        self.batch_manager.flush()

        print("All addresses processed.")