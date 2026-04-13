# main.py

from config import Config
from data_loader import load_addresses
from driver_manager import DriverManager
from scraper import TaxScraper
from wards import WARDS


def main():
    # -------------------------
    # 1. Select Ward
    # -------------------------
    ward_input = input("Please enter the ward number: ")
    ward = WARDS.get(str(ward_input))

    if not ward:
        raise ValueError("Invalid ward number.")

    print(f"Scraping data for ward: {ward}")

    # -------------------------
    # 2. Config
    # -------------------------
    config = Config.from_ward(ward)

    # -------------------------
    # 3. Load Data
    # -------------------------
    to_be_checked = load_addresses(config)
    print(f"Number of addresses remaining: {len(to_be_checked)}")

    # -------------------------
    # 4. Driver Lifecycle
    # -------------------------
    driver_manager = DriverManager(headless=True)
    driver = driver_manager.start()

    try:
        # -------------------------
        # 5. Run Scraper
        # -------------------------
        scraper = TaxScraper(driver, config)
        scraper.run(to_be_checked)

    finally:
        # -------------------------
        # 6. Cleanup
        # -------------------------
        driver_manager.stop()
        print("Completed all addresses.")


if __name__ == "__main__":
    main()