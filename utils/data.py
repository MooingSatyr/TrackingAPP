import pandas as pd
from utils.sphreric_to_decart import to_decart


def load_data(filepath="output.xlsx"):
    df = pd.read_excel(filepath, sheet_name="Лист1")
    to_decart(df)
    return df
