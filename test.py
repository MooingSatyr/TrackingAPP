from dash import html, dcc, Input, Output, State, callback
import plotly.graph_objects as go
from datetime import datetime
import os

# layout
html.Button("Сохранить график", id="save-btn"),
dcc.Interval(id="save-btn-reset", interval=2000, n_intervals=0, disabled=True)

# callback
@callback(
    Output("save-btn", "children"),
    Output("save-btn-reset", "disabled"),
    Input("save-btn", "n_clicks"),
    State("graph_x_y", "figure"),
    prevent_initial_call=True
)
def save_graph(n_clicks, fig_dict):
    if not fig_dict:
        raise dash.exceptions.PreventUpdate

    # сохраняем график
    fig = go.Figure(fig_dict)
    os.makedirs("exports", exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.join("exports", f"saved_plot_{timestamp}.png")
    fig.write_image(filename)
    
    # включаем таймер для сброса кнопки
    return f"Сохранено: {timestamp}", False  # False → таймер активен

# callback для сброса текста кнопки
@app.callback(
    Output("save-btn", "children"),
    Output("save-btn-reset", "disabled"),
    Input("save-btn-reset", "n_intervals"),
    prevent_initial_call=True
)
def reset_save_btn(n):
    # возвращаем исходный текст и отключаем таймер
    return "Сохранить график", True
