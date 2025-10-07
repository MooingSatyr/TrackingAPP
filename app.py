import dash
from dash import Dash
from layout import create_layout
from callbacks import register_callbacks
from utils.data import load_data
import pandas as pd
from utils.resource_path import resource_path

df, zu_df = load_data(resource_path("Dima.xlsx"))

app = Dash(__name__)

app.layout = create_layout(df)

register_callbacks(app, df, zu_df)

if __name__ == "__main__":
    app.run(debug=False)
