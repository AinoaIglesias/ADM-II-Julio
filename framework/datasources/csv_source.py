from .base_source import BaseDataSource
from utils.cleaner import clean_dataframe
import pandas as pd

class CSVDataSource(BaseDataSource):
    def __init__(self, filepath):
        self.filepath = filepath

    def load(self) -> pd.DataFrame:
        df = pd.read_csv(self.filepath)
        df = clean_dataframe(df, strategy="auto")
        return df 




