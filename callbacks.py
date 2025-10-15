import dash
from dash import Input, Output, State, callback, no_update, html
from dash.exceptions import PreventUpdate
import pandas as pd
import numpy as np
import base64
import io
from datetime import datetime, timedelta
from utils.FigureUpdate import get_figure, expand_range
from utils.sphreric_to_decart import to_decart


def register_callbacks(app, df_init, zu_df):
    """
    Регистрирует все callback'и приложения.
    df_init — исходный DataFrame, загруженный при старте.
    """

    # 🔹 1. Добавление новых файлов
    @app.callback(
        Output("data-store", "data", allow_duplicate=True),
        Output("dropdown", "options", allow_duplicate=True),
        Output("dropdown", "value", allow_duplicate=True),
        Input("upload-data", "contents"),
        State("upload-data", "filename"),
        State("data-store", "data"),
        prevent_initial_call=True,
    )
    def upload_new_files(contents, filenames, data_records):
        """Добавляет новые файлы в общий DataFrame и обновляет список выбора."""
        if not contents:
            raise PreventUpdate

        current_df = pd.DataFrame(data_records) if data_records else pd.DataFrame()

        for content, name in zip(contents, filenames):
            try:
                content_type, content_string = content.split(",")
                decoded = base64.b64decode(content_string)
                df_new = pd.read_csv(io.StringIO(decoded.decode("utf-8")))
                df_new["FileName"] = name  # добавляем имя файл
                to_decart(df_new)

                current_df = pd.concat([current_df, df_new], ignore_index=True)
                print(f"✅ Файл {name} успешно добавлен.")
            except Exception as e:
                print(f"⚠️ Ошибка при загрузке {name}: {e}")

        options = [{"label": n, "value": n} for n in current_df["FileName"].unique()]
        new_value = filenames[-1] if filenames else None

        return current_df.to_dict("records"), options, new_value

    # 🔹 2. Обновление параметров слайдера при выборе файла
    @app.callback(
        Output("time_slider", "min"),
        Output("time_slider", "max"),
        Output("time_slider", "value"),
        Output("time_slider", "step"),
        Output("time_slider", "marks"),
        Output("playback-store", "data"),
        Output("plot_range_store", "data"),
        Input("dropdown", "value"),
        State("data-store", "data"),
    )
    def update_slider_params(selected_name, data_records):
        if not selected_name or not data_records:
            raise PreventUpdate

        df = pd.DataFrame(data_records)
        filtered_df = df[df.FileName == selected_name].copy()
        if filtered_df.empty or "time_stamp" not in filtered_df.columns:
            raise PreventUpdate

        # убираем NaN в time_stamp
        filtered_df = filtered_df.dropna(subset=["time_stamp"])
        if filtered_df.empty:
            raise PreventUpdate

        tmin = float(filtered_df["time_stamp"].min())
        tmax = float(filtered_df["time_stamp"].max())

        # защита от деления на 0
        if tmin == tmax:
            tmax = tmin + 1.0

        step = (tmax - tmin) / len(filtered_df)

        num_marks = min(10, len(filtered_df))
        marks = {}

        # пытаемся получить базовое время из имени файла
        try:
            base_time = datetime.strptime(
                (list(filtered_df["FileName"])[0].split(".")[0][-6:]), "%H%M%S"
            )
        except Exception:
            base_time = datetime.strptime("000000", "%H%M%S")

        for i in range(num_marks):
            if num_marks > 1:
                value = tmin + (tmax - tmin) * i / (num_marks - 1)
            else:
                value = tmin

            if pd.isna(value):
                continue  # пропускаем NaN

            rounded_value = int(round(value))
            label = (base_time + timedelta(seconds=rounded_value)).strftime("%H:%M:%S")
            marks[rounded_value] = {
                "label": label,
                "style": {"fontSize": "11px", "whiteSpace": "nowrap"},
            }

        playback_state = {
            "playing": False,
            "current_time": tmin,
            "speed": 0.5,
            "min_time": tmin,
            "max_time": tmax,
            "selected_file": selected_name,
        }

        range_max = {
            "x": expand_range(
                min(filtered_df["x"].min(), zu_df["x"].min()),
                max(filtered_df["x"].max(), zu_df["x"].max()),
            ),
            "y": expand_range(
                min(filtered_df["y"].min(), zu_df["y"].min()),
                max(filtered_df["y"].max(), zu_df["y"].max()),
            ),
            "z": expand_range(
                min(filtered_df["z"].min(), zu_df["z"].min()),
                max(filtered_df["z"].max(), zu_df["z"].max()),
            ),
        }

        return tmin, tmax, tmin, step, marks, playback_state, range_max

    # 🔹 3. Управление воспроизведением (старт, пауза, скорость)
    @app.callback(
        Output("playback-store", "data", allow_duplicate=True),
        Output("playback-timer", "disabled", allow_duplicate=True),
        Input("start-btn", "n_clicks"),
        Input("pause-btn", "n_clicks"),
        Input("speed-slider", "value"),
        State("playback-store", "data"),
        State("dropdown", "value"),
        prevent_initial_call=True,
    )
    def control_playback(start, pause, speed, playback_state, selected_file):
        ctx = dash.callback_context
        if not ctx.triggered:
            return playback_state, True

        button_id = ctx.triggered[0]["prop_id"].split(".")[0]

        if playback_state["selected_file"] != selected_file:
            playback_state.update({"selected_file": selected_file})

        if button_id == "start-btn":
            playback_state["playing"] = True
        elif button_id == "pause-btn":
            playback_state["playing"] = False

        playback_state["speed"] = speed
        interval_disabled = not playback_state["playing"]

        return playback_state, interval_disabled

    # 🔹 4. Автоматическое продвижение по времени
    @app.callback(
        Output("time_slider", "value", allow_duplicate=True),
        Output("playback-store", "data", allow_duplicate=True),
        Output("playback-timer", "interval", allow_duplicate=True),
        Input("playback-timer", "n_intervals"),
        State("playback-store", "data"),
        State("dropdown", "value"),
        State("data-store", "data"),
        prevent_initial_call=True,
    )
    def auto_advance_by_point(n, playback_state, selected_file, data_records):
        if not playback_state["playing"]:
            return playback_state["current_time"], playback_state, dash.no_update

        df = pd.DataFrame(data_records)
        times = np.sort(df[df.FileName == selected_file]["time_stamp"].values)
        current_time = playback_state["current_time"]
        next_idx = np.searchsorted(times, current_time, side="right")

        if next_idx >= len(times):
            playback_state["playing"] = False
            new_time = times[-1]
            return new_time, playback_state, dash.no_update
        else:
            new_time = times[next_idx]

        playback_state["current_time"] = new_time
        speed = playback_state["speed"]
        interval_ms = int(1000 / speed) if speed > 0 else 1000

        return new_time, playback_state, interval_ms

    # 🔹 5. Обновление графика
    @app.callback(
        Output("graph_x_y", "figure"),
        Input("time_slider", "value"),
        Input("playback-store", "data"),
        Input("show-history", "value"),
        State("dropdown", "value"),
        State("plot_range_store", "data"),
        State("data-store", "data"),
    )
    def update_graphs(
        slider_time,
        playback_state,
        show_history,
        selected_name,
        range_max,
        data_records,
    ):
        df = pd.DataFrame(data_records)
        filtered_df = df[df.FileName == selected_name]

        if slider_time is not None:
            if show_history:
                filtered_df = filtered_df[filtered_df["time_stamp"] <= slider_time]
            else:
                filtered_df = filtered_df[filtered_df["time_stamp"] == slider_time]

        if filtered_df.empty:
            return no_update

        fig_ra = get_figure(filtered_df, zu_df, range_max, "x", "y")
        return fig_ra

    # 🔹 6. Обновление текущего времени в Store
    @app.callback(
        Output("playback-store", "data", allow_duplicate=True),
        Input("time_slider", "value"),
        State("playback-store", "data"),
        prevent_initial_call=True,
    )
    def change_current_time(current_time, playback):
        playback["current_time"] = current_time
        return playback

    # 🔹 7. Подсветка активных кнопок
    @app.callback(
        Output("start-btn", "style"),
        Output("pause-btn", "style"),
        Input("playback-store", "data"),
        prevent_initial_call=True,
    )
    def highlight_playback_buttons(playback_state):
        base_style = {
            "width": "120px",
            "height": "40px",
            "margin": "0 10px",
            "border": "1px solid #ced4da",
            "borderRadius": "6px",
            "cursor": "pointer",
            "transition": "all 0.2s ease-in-out",
            "boxShadow": "0 2px 4px rgba(0,0,0,0.05)",
            "backgroundColor": "#ffffff",
        }

        if playback_state["playing"]:
            start_style = {**base_style, "backgroundColor": "#d4edda"}
            pause_style = base_style
        else:
            start_style = base_style
            pause_style = {**base_style, "backgroundColor": "#f8d7da"}

        return start_style, pause_style

    # 🔹 8. Отображение текущего времени под слайдером
    @app.callback(
        Output("slider-time-display", "children"),
        Input("time_slider", "value"),
        State("dropdown", "value"),
        State("data-store", "data"),
    )
    def display_time(slider_value, selected_file, data_records):
        df = pd.DataFrame(data_records)
        filtered_df = df[df.FileName == selected_file]

        if filtered_df.empty:
            raise PreventUpdate

        base_time = datetime.strptime(
            (list(filtered_df["FileName"])[0].split(".")[0][-6:]), "%H%M%S"
        )

        last_second = int(filtered_df["time_stamp"].iloc[-1])
        current_time = (base_time + timedelta(seconds=int(slider_value))).strftime(
            "%H:%M:%S"
        )
        last_time = (base_time + timedelta(seconds=last_second)).strftime("%H:%M:%S")

        return f"{current_time}/{last_time}"

    @app.callback(
        Output("stats-content", "children"),
        State("data-store", "data"),
        Input("dropdown", "value"),
    )
    def stats_update(records, selected_name):
        if not records:
            return html.Div("Нет данных для отображения.", style={"color": "#6c757d"})

        df = pd.DataFrame(records)
        df = df[df.FileName == selected_name]
        dots_count = len(df)
        x_range = [df["x"].min(), df["x"].max()]
        y_range = [df["y"].min(), df["y"].max()]
        z_range = [df["z"].min(), df["z"].max()]

        return html.Div(
            [
                html.Ul(
                    [
                        html.Li(
                            f"Количество записей:   {dots_count:,}".replace(",", " ")
                        ),
                        html.Li(
                            f"Диапазон по оси X:   {x_range[0]:.3f} — {x_range[1]:.3f}"
                        ),
                        html.Li(
                            f"Диапазон по оси Y:   {y_range[0]:.3f} — {y_range[1]:.3f}"
                        ),
                        html.Li(
                            f"Диапазон по оси Z:   {z_range[0]:.3f} — {z_range[1]:.3f}"
                        ),
                    ],
                    style={
                        "listStyleType": "none",
                        "paddingLeft": "1px",
                        "lineHeight": "2",
                    },
                ),
            ],
            style={
                "fontSize": "15px",
                "color": "#212529",
                "backgroundColor": "#ffffff",
                "borderRadius": "8px",
                "padding": "10px 15px",
                "boxShadow": "0 2px 6px rgba(0,0,0,0.05)",
            },
        )
