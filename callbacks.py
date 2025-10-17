import dash
from dash import Input, Output, State, callback, no_update, dcc
from dash.exceptions import PreventUpdate
import pandas as pd
import numpy as np
import base64
import io
from datetime import datetime, timedelta
from utils.FigureUpdate import get_figure, expand_range
from utils.sphreric_to_decart import to_decart
import plotly.graph_objects as go
from ui.buttons import base_style


def register_callbacks(app):
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
        if not contents:
            raise PreventUpdate

        current_df = pd.DataFrame(data_records) if data_records else pd.DataFrame()

        for content, name in zip(contents, filenames):
            try:
                content_type, content_string = content.split(",")
                decoded = base64.b64decode(content_string)
                df_new = pd.read_csv(io.StringIO(decoded.decode("utf-8")))
                df_new["FileName"] = name
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

        filtered_df = filtered_df.dropna(subset=["time_stamp"])
        if filtered_df.empty:
            raise PreventUpdate

        tmin = float(filtered_df["time_stamp"].min())
        tmax = float(filtered_df["time_stamp"].max())
        if tmin == tmax:
            tmax = tmin + 1.0

        step = (tmax - tmin) / len(filtered_df)

        # Пустые метки - ничего не отображается под слайдером
        marks = None

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
                filtered_df["x"].min(),
                filtered_df["x"].max(),
            ),
            "y": expand_range(
                filtered_df["y"].min(),
                filtered_df["y"].max(),
            ),
            "z": expand_range(
                filtered_df["z"].min(),
                filtered_df["z"].max(),
            ),
        }

        return tmin, tmax, tmin, step, marks, playback_state, range_max

    # 🔹 3. Управление воспроизведением (старт, пауза, скорость)
    @app.callback(
        Output("playback-store", "data", allow_duplicate=True),
        Output("playback-timer", "disabled", allow_duplicate=True),
        Input("start-btn", "n_clicks"),
        Input("pause-btn", "n_clicks"),
        Input("speed-dropdown", "value"),
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
        Output("playback-timer", "disabled", allow_duplicate=True),
        Input("playback-timer", "n_intervals"),
        State("playback-store", "data"),
        State("dropdown", "value"),
        State("data-store", "data"),
        prevent_initial_call=True,
    )
    def auto_advance_by_point(n, playback_state, selected_file, data_records):
        if not playback_state["playing"]:
            return playback_state["current_time"], playback_state, dash.no_update, True

        df = pd.DataFrame(data_records)
        times = np.sort(df[df.FileName == selected_file]["time_stamp"].values)
        current_time = playback_state["current_time"]
        next_idx = np.searchsorted(times, current_time, side="right")

        if next_idx >= len(times):
            playback_state["playing"] = False
            new_time = times[-1]

            return new_time, playback_state, dash.no_update, True
        else:
            new_time = times[next_idx]

        playback_state["current_time"] = new_time
        speed = playback_state["speed"]
        interval_ms = int(1000 / speed) if speed > 0 else 1000

        return new_time, playback_state, interval_ms, False

    # 🔹 5. Обновление графика
    @app.callback(
        Output("graph_x_y", "figure"),
        Output("history-toggle-btn", "children"),
        Input("time_slider", "value"),
        Input("playback-store", "data"),
        Input("history-toggle-btn", "n_clicks"),
        State("dropdown", "value"),
        State("plot_range_store", "data"),
        State("data-store", "data"),
    )
    def update_graphs(
        slider_time,
        playback_state,
        n_clicks,
        selected_name,
        range_max,
        data_records,
    ):
        df = pd.DataFrame(data_records)
        filtered_df = df[df.FileName == selected_name]

        if n_clicks % 2 != 0:
            filtered_df = filtered_df[filtered_df["time_stamp"] <= slider_time]
            new_text = "Скрыть историю"
        else:
            filtered_df = filtered_df[filtered_df["time_stamp"] <= slider_time]
            filtered_df = filtered_df.iloc[[-1]]
            new_text = "Показать историю"

        if filtered_df.empty:
            return no_update

        current_time = playback_state["current_time"]

        fig_ra = get_figure(filtered_df, range_max, "x", "y", current_time)
        return fig_ra, new_text

    # 🔹 6. Обновление текущего времени
    @app.callback(
        Output("playback-store", "data", allow_duplicate=True),
        Input("time_slider", "value"),
        State("playback-store", "data"),
        prevent_initial_call=True,
    )
    def change_current_time(current_time, playback):
        playback["current_time"] = current_time
        return playback

    # 🔹 7. Подсветка кнопок
    @app.callback(
        Output("start-btn", "style"),
        Output("pause-btn", "style"),
        Input("playback-store", "data"),
        prevent_initial_call=True,
    )
    def highlight_playback_buttons(playback_state):
        if playback_state["playing"]:
            start_style = {**base_style, "backgroundColor": "#d4edda"}
            pause_style = base_style
        else:
            start_style = base_style
            pause_style = {**base_style, "backgroundColor": "#f8d7da"}

        return start_style, pause_style

    # 🔹 8. Отображение времени под слайдером
    @app.callback(
        Output("time_slider", "tooltip"),
        Input("time_slider", "value"),
        Input("dropdown", "value"),
        State("data-store", "data"),
    )
    def update_tooltip_format(slider_value, selected_file, data_records):
        if not selected_file or not data_records or slider_value is None:
            raise PreventUpdate

        df = pd.DataFrame(data_records)
        filtered_df = df[df.FileName == selected_file]

        if filtered_df.empty:
            raise PreventUpdate

        try:
            # Получаем базовое время из имени файла
            base_time = datetime.strptime(
                (list(filtered_df["FileName"])[0].split(".")[0][-6:]), "%H%M%S"
            )

            # Форматируем текущее время
            current_time = (base_time + timedelta(seconds=int(slider_value))).strftime(
                "%H:%M:%S"
            )

            # Возвращаем обновленные настройки tooltip
            return {
                "placement": "bottom",
                "always_visible": True,
                "template": current_time,  # Кастомный текст для tooltip
            }

        except Exception:
            # В случае ошибки возвращаем значение по умолчанию
            return {
                "placement": "bottom",
                "always_visible": True,
                "template": f"{slider_value}s",  # Fallback - показываем просто секунды
            }

    # 🔹 9. Статистика
    @app.callback(
        Output("stats-content", "children"),
        State("data-store", "data"),
        Input("dropdown", "value"),
        Input("time_slider", "value"),
    )
    def stats_update(records, selected_name, current_time):
        if not records or not selected_name:
            return dcc.Markdown(
                "**Нет данных для отображения.**",
                style={
                    "color": "#6c757d",
                    "fontSize": "15px",
                    "fontFamily": "Arial",
                    "whiteSpace": "pre-wrap",
                },
            )

        df = pd.DataFrame(records)
        df = df[df.FileName == selected_name].copy()
        if df.empty or "time_stamp" not in df.columns:
            return dcc.Markdown(
                "**Недостаточно данных для вычисления статистики.**",
                style={
                    "color": "#6c757d",
                    "fontSize": "15px",
                    "fontFamily": "Arial",
                    "whiteSpace": "pre-wrap",
                },
            )

        # Разбор даты начала записи (из имени файла)
        date_str, time_str = selected_name.replace(".log", "").split("_")
        dt_start = datetime.strptime(f"{date_str}_{time_str}", "%Y%m%d_%H%M%S")
        dt_current = dt_start + timedelta(seconds=current_time)
        delta_ms = int(current_time * 1000)

        # Общая статистика
        dots_total = len(df)
        x_range_total = [df["x"].min(), df["x"].max()]
        y_range_total = [df["y"].min(), df["y"].max()]
        z_range_total = [df["z"].min(), df["z"].max()]

        # Текущая статистика (до текущего времени)
        df_current = df[df["time_stamp"] <= current_time]
        if df_current.empty:
            dots_current = 0
            x_range_cur = y_range_cur = z_range_cur = [None, None]
        else:
            dots_current = len(df_current)
            x_range_cur = [df_current["x"].min(), df_current["x"].max()]
            y_range_cur = [df_current["y"].min(), df_current["y"].max()]
            z_range_cur = [df_current["z"].min(), df_current["z"].max()]

        # Форматирование времени
        current_str = dt_current.strftime("%H:%M:%S.%f")[:-3]

        # Markdown в строгом стиле
        markdown_text = f"""
    **Статистическая сводка по файлу:** `{selected_name}`

    #### Общие данные:
    - Количество записей: **{dots_total:,}**
    - Диапазон X: **{x_range_total[0]:.3f} — {x_range_total[1]:.3f}**
    - Диапазон Y: **{y_range_total[0]:.3f} — {y_range_total[1]:.3f}**
    - Диапазон Z: **{z_range_total[0]:.3f} — {z_range_total[1]:.3f}**

    ---

    #### Состояние на {current_str}:
    - Запись №: **{dots_current:,}**
    - Диапазон X: **{x_range_cur[0]:.3f} — {x_range_cur[1]:.3f}** {'' if x_range_cur[0] is not None else '—'}
    - Диапазон Y: **{y_range_cur[0]:.3f} — {y_range_cur[1]:.3f}** {'' if y_range_cur[0] is not None else '—'}
    - Диапазон Z: **{z_range_cur[0]:.3f} — {z_range_cur[1]:.3f}** {'' if z_range_cur[0] is not None else '—'}
    """.replace(
            ",", " "
        )

        return dcc.Markdown(
            markdown_text,
            style={
                "fontSize": "15px",
                "fontFamily": "Arial",
                "color": "#212529",
                "backgroundColor": "#ffffff",
                "borderRadius": "8px",
                "padding": "12px 18px",
                "boxShadow": "0 2px 6px rgba(0,0,0,0.05)",
                "whiteSpace": "pre-wrap",
                "lineHeight": "1.6",
            },
        )
