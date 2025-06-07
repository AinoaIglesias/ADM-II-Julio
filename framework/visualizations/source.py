import pandas as pd

class DataSource:
    def __init__(self, path):
        self.path = path

    def load(self):
        try:
            df = pd.read_csv(self.path)
            print(f"✅ Datos cargados desde {self.path} con {len(df)} filas.")
            return df
        except Exception as e:
            print(f"❌ Error cargando datos: {e}")
            return pd.DataFrame()
