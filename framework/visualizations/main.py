from source import DataSource
from config import DATA_PATH, VISUALIZATIONS

def main():
    source = DataSource(DATA_PATH)
    df = source.load()

    if df.empty:
        print("⚠️ Dataset vacío. Revisa la ruta o el archivo.")
        return

    for strategy in VISUALIZATIONS:
        strategy.visualize(df)

if __name__ == "__main__":
    main()
