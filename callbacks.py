import dash
from dash import Input, Output, State, callback, no_update, dcc
from dash.exceptions import PreventUpdate
from utils.FigureUpdate import get_polar_ra, get_polar_re, expand_range_max
import numpy as np
from datetime import datetime, timedelta


def register_callbacks(app, df, zu_df):

    @app.callback(
        Output("time_slider", "min"),
        Output("time_slider", "max"),
        Output("time_slider", "value"),
        Output("time_slider", "step"),
        Output("time_slider", "marks"),
        Output("playback-store", "data"),
        Output("plot_range_store", "data"),
        Input("dropdown", "value"),
    )
    def update_slider_params(selected_name):
        """Обновляет параметры слайдера времени и диапазоны осей при выборе нового файла."""
        filtered_df = df[df.FileName == selected_name]
        if filtered_df.empty:
            raise PreventUpdate

        tmin = min(filtered_df["Time"])
        tmax = max(filtered_df["Time"])

        # Шаг для плавного движения — маленький
        step = (tmax - tmin) / len(filtered_df) if (tmax - tmin) > 0 else 1

        num_marks = min(10, len(filtered_df["Time"]))  
        marks = {}
        base_time = datetime.strptime(
            (list(filtered_df["FileName"])[0].split(".")[0][-6:]), "%H%M%S"
        )

        for i in range(num_marks):
            if num_marks > 1:
                value = tmin + (tmax - tmin) * i / (num_marks - 1)
            else:
                value = tmin

            rounded_value = int(round(value))
            label = (base_time + timedelta(seconds=rounded_value)).strftime("%H:%M:%S")
            marks[rounded_value] = {
                "label": label,
                "style": {"fontSize": "11px", "whiteSpace": "nowrap"},
            }

        # Обновляем состояние автопроигрывания
        playback_state = {
            "playing": False,
            "current_time": tmin,
            "speed": 0.5,
            "min_time": tmin,
            "max_time": tmax,
            "selected_file": selected_name,
        }

        range_max = max(filtered_df["Range"].max(), zu_df["Range"].max())

        return tmin, tmax, tmin, step, marks, playback_state, range_max


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
        """Обрабатывает кнопки управления воспроизведением и изменяет скорость."""
        ctx = dash.callback_context
        if not ctx.triggered:
            return playback_state, True

        button_id = ctx.triggered[0]["prop_id"].split(".")[0]

        # Обновляем выбранный файл если он изменился
        if playback_state["selected_file"] != selected_file:
            filtered_df = df[df.FileName == selected_file]
            if not filtered_df.empty:
                tmin = min(filtered_df["Time"])
                tmax = max(filtered_df["Time"])
                playback_state.update(
                    {
                        "current_time": tmin,
                        "min_time": tmin,
                        "max_time": tmax,
                        "selected_file": selected_file,
                    }
                )

        if button_id == "start-btn":
            playback_state["playing"] = True

        elif button_id == "pause-btn":
            playback_state["playing"] = False

        elif button_id == "speed-slider":
            playback_state["speed"] = speed

        playback_state["speed"] = speed

        # Обновляем интервал в зависимости от скорости
        interval_disabled = not playback_state["playing"]

        return playback_state, interval_disabled

    @app.callback(
        Output("time_slider", "value", allow_duplicate=True),
        Output("playback-store", "data", allow_duplicate=True),
        Output("playback-timer", "interval", allow_duplicate=True),
        Input("playback-timer", "n_intervals"),
        State("playback-store", "data"),
        State("dropdown", "value"),
        prevent_initial_call=True,
    )
    def auto_advance_by_point(n, playback_state, selected_file):
        """
        Автоматическое пошаговое воспроизведение по точкам данных.
        Шаг вычисляется до следующей точки в таблице. Скорость регулируется временем интервала.
        """
        if not playback_state["playing"]:
            # если воспроизведение на паузе
            current_time = playback_state["current_time"]
            time_info = f"Текущее время: {current_time:.2f} (пауза)"
            return current_time, playback_state, dash.no_update

        # Получаем отсортированные временные метки для выбранного файла
        times = np.sort(df[df.FileName == selected_file]["Time"].values)
        current_time = playback_state["current_time"]
        next_idx = np.searchsorted(times, current_time, side="right")

        if next_idx >= len(times):
            # достигли конца — стоп на последней точке
            playback_state["playing"] = False
            new_time = times[-1]
            slider_time = new_time
            return slider_time, playback_state, dash.no_update
        else:
            new_time = times[next_idx]

        playback_state["current_time"] = new_time

        # Узкий диапазон для слайдера
        slider_time = new_time


        # Пересчёт интервала таймера на основе скорости (ms)
        # speed = число точек/секунда
        speed = playback_state["speed"]
        interval_ms = int(1000 / speed) if speed > 0 else 1000

        return slider_time, playback_state, interval_ms

    @app.callback(
        Output("graph_x_y", "figure"),
        Input("time_slider", "value"),
        Input("playback-store", "data"),
        Input("show-history", "value"),
        State("dropdown", "value"),
        State("plot_range_store", "data"),
    )
    def update_graphs(
        slider_time, playback_state, show_history, selected_name, range_max
    ):  
        ctx = dash.callback_context
        button_id = ctx.triggered[0]["prop_id"].split(".")[0]
        print(f'Зашел в update_graphsб триггер - {button_id}')
        
        filtered_df = df[df.FileName == selected_name]

        if slider_time is not None:
            current_time = slider_time
            if show_history:
                filtered_df = filtered_df[filtered_df["Time"] <= current_time]
            else:
                filtered_df = filtered_df[filtered_df["Time"] == current_time]

        if filtered_df.empty:
            return no_update, no_update

        fig_ra = get_polar_ra(filtered_df, zu_df, range_max)

        return fig_ra

    @callback(
        Output("playback-store", "data", allow_duplicate=True),
        Input("time_slider", "value"),
        State("playback-store", "data"),
        prevent_initial_call=True,
    )
    def change_current_time(current_time, playback):
        playback["current_time"] = current_time
        return playback

    @callback(
        Output("start-btn", "style"),
        Output("pause-btn", "style"),
        Input("playback-store", "data"),
        prevent_initial_call=True,
    )
    def highlight_playback_buttons(playback_state):
        """Подсвечивает кнопку Старт, если воспроизведение активно, и Пауза, если на паузе."""
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

        # Подсветка активной кнопки
        if playback_state["playing"]:
            start_style = {
                **base_style,
                "backgroundColor": "#d4edda",
            }  # зелёная подсветка
            pause_style = base_style
        else:
            start_style = base_style
            pause_style = {
                **base_style,
                "backgroundColor": "#f8d7da",
            }  # красная подсветка

        return start_style, pause_style
    
    @app.callback(
        Output("slider-time-display", "children"),
        Input("time_slider", "value"),
        State("dropdown", "value")
    )
    def display_time(slider_value, selected_file):
        filtered_df = df[df.FileName == selected_file]



        if filtered_df.empty:
            raise PreventUpdate

        base_time = datetime.strptime(
            (list(filtered_df["FileName"])[0].split(".")[0][-6:]), "%H%M%S"
        )

        last_second=int((filtered_df["Time"]).iloc[-1])
    

        current_time = (base_time + timedelta(seconds=int(slider_value))).strftime("%H:%M:%S")
        last_time = (base_time + timedelta(seconds=last_second)).strftime("%H:%M:%S") 
        return f"{current_time}/{last_time}"

