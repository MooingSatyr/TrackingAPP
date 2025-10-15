import dash
from dash import html, dcc, Output, Input

app = dash.Dash(__name__)

app.layout = html.Div([
    html.Label("Скорость"),
    dcc.Dropdown(
        id='speed-dropdown',
        options=[
            {'label': '0.5x', 'value': 0.5},
            {'label': '1x', 'value': 1},
            {'label': '2x', 'value': 2},
            {'label': '3x', 'value': 3},
            {'label': '4x', 'value': 4},
            {'label': '5x', 'value': 5},
        ],
        value=1,  # значение по умолчанию
        clearable=False,
        style={'width': '120px'}
    ),
    html.Div(id='speed-display')
])

@app.callback(
    Output('speed-display', 'children'),
    Input('speed-dropdown', 'value')
)
def update_speed(value):
    return f"Текущая скорость: {value}x"

if __name__ == '__main__':
    app.run(debug=True)
