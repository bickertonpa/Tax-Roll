# main.py

from config import Config
from data_loader import load_addresses
from driver_manager import DriverManager
from scraper import TaxScraper
from wards import WARDS
from utils.logger import set_log_file

def setup_run_output_folder(config, ward):
    from datetime import datetime

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_ward = ward.replace(" ", "_")

    run_dir = config.base_dir / "Output" / f"{safe_ward}_{timestamp}"
    run_dir.mkdir(parents=True, exist_ok=False)

    config.output_path = run_dir / f"{safe_ward}.json"
    config.checkpoint_path = run_dir / f"{safe_ward}_to_be_checked.csv"
    config.log_path = run_dir / f"scraper_{timestamp}.log"

    print(f"Run folder: {run_dir}")
    print(f"Results path: {config.output_path}")
    print(f"Checkpoint path: {config.checkpoint_path}")
    print(f"Log path: {config.log_path}")

    return run_dir

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
    # 3. Create run folder and redirect outputs
    # -------------------------
    setup_run_output_folder(config, ward)
    set_log_file(config.log_path)

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