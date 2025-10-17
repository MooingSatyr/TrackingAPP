import dash
from dash import dcc, html
from ui.buttons import base_style


def create_layout(df):
    border_thick = "2px solid #adb5bd"

    return html.Div(
        [
            # 🔹 Внешний контейнер
            html.Div(
                [
                    # 🔹 Левая колонка
                    html.Div(
                        [
                            # --- Панель работы с файлами ---
                            html.Div(
                                [
                                    html.H4(
                                        "Файлы",
                                        style={
                                            "marginBottom": "10px",
                                            "fontWeight": "bold",
                                        },
                                    ),
                                    html.Div(
                                        [
                                            html.Div(
                                                [
                                                    html.Label(
                                                        "Выберите файл:",
                                                        style={
                                                            "fontWeight": "bold",
                                                            "marginBottom": "5px",
                                                        },
                                                    ),
                                                    dcc.Dropdown(
                                                        id="dropdown",
                                                        options=[
                                                            {
                                                                "label": name,
                                                                "value": name,
                                                            }
                                                            for name in df[
                                                                "FileName"
                                                            ].unique()
                                                        ],
                                                        value=(
                                                            df["FileName"].iloc[0]
                                                            if not df.empty
                                                            else None
                                                        ),
                                                        placeholder="Выберите файл...",
                                                        style={"width": "100%"},
                                                        clearable=False,
                                                    ),
                                                ],
                                                style={"flex": "1"},
                                            ),
                                            html.Div(
                                                [
                                                    html.Label(
                                                        "Загрузить файл:",
                                                        style={
                                                            "fontWeight": "bold",
                                                            "marginBottom": "5px",
                                                        },
                                                    ),
                                                    dcc.Upload(
                                                        id="upload-data",
                                                        children=html.Div(
                                                            "Выберите файл"
                                                        ),
                                                        multiple=True,
                                                        style={
                                                            "width": "100%",
                                                            "height": "35px",
                                                            "lineHeight": "40px",
                                                            "borderWidth": "1px",
                                                            "borderStyle": "solid",
                                                            "borderColor": "#adb5bd",
                                                            "borderRadius": "8px",
                                                            "textAlign": "center",
                                                            "backgroundColor": "#ffffff",
                                                            "cursor": "pointer",
                                                            "fontSize": "14px",
                                                        },
                                                    ),
                                                ],
                                                style={
                                                    "flex": "1",
                                                    "marginLeft": "10px",
                                                },
                                            ),
                                        ],
                                        style={
                                            "display": "flex",
                                            "gap": "10px",
                                            "marginBottom": "15px",
                                        },
                                    ),
                                ],
                                style={
                                    "width": "100%",
                                    "padding": "16px",
                                    "backgroundColor": "#ffffff",
                                    "border": "1px solid #adb5bd",
                                    "borderRadius": "10px",
                                    "boxShadow": "0 2px 6px rgba(0,0,0,0.05)",
                                    "boxSizing": "border-box",
                                    "marginBottom": "20px",
                                    "flex": "0 0 auto",
                                },
                            ),
                            # --- График ---
                            html.Div(
                                [
                                    dcc.Graph(
                                        id="graph_x_y",
                                        style={"width": "100%", "height": "100%"},
                                        config={
                                            "displaylogo": False,
                                            "responsive": True,
                                            "scrollZoom": True,
                                            "modeBarButtonsToRemove": [
                                                "select2d",
                                                "lasso2d",
                                                "autoScale2d",
                                                "resetScale2d",
                                            ],
                                            "displayModeBar": True,
                                        },
                                    ),
                                ],
                                style={
                                    "border": border_thick,
                                    "borderRadius": "10px",
                                    "backgroundColor": "#ffffff",
                                    "padding": "12px",
                                    "boxShadow": "0 3px 8px rgba(0,0,0,0.05)",
                                    "overflow": "hidden",
                                    "boxSizing": "border-box",
                                    "flex": "1 1 0",
                                    "minHeight": "700px",
                                },
                            ),
                        ],
                        style={
                            "flexBasis": "70%",
                            "maxWidth": "70%",
                            "minWidth": "400px",
                            "display": "flex",
                            "flexDirection": "column",
                            "justifyContent": "flex-start",
                            "flexGrow": "1",
                            "height": "100%",
                        },
                    ),
                    # 🔹 Правая колонка
                    html.Div(
                        [
                            # --- Статистика сверху ---
                            html.Div(
                                id="stats-content",
                                children="Здесь будет отображаться статистика...",
                                style={
                                    "border": border_thick,
                                    "borderRadius": "8px",
                                    "backgroundColor": "#ffffff",
                                    "boxShadow": "0 2px 5px rgba(0,0,0,0.05)",
                                    "minHeight": "80px",
                                    "marginBottom": "20px",
                                },
                            ),
                            # --- Нижний блок: кнопки + скорость + слайдер ---
                            html.Div(
                                [
                                    html.Div(
                                        [
                                            html.Button(
                                                [
                                                    html.Img(
                                                        src="/assets/play.png",
                                                        style={
                                                            "width": "20px",
                                                            "height": "20px",
                                                        },
                                                    )
                                                ],
                                                id="start-btn",
                                                n_clicks=0,
                                                style=base_style,
                                            ),
                                            html.Button(
                                                [
                                                    html.Img(
                                                        src="/assets/stop.png",
                                                        style={
                                                            "width": "20px",
                                                            "height": "20px",
                                                        },
                                                    )
                                                ],
                                                id="pause-btn",
                                                n_clicks=0,
                                                style=base_style,
                                            ),
                                            html.Div(
                                                [
                                                    html.Button(
                                                        "Показать историю",
                                                        id="history-toggle-btn",
                                                        n_clicks=0,
                                                        style=base_style,
                                                    ),
                                                ],
                                                style={
                                                    "display": "flex",
                                                    "gap": "10px",
                                                },
                                            ),
                                            html.Div(
                                                [
                                                    html.Label(
                                                        "Скорость:",
                                                        style={
                                                            "fontWeight": "bold",
                                                            "marginLeft": "10px",
                                                            "whiteSpace": "nowrap",
                                                        },
                                                    ),
                                                    dcc.Dropdown(
                                                        id="speed-dropdown",
                                                        options=[
                                                            {
                                                                "label": "0.5×",
                                                                "value": 0.5,
                                                            },
                                                            {
                                                                "label": "1×",
                                                                "value": 1.0,
                                                            },
                                                            {
                                                                "label": "2×",
                                                                "value": 2.0,
                                                            },
                                                            {
                                                                "label": "3×",
                                                                "value": 3.0,
                                                            },
                                                        ],
                                                        value=0.5,
                                                        clearable=False,
                                                        style={
                                                            "width": "100px",
                                                            "minWidth": "100px",
                                                        },
                                                    ),
                                                ],
                                                style={
                                                    "display": "flex",
                                                    "alignItems": "center",
                                                    "marginTop": "10px",
                                                    "gap": "10px",
                                                },
                                            ),
                                        ],
                                        style={
                                            "display": "flex",
                                            "alignItems": "center",
                                            "gap": "5px",
                                            "flexWrap": "wrap",
                                        },
                                    ),
                                    # Слайдер под кнопками
                                    html.Div(
                                        [
                                            html.Label(
                                                "Время:",
                                                style={
                                                    "fontWeight": "bold",
                                                    "marginTop": "10px",
                                                },
                                            ),
                                            dcc.Slider(
                                                id="time_slider",
                                                min=0,
                                                max=1,
                                                value=1,
                                                step=0.1,
                                                tooltip={
                                                    "placement": "bottom",
                                                    "always_visible": True,
                                                },
                                            ),
                                            html.Div(id="slider-time-display"),
                                        ],
                                        style={"marginTop": "10px"},
                                    ),
                                ],
                                style={"marginTop": "auto"},
                            ),
                        ],
                        style={
                            "flexBasis": "28%",
                            "maxWidth": "28%",
                            "padding": "20px",
                            "backgroundColor": "#ffffffff",
                            "border": border_thick,
                            "borderRadius": "20px",
                            "boxShadow": "0 3px 8px rgba(0,0,0,0.05)",
                            "display": "flex",
                            "flexDirection": "column",
                            "justifyContent": "flex-start",
                            "alignSelf": "stretch",
                            "flexGrow": "1",
                            "boxSizing": "border-box",
                        },
                    ),
                ],
                style={
                    "display": "flex",
                    "flexDirection": "row",
                    "justifyContent": "space-between",
                    "alignItems": "stretch",
                    "gap": "20px",
                    "padding": "20px",
                    "maxWidth": "100vw",
                    "height": "100%",
                    "overflowX": "hidden",
                },
            ),
            dcc.Interval(
                id="playback-timer", interval=1000, n_intervals=0, disabled=True
            ),
            dcc.Interval(
                id="save-btn-reset", interval=2000, n_intervals=0, disabled=True
            ),
            dcc.Store(
                id="playback-store",
                data={
                    "playing": False,
                    "current_time": 0,
                    "speed": 5,
                    "min_time": 0,
                    "max_time": 1,
                    "selected_file": None,
                },
            ),
            dcc.Store(id="plot_range_store", data={}),
            dcc.Store(id="data-store", data=df.to_dict("records")),
        ]
    )
