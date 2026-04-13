# utils/batch_manager.py

import pandas as pd
from typing import List, Dict, Any, Callable


class BatchManager:
    """
    Manages batching, incremental saving, and checkpoint updates.

    Responsibilities:
        - Accumulate scraped records
        - Save to JSON in batches
        - Update checkpoint (to_be_checked)
        - Ensure no duplicate processing
    """

    def __init__(
        self,
        config,
        to_be_checked: List[Dict[str, Any]],
        save_func: Callable
    ):
        """
        Args:
            config: Config object (paths + batch_size)
            to_be_checked: mutable list of remaining addresses
            save_func: function to persist data (your existing save_to_json)
        """
        self.config = config
        self.to_be_checked = to_be_checked
        self.save_func = save_func

        self.batch: List[Dict[str, Any]] = []
        self.total_saved = 0

    # -------------------------
    # Public API
    # -------------------------

    def add(self, record: Dict[str, Any]):
        """
        Add a single record to the batch and trigger save if needed.
        """
        if not record:
            return

        self.batch.append(record)

        if len(self.batch) >= self.config.batch_size:
            self._flush()

    def add_many(self, records: List[Dict[str, Any]]):
        """
        Add multiple records (useful for condo processing).
        """
        if not records:
            return

        for record in records:
            self.add(record)

    def flush(self):
        """
        Force save remaining records.
        """
        if self.batch:
            self._flush()

    # -------------------------
    # Internal methods
    # -------------------------

    def _flush(self):
        """
        Save current batch and update checkpoint.
        """
        if not self.batch:
            return

        # Debug / visibility
        print(f"Saving batch of {len(self.batch)} records...")

        # Call your existing save function
        self.save_func(
            self.batch,
            self.config.output_path,
            self.to_be_checked,
            self.config.checkpoint_path
        )

        self.total_saved += len(self.batch)

        print(f"Total records saved so far: {self.total_saved}")
        print(f"Remaining addresses: {len(self.to_be_checked)}")

        # Clear batch
        self.batch.clear()