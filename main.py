# main.py

from pathlib import Path
from datetime import datetime
import shutil

from config import Config
from data_loader import load_addresses
from driver_manager import DriverManager
from scraper import TaxScraper
from wards import WARDS
from utils.logger import log_result, set_log_file

def setup_run_output_folder(config, ward):
    
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

def select_run_mode():
    print("\nSelect run mode:")
    print("1. New")
    print("2. Resume")
    choice = input("Enter 1 or 2: ").strip()

    if choice == "1":
        return "new"
    if choice == "2":
        return "resume"

    raise ValueError("Invalid selection. Enter 1 or 2.")

def prepare_input_checkpoint(config, mode):
    """
    For a new run: do nothing. load_addresses() will use raw input if no checkpoint exists.
    For a resume run: ask user for a to_be_checked.csv path and copy it into the new run folder.
    """
    if mode == "new":
        return None

    checkpoint_source = input(
        "Enter the full path to the to_be_checked.csv file to resume from: "
    ).strip()

    checkpoint_source = Path(checkpoint_source)

    if not checkpoint_source.exists():
        raise FileNotFoundError(f"Checkpoint file not found: {checkpoint_source}")

    shutil.copy2(checkpoint_source, config.checkpoint_path)

    print(f"Copied resume checkpoint to: {config.checkpoint_path}")

    return checkpoint_source

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
    # 2. Select mode
    # -------------------------
    mode = select_run_mode()

    # -------------------------
    # 3. Config
    # -------------------------
    config = Config.from_ward(ward)

    # -------------------------
    # 4. Create a fresh run folder
    # -------------------------
    setup_run_output_folder(config, ward)
    set_log_file(config.log_path)

    # -------------------------
    # 5. Prepare checkpoint input
    # -------------------------
    checkpoint_source = prepare_input_checkpoint(config, mode)

    log_kwargs = {
        "Ward": ward,
        "Mode": mode,
        "RunDir": config.output_path.parent
    }

    if mode == "resume":
        log_kwargs["ResumeFrom"] = checkpoint_source

    log_result(
        level="INFO",
        method="main",
        message="Run started",
        **log_kwargs
    )
    
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
        log_result(
            level="INFO",
            method="main",
            message="Run ended",
            Ward=ward,
            Mode=mode
        )
        print("Completed all addresses.")

if __name__ == "__main__":
    main()