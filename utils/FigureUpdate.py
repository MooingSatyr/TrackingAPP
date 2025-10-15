import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime

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


def get_figure(df, axis_ranges, x_axis, y_axis):

    date_str, time_str = df.FileName.iloc[0].replace(".log", "").split("_")
    dt = datetime.strptime(f"{date_str}_{time_str}", "%Y%m%d_%H%M%S")

    fig = px.scatter(df, x=x_axis, y=y_axis)

    fig.update_traces(
        customdata=df.index,
        mode="markers",
        marker={"color": "rgb(0, 0, 150)", "size": 12, "opacity": 0.7},
    )

    fig.add_trace(
        go.Scatter(
            x=(0,),
            y=(0,),
            mode="markers",
            marker=dict(size=22, symbol="square", color="rgb(0, 150, 30)"),
        )
    )

    # Добавляем отдельный trace для последней точки
    last_point = df.iloc[[-1]]  # последняя точка

    if y_axis == "y":
        fig.add_scatter(
            x=last_point["x"],
            y=last_point[y_axis],
            mode="markers+text",
            marker=dict(size=12, color="red"),
            text=["🡇"],
            textposition="top center",
        )
    else:
        fig.add_scatter(
            x=last_point["x"],
            y=last_point[y_axis],
            mode="markers+text",
            marker=dict(size=12, color="red"),
            text=["🡇"],
            textposition="top center",
        )

    fig.update_layout(
        title={
            "text": f"Начало записи: {dt.day} {months[dt.month]} {dt.year} {dt.strftime('%H:%M:%S')}",
        },
        xaxis=dict(range=axis_ranges["x"]),
        yaxis=dict(range=axis_ranges[y_axis]),
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
