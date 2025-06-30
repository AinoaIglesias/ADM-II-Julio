import pandas as pd
from .base_source import BaseDataSource
from utils.cleaner import clean_dataframe

class ExcelDataSource(BaseDataSource):
    def __init__(self, filepath):
        self.filepath = filepath

    def load(self) -> pd.DataFrame:
        df = pd.read_excel(self.filepath)
        df = clean_dataframe(df, strategy="auto")
        return df 
