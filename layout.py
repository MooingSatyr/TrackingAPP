import dash
from dash import dcc, html
import pandas as pd
import numpy as np


def create_layout(df):
    button_style = {
        "width": "120px",
        "height": "40px",
        "margin": "0 10px",
        "border": "1px solid #ced4da",
        "borderRadius": "6px",
        "backgroundColor": "#ffffff",
        "cursor": "pointer",
        "transition": "all 0.2s ease-in-out",
        "boxShadow": "0 2px 4px rgba(0,0,0,0.05)",
    }

    return html.Div(
        [
            # 🔹 ВЕРХНЯЯ ЧАСТЬ: Фильтры
            html.Div(
                [
                    html.Label("Выберите файл:"),
                    dcc.Dropdown(
                        id="dropdown",
                        options=[
                            {"label": name, "value": name}
                            for name in df["FileName"].unique()
                        ],
                        value=df["FileName"].iloc[0] if not df.empty else None,
                    ),
                ],
                style={"margin": "10px", "width": "20%", "alignItems": "left"},
            ),
            # 🔹 СРЕДНЯЯ ЧАСТЬ: Графики
            html.Div(
                [
                    dcc.Graph(
                        id="graph_x_y",
                        style={
                            "width": "100%",
                            "height": "800px",
                            "display": "block",
                        },
                    )
                ]
            ),
            # 🔹 НИЖНЯЯ ЧАСТЬ: Панель управления + слайдер времени
            html.Div(
                [
                    # Верхняя строка: кнопки слева, скорость + чекбокс справа
                    html.Div(
                        [
                            # Кнопки старт/пауза (слева)
                            html.Div(
                                [
                                    html.Button(
                                        "▶️ Старт",
                                        id="start-btn",
                                        n_clicks=0,
                                        style=button_style,
                                    ),
                                    html.Button(
                                        "⏸️ Пауза",
                                        id="pause-btn",
                                        n_clicks=0,
                                        style=button_style,
                                    ),
                                ],
                                style={
                                    "display": "inline-block",
                                    "marginRight": "20px",
                                },
                            ),
                            # Скорость + чекбокс (справа)
                            html.Div(
                                [
                                    html.Label("Скорость:"),
                                    dcc.Slider(
                                        id="speed-slider",
                                        min=0.5,
                                        max=5,
                                        step=0.5,
                                        value=0.5,
                                        marks={
                                            i: f"{i:.1f}×" for i in [0.5, 1, 2, 3, 4, 5]
                                        },
                                    ),
                                    dcc.Checklist(
                                        id="show-history",
                                        options=[
                                            {
                                                "label": "Показывать историю",
                                                "value": "history",
                                            }
                                        ],
                                        value=["history"],
                                        inline=True,
                                        style={"marginTop": "10px"},
                                    ),
                                ],
                                style={
                                    "display": "inline-block",
                                    "width": "20%",
                                },
                            ),
                        ],
                        style={
                            "display": "flex",
                            "justifyContent": "space-between",
                            "alignItems": "center",
                            "marginBottom": "15px",
                        },
                    ),
                    # Слайдер времени
                    html.Div(
                        [
                            html.Label("Диапазон времени:"),
                            dcc.Slider(
                                id="time_slider",
                                min=0,
                                max=1,
                                value=1,
                                step=0.1,
                                marks=None,
                                tooltip={
                                    "placement": "bottom",
                                    "always_visible": False,
                                },
                            ),
                            html.Div(
                                id="slider-time-display", style={"marginTop": "10px"}
                            ),
                        ],
                        style={"margin": "20px 10px"},
                    ),
                ],
                style={
                    "margin": "20px 10px",
                    "padding": "15px",
                    "backgroundColor": "#f8f9fa",
                    "border": "1px solid #dee2e6",
                    "borderRadius": "20px",
                },
            ),
            # 🔹 Скрытые компоненты для автопроигрывания
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
        ]
    )
