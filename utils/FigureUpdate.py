import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta

months = {
    1: "января",
    2: "февраля",
    3: "марта",
    4: "апреля",
    5: "мая",
    6: "июня",
    7: "июля",
    8: "августа",
    9: "сентября",
    10: "октября",
    11: "ноября",
    12: "декабря",
}


def get_figure(df, axis_ranges, x_axis, y_axis, current_time):
    """
    Строит scatter-график по выбранным осям с строгим визуальным стилем и указанием текущего времени.
    """

    # Разбор даты и времени начала
    date_str, time_str = df.FileName.iloc[0].replace(".log", "").split("_")
    dt_start = datetime.strptime(f"{date_str}_{time_str}", "%Y%m%d_%H%M%S")

    # Текущее время
    dt_current = dt_start + timedelta(seconds=current_time)
    delta_ms = int(current_time * 1000)

    # Основной scatter-график
    fig = px.scatter(df, x=x_axis, y=y_axis)
    fig.update_traces(
        mode="markers",
        marker={"color": "rgba(0, 51, 153, 0.7)", "size": 10},
    )

    # Центр координат
    fig.add_trace(
        go.Scatter(
            x=(0,),
            y=(0,),
            mode="markers",
            marker=dict(size=16, symbol="square", color="rgba(0, 0, 0, 0.5)"),
        )
    )

    # Последняя точка
    last_point = df.iloc[[-1]]
    fig.add_scatter(
        x=last_point["x"],
        y=last_point[y_axis],
        mode="markers",
        marker=dict(size=10, color="crimson"),
    )

    # Заголовок — строгий, с месяцами по-русски
    start_str = f"{dt_start.day} {months[dt_start.month]} {dt_start.year} {dt_start.strftime('%H:%M:%S')}"
    current_str = dt_current.strftime("%H:%M:%S.%f")[:-3]

    title_text = (
        f"Начало записи: {start_str}<br>"
        f"<span style='color:#555; font-family:monospace;'>"
        f"Текущее время: {current_str}"
        f"</span>"
    )

    # Оформление графика
    fig.update_layout(
        dragmode="pan",
        title=dict(
            text=title_text,
            x=0.5,
            font=dict(family="Arial", size=14, color="#111"),
        ),
        xaxis=dict(
            title=x_axis.upper(),
            range=axis_ranges["x"],
            showgrid=True,
            gridcolor="rgba(0,0,0,0.1)",
            zeroline=False,
        ),
        yaxis=dict(
            title=y_axis.upper(),
            range=axis_ranges[y_axis],
            showgrid=True,
            gridcolor="rgba(0,0,0,0.1)",
            zeroline=False,
        ),
        font=dict(family="Arial", size=12, color="#222"),
        plot_bgcolor="#ffffff",
        paper_bgcolor="#ffffff",
        margin=dict(l=60, r=40, t=80, b=60),
        uirevision="fixed",
    )

    fig.update_traces(showlegend=False, selector=dict(type="scatter"))
    return fig


def expand_range(vmin, vmax, pad_ratio=0.3):
    """Добавляем отступ к диапазону"""
    if vmin == vmax:
        return vmin - 1, vmax + 1
    delta = (vmax - vmin) * pad_ratio
    return vmin - delta, vmax + delta
