# data_manager.py
import pandas as pd

class DataManager:
    def __init__(self, config):
        self.config = config
        self.df = None

    def load(self):
        self.df = pd.read_csv(self.config.input_csv)
        return self.df

    def group_by_parcel(self):
        return self.df.groupby("parcel_assessment_roll_number")

    def save(self, df):
        df.to_csv(self.config.output_csv, index=False)