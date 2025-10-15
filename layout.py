import dash
from dash import dcc, html


def create_layout(df):
    button_style = {
        "width": "120px",
        "height": "40px",
        "margin": "0 10px",
        "border": "2px solid #adb5bd",
        "borderRadius": "6px",
        "backgroundColor": "#ffffff",
        "cursor": "pointer",
        "transition": "all 0.2s ease-in-out",
        "boxShadow": "0 2px 4px rgba(0,0,0,0.05)",
        "display": "flex",
        "justifyContent": "center",
        "alignItems": "center",
        "gap": "4px",
    }

    border_thick = "2px solid #adb5bd"

    return html.Div(
        [
            html.Div(
                [
                    # 🔹 ЛЕВАЯ КОЛОНКА
                    html.Div(
                        [
                            # --- БЛОК ЗАГРУЗКИ ---
                            html.Div(
                                [
                                    html.H4(
                                        "📂 Данные", style={"marginBottom": "10px"}
                                    ),
                                    html.Div(
                                        [
                                            html.Div(
                                                [
                                                    html.Label(
                                                        "Выберите файл:",
                                                        style={"fontWeight": "bold"},
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
                                                        placeholder="Выберите или загрузите файл...",
                                                        style={"width": "100%"},
                                                    ),
                                                ],
                                                style={
                                                    "flex": "3",
                                                    "marginRight": "10px",
                                                },
                                            ),
                                            html.Div(
                                                [
                                                    html.Label(
                                                        "Загрузка:",
                                                        style={"fontWeight": "bold"},
                                                    ),
                                                    dcc.Upload(
                                                        id="upload-data",
                                                        children=html.Div(
                                                            [
                                                                html.Img(
                                                                    src="/assets/upload.png",
                                                                    style={
                                                                        "width": "20px",
                                                                        "height": "20px",
                                                                        "marginRight": "8px",
                                                                        "verticalAlign": "middle",
                                                                    },
                                                                ),
                                                                html.A(
                                                                    "Добавить файлы",
                                                                    style={
                                                                        "cursor": "pointer",
                                                                        "verticalAlign": "middle",
                                                                    },
                                                                ),
                                                            ],
                                                            style={
                                                                "display": "flex",
                                                                "justifyContent": "center",
                                                                "alignItems": "center",
                                                                "gap": "6px",
                                                            },
                                                        ),
                                                        multiple=True,
                                                        style={
                                                            "width": "100%",
                                                            "height": "30px",
                                                            "lineHeight": "30px",
                                                            "borderWidth": "5px",
                                                            "borderRadius": "10px",
                                                            "textAlign": "center",
                                                            "backgroundColor": "#f9f9f9",
                                                            "cursor": "pointer",
                                                        },
                                                    ),
                                                ],
                                                style={"flex": "2"},
                                            ),
                                        ],
                                        style={
                                            "display": "flex",
                                            "gap": "10px",
                                            "alignItems": "end",
                                            "marginBottom": "10px",
                                        },
                                    ),
                                ],
                                style={
                                    "width": "100%",
                                    "padding": "12px",
                                    "backgroundColor": "#ffffff",
                                    "border": border_thick,
                                    "borderRadius": "10px",
                                    "boxShadow": "0 3px 8px rgba(0,0,0,0.05)",
                                    "marginBottom": "15px",
                                    "boxSizing": "border-box",
                                },
                            ),
                            # --- ГРАФИК ---
                            html.Div(
                                [
                                    html.Div(
                                        [
                                            dcc.Graph(
                                                id="graph_x_y",
                                                style={
                                                    "width": "100%",
                                                    "height": "700px",
                                                },
                                                config={"responsive": True},
                                            ),
                                            # Контейнер для кнопки и чекбокса
                                            html.Div(
                                                [
                                                    # Кнопка сохранить график - слева
                                                    html.Button(
                                                        "Сохранить график",
                                                        id="save-btn",
                                                        style={"marginRight": "10px"},
                                                    ),
                                                    # Чекбокс показать историю - справа
                                                    html.Div(
                                                        dcc.Checklist(
                                                            id="show-history",
                                                            options=[
                                                                {
                                                                    "label": "Показывать историю",
                                                                    "value": "history",
                                                                },
                                                            ],
                                                            value=["history"],
                                                            inline=True,
                                                        ),
                                                        style={
                                                            "marginLeft": "auto",  # Выравнивание по правому краю
                                                        },
                                                    ),
                                                ],
                                                style={
                                                    "display": "flex",
                                                    "justifyContent": "space-between",
                                                    "alignItems": "center",
                                                    "marginTop": "15px",
                                                    "width": "100%",
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
                                        },
                                    ),
                                ],
                                style={"width": "100%"},
                            ),
                        ],
                        style={
                            "flexBasis": "60%",
                            "maxWidth": "60%",
                            "minWidth": "400px",
                        },
                    ),
                    # 🔹 ПРАВАЯ КОЛОНКА — ПАНЕЛЬ
                    html.Div(
                        [
                            # --- Панель управления с кнопками и скоростью в одной строке ---
                            html.Div(
                                [
                                    # Кнопки слева
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
                                                    ),
                                                ],
                                                id="start-btn",
                                                n_clicks=0,
                                                style=button_style,
                                            ),
                                            html.Button(
                                                [
                                                    html.Img(
                                                        src="/assets/stop.png",
                                                        style={
                                                            "width": "20px",
                                                            "height": "20px",
                                                        },
                                                    ),
                                                ],
                                                id="pause-btn",
                                                n_clicks=0,
                                                style=button_style,
                                            ),
                                        ],
                                        style={"display": "flex", "gap": "1px"},
                                    ),
                                    # Дропдаун скорости справа
                                    html.Div(
                                        [
                                            html.Label(
                                                "Скорость:",
                                                style={
                                                    "fontWeight": "bold",
                                                    "marginRight": "10px",
                                                    "whiteSpace": "nowrap",
                                                },
                                            ),
                                            dcc.Dropdown(
                                                id="speed-dropdown",
                                                options=[
                                                    {"label": "0.5×", "value": 0.5},
                                                    {"label": "1×", "value": 1.0},
                                                    {"label": "2×", "value": 2.0},
                                                    {"label": "3×", "value": 3.0},
                                                    {"label": "4×", "value": 4.0},
                                                    {"label": "5×", "value": 5.0},
                                                ],
                                                value=1.0,
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
                                            "marginLeft": "auto",  # Выравнивание по правому краю
                                        },
                                    ),
                                ],
                                style={
                                    "display": "flex",
                                    "justifyContent": "space-between",
                                    "alignItems": "center",
                                    "marginBottom": "20px",
                                    "width": "100%",
                                },
                            ),
                            html.Div(
                                [
                                    html.Label(
                                        "Время:",
                                        style={"fontWeight": "bold"},
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
                                    html.Div(
                                        id="slider-time-display",
                                    ),
                                ],
                                style={"marginBottom": "25px"},
                            ),
                            # --- 📊 БЛОК СТАТИСТИКИ ---
                            html.Div(
                                id="stats-content",
                                children="Здесь будет отображаться статистика...",
                                style={
                                    "border": border_thick,
                                    "borderRadius": "8px",
                                    "backgroundColor": "#ffffff",
                                    "boxShadow": "0 2px 5px rgba(0,0,0,0.05)",
                                    "minHeight": "80px",
                                },
                            ),
                        ],
                        style={
                            "flexBasis": "38%",
                            "maxWidth": "38%",
                            "padding": "20px",
                            "backgroundColor": "#ffffffff",
                            "border": border_thick,
                            "borderRadius": "20px",
                            "boxShadow": "0 3px 8px rgba(0,0,0,0.05)",
                            "height": "fit-content",
                        },
                    ),
                ],
                style={
                    "display": "flex",
                    "flexDirection": "row",
                    "justifyContent": "space-between",
                    "alignItems": "flex-start",
                    "gap": "20px",
                    "padding": "20px",
                    "maxWidth": "100vw",
                    "overflowX": "hidden",
                },
            ),
            # --- Скрытые компоненты ---
            dcc.Interval(
                id="playback-timer", interval=1000, n_intervals=0, disabled=True
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
