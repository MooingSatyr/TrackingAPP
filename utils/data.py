import pandas as pd


def load_data(filepath="output.xlsx"):
    df = pd.read_excel(filepath, sheet_name="Лист1")

    zu_df = pd.read_excel(filepath, sheet_name="Лист2")
    return df, zu_df
